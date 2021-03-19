from dotenv import load_dotenv
import sys
import os
if os.environ.get("app"):
    load_dotenv("." + os.environ.get("app"))
elif len(sys.argv) > 1:
    load_dotenv("." + sys.argv[1])
else:
    load_dotenv()
from flare import app
from registry import db

import core_models
__import__("apps." + os.environ["app"])

db.init(os.environ["db_name"],
    user=os.environ["db_user"],
    password=os.environ["db_pass"],
    host=os.environ["db_host"],
    port=os.environ["db_port"])
port = os.environ.get("port", 6800)
host = os.environ.get("host", "0.0.0.0")
flask_debug = True if os.environ.get("flask_debug",'') == 'True' else False
if __name__ == "__main__":
    app.run(port=port, host=host, debug=flask_debug)
    if os.path.exists("scheduler.pid"):
        print("Killing scheduler")
        with open("scheduler.pid") as f:
            os.system("kill %s"%f.read())
