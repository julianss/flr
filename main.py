from dotenv import load_dotenv
import sys
import os
if os.environ.get("flr_app"):
    load_dotenv("." + os.environ.get("flr_app"))
elif len(sys.argv) > 1:
    load_dotenv("." + sys.argv[1])
else:
    load_dotenv()
from flr import app
from registry import db

import core_models
__import__("apps." + os.environ["flr_app"])

db.init(os.environ["flr_db_name"],
    user=os.environ["flr_db_user"],
    password=os.environ["flr_db_pass"],
    host=os.environ["flr_db_host"],
    port=os.environ["flr_db_port"])
port = os.environ.get("flr_port", 6800)
host = os.environ.get("flr_host", "0.0.0.0")
flask_debug = True if os.environ.get("flr_flask_debug",'') == 'True' else False
if __name__ == "__main__":
    app.run(port=port, host=host, debug=flask_debug)
    if os.path.exists("scheduler.pid"):
        print("Killing scheduler")
        with open("scheduler.pid") as f:
            os.system("kill %s"%f.read())
