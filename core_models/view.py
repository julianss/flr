import peewee as pw
from flare import BaseModel, Registry

class FlrView(BaseModel):
    name = pw.CharField()
    definition = pw.JSONField()
    view_type = pw.CharField(choices=[("list","List"),("form","Form"),("search","Search")],default="list")
    menu_id = pw.ForeignKeyField(Registry["FlrMenu"], null=True, backref="views")
    model = pw.CharField()
    sequence = pw.IntegerField(default=1)
    wizard = pw.BooleanField(default=False)

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