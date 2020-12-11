import peewee as pw
from flare import BaseModel, Registry as r

class FlrCompany(BaseModel):
    name = pw.CharField(help_text="Nombre")
    image = pw.FileField(help_text="Imagen", null=True)


FlrCompany.r()

r["FlrUser"]._meta.add_field(
    "company_id", pw.ForeignKeyField(FlrCompany, verbose_name="Compañía")
)