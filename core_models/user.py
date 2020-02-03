import peewee as pw
from flare import BaseModel
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha512
import jwt
import os

SECRET = os.environ.get("jwt_secret")

class FlrUser(BaseModel):
    name = pw.CharField(help_text="Nombre")
    active = pw.BooleanField(help_text="Activo", default=True)
    login = pw.CharField(help_text="Login", unique=True)
    password = pw.CharField(help_text="Password")

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
    def decode_jwt(request):
        auth = request.headers.get("Authorization")
        if not auth:
            raise Exception("Needs Authorization")
        token = auth.split(" ")[1]
        try:
            decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
            request.uid = decoded.get("id")
        except:
            raise Exception("Invalid JWT")

FlrUser.r()

class FlrGroup(BaseModel):
    name = pw.CharField(help_text="Nombre")

FlrGroup.r()

class FlrUserFlrGroup(BaseModel):
    user_id = pw.ForeignKeyField(FlrUser, help_text="Usuario")
    group_id = pw.ForeignKeyField(FlrGroup, help_text="Grupo")

FlrUserFlrGroup.r()