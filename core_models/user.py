import peewee as pw
from flask import request, has_request_context
from flare import BaseModel, Registry, normalize_filters, combine_filters
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha512
import jwt
import os

SECRET = os.environ.get("jwt_secret")

def encrypt_password(fields):
    if 'password' in fields:
        if not fields["password"].startswith("$pbkdf2-sha512$"):
            crypt_password = CryptContext(schemes=["pbkdf2_sha512"]).encrypt(fields["password"])
            fields["password"] = crypt_password


class FlrUser(BaseModel):
    name = pw.CharField(help_text="Nombre")
    active = pw.BooleanField(help_text="Activo", default=True)
    login = pw.CharField(help_text="Login", unique=True, null=True)
    email = pw.CharField(help_text="Email", unique=True, null=True)
    password = pw.CharField(help_text="Password")
    role = pw.CharField(help_text="Perfil", null=True)

    @staticmethod
    def auth(login, password):
        crypt_password = CryptContext(schemes=["pbkdf2_sha512"]).encrypt(password)
        auth_field_name = os.environ.get("auth_field", "login")
        if auth_field_name == "login":
            auth_field = FlrUser.login
        elif auth_field_name == "email":
            auth_field = FlrUser.email
        user = FlrUser.select().where(auth_field==login, FlrUser.active==True)
        if not user:
            return False
        user = user.first()
        if not pbkdf2_sha512.verify(password, user.password):
            return False
        else:
            jwt_payload = {
                'id': user.id,
                'name': user.name,
                'role': user.role,
                auth_field_name: getattr(user, auth_field_name)
            }
            encoded_jwt = jwt.encode(jwt_payload, SECRET, algorithm='HS256')
            return encoded_jwt.decode('ascii')

    @classmethod
    def create(cls, **fields):
        encrypt_password(fields)
        return super(FlrUser, cls).create(**fields)

    @classmethod
    def flr_update(cls, fields, filters):
        encrypt_password(fields)
        return super(FlrUser, cls).flr_update(fields, filters)

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

    def get_permissions(self, model=False):
        data = {}
        if not model:
            models = [model for model in Registry]
        else:
            models = [model]
        for model in models:
            data.setdefault(model, {
                'perm_read': request.uid == 1,
                'perm_update': request.uid == 1,
                'perm_create': request.uid == 1,
                'perm_delete': request.uid == 1,
            })
        for group in self.groups:
            for rule in group.acls:
                if rule.model in models:
                    model_rule = data[rule.model]
                    model_rule["perm_read"] = model_rule["perm_read"] or rule.perm_read
                    model_rule["perm_update"] = model_rule["perm_update"] or rule.perm_update
                    model_rule["perm_create"] = model_rule["perm_create"] or rule.perm_create
                    model_rule["perm_delete"] = model_rule["perm_delete"] or rule.perm_delete
        return data

    @classmethod
    def check_access(cls, model, operation):
        if has_request_context():
            user = cls.get_by_id(request.uid)
            permissions = user.get_permissions(model)
            if not permissions[model]["perm_" + operation]:
                raise Exception("Access denied for operation %s on model %s by ACL"%(operation, model))
        else:
            return True

    @classmethod
    def check_rules(cls, model, operation, args, kwargs):
        if has_request_context():
            user = Registry["FlrUser"].get_by_id(request.uid)
            user_groups = [g.id for g in user.groups]
            FlrRule = Registry["FlrRule"]
            rules = FlrRule.select().where(
                FlrRule.group_id.in_(user_groups),
                FlrRule.model == model
            )
            total_result = {'ok': True, 'force_filter': []}
            for rule in rules:
                validator = getattr(Registry[model], rule.method)
                result = validator(operation, args, kwargs)
                if not result["ok"]:
                    msg = "Access denied for operation %s on model %s by Security Rule"%(operation, model)
                    if result.get("msg", ""):
                        msg += "\n" + result["msg"]
                    raise Exception(msg)
                if result.get('force_filter', []):
                    total_result["force_filter"].append(normalize_filters(result["force_filter"]))
            if total_result["force_filter"]:
                total_result["force_filter"] = combine_filters("|", total_result["force_filter"])
            return total_result
        else:
            return {'ok': True}


class FlrGroup(BaseModel):
    name = pw.CharField(help_text="Nombre")

FlrUser._meta.add_field("groups", pw.ManyToManyField(FlrGroup))

FlrUser.r()
FlrGroup.r()

class FlrPreferences(BaseModel):
    _transient = True

    user = pw.ForeignKeyField(FlrUser, help_text="Usuario")
    old_password = pw.CharField(help_text="Password anterior")
    new_password = pw.CharField(help_text="Password nuevo")
    confirm_new_password = pw.CharField(help_text="Password confirmación")

    @classmethod
    def get_default(cls):
        user = FlrUser.get_by_id(request.uid)
        return {
            'user': user.get_dict_id_and_name(),
        }

    @classmethod
    def flr_create(cls, **fields):
        user = FlrUser.get_by_id(request.uid)
        if not pbkdf2_sha512.verify(fields.get("old_password"), user.password):
            raise Exception("El password anterior no coincide")
        elif not fields.get('new_password') == fields.get('confirm_new_password'):
            raise Exception("El password nuevo y el password de confirmación no son identicos")
        FlrUser.flr_update({'password': fields.get('new_password')},
            [('id','=',user.id)])
        return super(FlrPreferences, cls).flr_create(**fields)

FlrPreferences.r()

class FlrACL(BaseModel):
    name = pw.CharField(verbose_name="Name")
    group_id = pw.ForeignKeyField(FlrGroup, help_text="Group", backref="acls")
    model = pw.CharField(help_text="Model")
    perm_read = pw.BooleanField(help_text="Read permission", null=True, default=False)
    perm_update = pw.BooleanField(help_text="Update permission", null=True, default=False)
    perm_create = pw.BooleanField(help_text="Create permission", null=True, default=False)
    perm_delete = pw.BooleanField(help_text="Delete permission", null=True, default=False)

FlrACL.r()

class FlrRule(BaseModel):
    group_id = pw.ForeignKeyField(FlrGroup, verbose_name="Group", backref="rules")
    name = pw.CharField(verbose_name="Rule name")
    model = pw.CharField(verbose_name="Model")
    method = pw.CharField(verbose_name="Model method", help_text="Method in model that performs the access validation")

FlrRule.r()