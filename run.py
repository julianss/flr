from dotenv import load_dotenv
load_dotenv()

from registry import Registry, db
from flare import app
import os
import core_models
__import__("apps." + os.environ["app"])

db.init(os.environ["db_name"],
    user=os.environ["db_user"],
    password=os.environ["db_pass"],
    host=os.environ["db_host"],
    port=os.environ["db_port"])
db_interactive_evolve = True if os.environ.get("db_interactive_evolve",'') == 'True' else False
db.evolve(interactive=db_interactive_evolve)
port = os.environ.get("port", 6800)
host = os.environ.get("host", "0.0.0.0")
flask_debug = True if os.environ.get("flask_debug",'') == 'True' else False
print(Registry)
app.run(port=port, host=host, debug=flask_debug)