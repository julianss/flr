import peewee as pw
from flare import BaseModel

class FlrMeta(BaseModel):
    meta_id = pw.CharField(unique=True)
    model = pw.CharField()
    rec_id = pw.IntegerField()

FlrMeta.r()