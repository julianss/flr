import peewee as pw
from flare import BaseModel, n_

class FlrMeta(BaseModel):
    meta_id = pw.CharField(verbose_name=n_("Name"), unique=True)
    model = pw.CharField(verbose_name=n_("Model"))
    rec_id = pw.IntegerField(verbose_name=n_("Rec id"))

FlrMeta.r()