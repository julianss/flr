from dotenv import load_dotenv
import sys
import os
os.environ["TZ"] = "UTC"
import time
time.tzset()
if os.environ.get("flr_app"):
    load_dotenv("." + os.environ.get("flr_app"))
elif len(sys.argv) > 1:
    load_dotenv("." + sys.argv[1])
else:
    load_dotenv()
from registry import Registry, db
from flr import scheduler, m
import json
import os
import core_models
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
__import__("apps." + os.environ["flr_app"])
os.environ["flr_app_path"] = os.path.abspath(os.path.join("apps", os.environ["flr_app"]))
print("App path", os.environ["flr_app_path"])

#Attempt to create database if it doesn't exist
conn = psycopg2.connect("user=%s password=%s host=%s port=%s dbname=postgres"%(
    os.environ["flr_db_user"],
    os.environ["flr_db_pass"],
    os.environ["flr_db_host"],
    os.environ["flr_db_port"]
))
try:
    cr = conn.cursor()
    cr.execute("SELECT 1 FROM pg_database where datname=%s", (os.environ["flr_db_name"],))
    if not cr.rowcount:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cr.execute(sql.SQL("CREATE database {} owner {};").format(
            sql.Identifier(os.environ["flr_db_name"]),
            sql.Identifier(os.environ["flr_db_pass"])
        ))
finally:
    conn.close()

db.init(os.environ["flr_db_name"],
    user=os.environ["flr_db_user"],
    password=os.environ["flr_db_pass"],
    host=os.environ["flr_db_host"],
    port=os.environ["flr_db_port"])
db_interactive_evolve = True if os.environ.get("flr_db_interactive_evolve",'') == 'True' else False
db.evolve(interactive=db_interactive_evolve)
Meta = Registry["FlrMeta"]
with db.atomic() as transaction:
#Load records from "data" directory
    try:
        all_meta_ids = set()
        for meta in Meta.select(Meta.meta_id):
            all_meta_ids.add(meta.meta_id)
        read_meta_ids = set()
        files_initial = []
        files_custom  = []
        initial_data = "data"
        custom_data = os.path.join("apps", os.environ["flr_app"], "data")
        for files, data_directory in ((files_initial,initial_data), (files_custom,custom_data)):
            if os.path.exists(data_directory):
                for fname in os.listdir(data_directory):
                    if fname.endswith(".json"):
                        fullpath = os.path.join(data_directory, fname)
                        files.append(fullpath)
        for fullpath in sorted(files_initial) + sorted(files_custom):
            print("Loading", fullpath)
            with open(fullpath) as f:
                records = json.load(f)
                for record in records:
                    if not record.get("meta_id"):
                        raise Exception("%s\nmeta:id missing"%record)
                    if not record.get("model"):
                        raise Exception("%s\nModel missing"%record)
                    if not record.get("data"):
                        raise Exception("%s\nData missing"%record)
                    model_name = record["model"]
                    Model = Registry[model_name]
                    meta_id = record["meta_id"]
                    read_meta_ids.add(meta_id)
                    existing = Meta.get_or_none(
                        Meta.model==model_name,
                        Meta.meta_id==meta_id
                    )
                    data = record["data"]
                    for field in data:
                        if field.endswith("_META_ID"):
                            if type(data[field]) == str:
                                meta_ids = [data[field]]
                                m2m = False
                            elif type(data[field]) == list:
                                meta_ids = data[field]
                                m2m = True
                            else:
                                raise Exception("%s expected string or list"%field)
                            res_ids = []
                            for meta_id_search in meta_ids:
                                ref = Meta.get_or_none(
                                    Meta.meta_id==meta_id_search
                                )
                                if ref is None:
                                    raise Exception("%s: meta_id does not exist"%meta_id_search)
                                res_ids.append(ref.rec_id)
                            if not m2m:
                                data[field] = res_ids[0]
                            else:
                                data[field] = res_ids
                    data = {
                        k.replace("_META_ID",""): data[k]
                        for k in data
                    }
                    if existing is None:
                        created_id = Model.flr_create(**data)
                        Meta.flr_create(
                            model=model_name,
                            rec_id=created_id,
                            meta_id=meta_id
                        )
                    elif not record.get("noupdate"):
                        Model.flr_update(data, [('id','=',existing.rec_id)])
        #Delete records that are in the meta table but are not present in the files (were deleted from the file)
        for meta_id in all_meta_ids:
            if meta_id not in read_meta_ids:
                print("deleting", meta_id)
                meta_rec = Meta.get_or_none(Meta.meta_id==meta_id)
                if meta_rec:
                    Registry[meta_rec.model].flr_delete([meta_rec.rec_id])
                    meta_rec.delete_instance()
    except:
        transaction.rollback()
        raise

#Set superuser password
superuser = m("flruser_admin")
Registry["FlrUser"].flr_update({
    'password': os.environ["flr_admin_pass"],
    'can_login_admin_panel':True
}, [('id','=',superuser.id)])