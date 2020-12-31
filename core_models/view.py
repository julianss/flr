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

    #Extended to delete restricted items from the views definitions ("groups" property)
    @classmethod
    def read(cls, fields, ids=[], filters=[], paginate=False, order=None, count=False):
        results = super(FlrView, cls).read(fields, ids=ids, filters=filters, paginate=paginate, order=order, count=count)
        FlrUser = Registry["FlrUser"]
        for result in results:
            new_definition = {}
            for key in result["definition"]:
                new_definition[key] = []
                item_list = result["definition"][key]
                if type(item_list) == list:
                    for item in item_list:
                        if "groups" in item:
                            ok = FlrUser.groups_check_any(item["groups"])
                            if ok:
                                new_definition[key].append(item)
                        else:
                            new_definition[key].append(item)
                else:
                    new_definition[key] = item_list
            result["definition"] = new_definition
        return results

FlrView.r()