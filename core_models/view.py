import peewee as pw
from flare import BaseModel, Registry
import json

class JSONField(pw.TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)

class FlrView(BaseModel):
    name = pw.CharField()
    definition = JSONField()
    view_type = pw.CharField(choices=[("list","List"),("form","Form")],default="list")
    menu_id = pw.ForeignKeyField(Registry["FlrMenu"], null=True, backref="views")
    model = pw.CharField()
    sequence = pw.IntegerField(default=1)

FlrView.r()