from flr import Registry
import peewee as pw
import json

class JSONField(pw.TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)

class FileField(pw.ForeignKeyField):
    def __init__(self, *args, **kwargs):
        super(FileField, self).__init__(Registry["FlrFile"], on_delete="SET NULL", *args, **kwargs)

pw.FileField = FileField
pw.JSONField = JSONField