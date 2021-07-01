import peewee as pw
from flr import BaseModel

class Person(BaseModel):
    name = pw.CharField()
    age = pw.IntegerField()
    favorite_color = pw.CharField(choices=[('G','Green'),('B','Blue'),('R','Red')], null=True)

Person.r()