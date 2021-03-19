from dotenv import load_dotenv
import sys
import os
if os.environ.get("app"):
    load_dotenv("." + os.environ.get("app"))
elif len(sys.argv) > 1:
    load_dotenv("." + sys.argv[1])
else:
    load_dotenv()

from registry import db
from flare import scheduler
import os
import core_models
__import__("apps." + os.environ["app"])
os.environ["app_path"] = os.path.abspath(os.path.join("apps", os.environ["app"]))

db.init(os.environ["db_name"],
    user=os.environ["db_user"],
    password=os.environ["db_pass"],
    host=os.environ["db_host"],
    port=os.environ["db_port"])

print("Starting scheduler")
scheduler.print_jobs()
scheduler.start()