from flare import Registry
import peewee as pw

class FileField(pw.ForeignKeyField):
    def __init__(self, *args, **kwargs):
        super(FileField, self).__init__(Registry["FlrFile"], on_delete="SET NULL", *args, **kwargs)

pw.FileField = FileField