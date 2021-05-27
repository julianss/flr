import os
import peewee as pw
from flr import BaseModel, Registry, n_, _, m
import json
import re

class FlrView(BaseModel):
    _order = "sequence"
    
    name = pw.CharField(verbose_name=n_("Name"))
    definition = pw.JSONField(verbose_name=n_("View Definition"))
    view_type = pw.CharField(verbose_name=n_("View type"), default="list",
        choices=[("list","List"),("form","Form"),("search","Search")])
    menu_id = pw.ForeignKeyField(Registry["FlrMenu"], verbose_name=n_("Views"), null=True, backref="views")
    model = pw.CharField(verbose_name=n_("Model"))
    sequence = pw.IntegerField(verbose_name=n_("Sequence"), default=1)
    wizard = pw.BooleanField(verbose_name=n_("Is wizard"), default=False)
    card_view_template = pw.CharField(verbose_name=n_("CardView EJS template file"), null=True)
    card_view_first = pw.BooleanField(verbose_name=n_("Show CardView first"), null=True)

    #Extended to
    # - delete restricted items from the views definitions ("groups" property)
    # - load the card view templates
    # - replace m(...) marks with the desired meta_id
    # - replace t(...) marks with the translations
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
            definition_as_text = json.dumps(result["definition"])
            requested_meta_ids = re.findall("m\((.*?)\)", definition_as_text)
            for meta_id in requested_meta_ids:
                definition_as_text = definition_as_text.replace("\"m(%s)\""%meta_id, str(m(meta_id).id))
            requested_translations = list(set(re.findall("_\('(.*?)'\)", definition_as_text)))
            for string_to_translate in requested_translations:
                definition_as_text = definition_as_text.replace("_('%s')"%string_to_translate, _(string_to_translate))
            if requested_meta_ids or requested_translations:
                result["definition"] = json.loads(definition_as_text)
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