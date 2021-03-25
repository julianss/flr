import os
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
    card_view_template = pw.CharField(null=True)
    card_view_first = pw.BooleanField(null=True)

    #Extended to delete restricted items from the views definitions ("groups" property)
    #Also to load the card view templates
    @classmethod
    def read(cls, fields, ids=[], filters=[], paginate=False, order=None, count=False):
        results = super(FlrView, cls).read(fields, ids=ids, filters=filters, paginate=paginate, order=order, count=count)
        FlrUser = Registry["FlrUser"]
        permissions = FlrUser.get_permissions()
        for result in results:
            perm_edit = permissions.get(result["model"])["perm_update"]
            perm_create = permissions.get(result["model"])["perm_create"]
            if result.get("card_view_template"):
                path = os.path.join("apps", os.environ["flr_app"], "data", result["card_view_template"])
                with open(path) as f:
                    result["card_view_template"] = f.read()
            new_definition = {}
            for key in result["definition"]:
                new_definition[key] = []
                value = result["definition"][key]
                if type(value) == list:
                    for item in value:
                        if "groups" in item:
                            ok = FlrUser.groups_check_any(item["groups"])
                            if ok:
                                new_definition[key].append(item)
                        else:
                            new_definition[key].append(item)
                elif key == "create":
                    if perm_create:
                        new_definition[key] = value
                    else:
                        del new_definition[key]
                elif key == "edit":
                    if perm_edit:
                        new_definition[key] = value
                    else:
                        del new_definition[key]
                else:
                    new_definition[key] = value
            if not "create" in new_definition:
                new_definition["create"] = perm_create
            if not "edit" in new_definition:
                new_definition["edit"] = perm_edit
            result["definition"] = new_definition
        return results

FlrView.r()