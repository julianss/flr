import peewee as pw
from flare import BaseModel, Registry, n_, _
from flask import request

class FlrMenuSection(BaseModel):
    name = pw.CharField(verbose_name=n_("Name"))
    sequence = pw.IntegerField(verbose_name=n_("Sequence"), default=1)

FlrMenuSection.r()

class FlrMenu(BaseModel):
    name = pw.CharField()
    section_id = pw.ForeignKeyField(FlrMenuSection, verbose_name=n_("Section"), backref="menus")
    groups = pw.ManyToManyField(Registry["FlrGroup"])
    sequence = pw.IntegerField(verbose_name=n_("Sequence"), default=1)

    @classmethod
    def get_menus(cls):
        user = Registry["FlrUser"].get_by_id(request.uid)
        user_groups = set([x.id for x in user.groups])
        result = []
        for section in FlrMenuSection.select().order_by(FlrMenuSection.sequence):
            section_obj = {
                'id': section.id,
                'name': _(section.name),
                'menus': []
            }
            for menu in section.menus.order_by(FlrMenu.sequence):
                menu_groups = [g.id for g in menu.groups]
                if not menu.groups or user_groups.intersection(menu_groups):
                    section_obj["menus"].append({
                        "id": menu.id,
                        "name": _(menu.name)
                    })
            if section_obj["menus"]:
                result.append(section_obj)
        return result

FlrMenu.r()