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

from registry import db
from flr import scheduler
import os
import core_models
__import__("apps." + os.environ["flr_app"])
os.environ["flr_app_path"] = os.path.abspath(os.path.join("apps", os.environ["flr_app"]))

db.init(os.environ["flr_db_name"],
    user=os.environ["flr_db_user"],
    password=os.environ["flr_db_pass"],
    host=os.environ["flr_db_host"],
    port=os.environ["flr_db_port"])

print("Starting scheduler")
scheduler.print_jobs()
scheduler.start()