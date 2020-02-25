import peewee as pw
from flask import request
from flare import BaseModel, Registry
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha512
import jwt
import os

SECRET = os.environ.get("jwt_secret")

class FlrGroup(BaseModel):
    name = pw.CharField(help_text="Nombre")

FlrGroup.r()

class FlrUser(BaseModel):
    name = pw.CharField(help_text="Nombre")
    active = pw.BooleanField(help_text="Activo", default=True)
    login = pw.CharField(help_text="Login", unique=True)
    password = pw.CharField(help_text="Password")
    groups = pw.ManyToManyField(FlrGroup)

    @staticmethod
    def auth(login, password):
        crypt_password = CryptContext(schemes=["pbkdf2_sha512"]).encrypt(password)
        user = FlrUser.select(FlrUser.id, FlrUser.password, FlrUser.name).where(FlrUser.login==login, FlrUser.active==True)
        if not user:
            return False
        user = user.first()
        if not pbkdf2_sha512.verify(password, user.password):
            return False
        else:
            jwt_payload = {'id': user.id, 'name': user.name}
            encoded_jwt = jwt.encode(jwt_payload, SECRET, algorithm='HS256')
            return encoded_jwt.decode('ascii')

    @classmethod
    def create(cls, **fields):
        if 'password' in fields:
            if not fields["password"].startswith("$pbkdf2-sha512$"):
                crypt_password = CryptContext(schemes=["pbkdf2_sha512"]).encrypt(fields["password"])
                fields["password"] = crypt_password
        return super(FlrUser, cls).create(**fields)

    @staticmethod
    def decode_jwt(request, token=False):
        auth = request.headers.get("Authorization")
        if not auth:
            if not token:
                raise Exception("Needs Authorization")
        if auth:
            token = auth.split(" ")[1]
        try:
            decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
            request.uid = decoded.get("id")
        except:
            raise Exception("Invalid JWT")

    def get_permissions(self):
        data = {}
        for model in Registry:
            data.setdefault(model, {
                'perm_read': request.uid == 1,
                'perm_update': request.uid == 1,
                'perm_create': request.uid == 1,
                'perm_delete': request.uid == 1,
            })
        for group in self.groups:
            for rule in group.acls:
                model_rule = data[rule.model]
                model_rule["perm_read"] = model_rule["perm_read"] or rule.perm_read 
                model_rule["perm_update"] = model_rule["perm_update"] or rule.perm_update
                model_rule["perm_create"] = model_rule["perm_create"] or rule.perm_create
                model_rule["perm_delete"] = model_rule["perm_delete"] or rule.perm_delete
        return data

FlrUser.r()

FlrUserFlrGroup = FlrUser.groups.get_through_model()

class FlrACL(BaseModel):
    group_id = pw.ForeignKeyField(FlrGroup, help_text="Group", backref="acls")
    model = pw.CharField(help_text="Model")
    perm_read = pw.BooleanField(help_text="Read permission", null=True, default=False)
    perm_update = pw.BooleanField(help_text="Update permission", null=True, default=False)
    perm_create = pw.BooleanField(help_text="Create permission", null=True, default=False)
    perm_delete = pw.BooleanField(help_text="Delete permission", null=True, default=False)

FlrACL.r()