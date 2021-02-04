import peewee as pw
from flare import BaseModel, r, m, u

class FlrCompany(BaseModel):
    name = pw.CharField(help_text="Nombre")
    image = pw.FileField(help_text="Imagen", null=True)
    
    _rbac = {
        'read': {
            '*': 'get_allowed_companies_filter'
        }
    }

    # Only permit reading user's own company and companies present in the user's allowed_companies
    # unless it is the superuser, who can see all companies regardless
    @classmethod
    def get_allowed_companies_filter(cls):
        user = u()
        if user.id == m("flruser_admin").id:
            return False
        else:
            allowed_companies = [user.company_id.id]
            allowed_companies.extend([c.id for c in user.allowed_companies])
            return [('id', 'in', allowed_companies)]

FlrCompany.r()

r["FlrUser"]._meta.add_field(
    "company_id", pw.ForeignKeyField(FlrCompany, verbose_name="Compañía")
)

r["FlrUser"]._meta.add_field(
    "allowed_companies",  pw.ManyToManyField(FlrCompany)
)