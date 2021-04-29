import peewee as pw
from flask import request, has_request_context
from flr import m, u, BaseModel, Registry, normalize_filters, combine_filters, sendmail, _, n_, i18n
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha512
import jwt
import os
from iso639 import languages

LANG_CHOICES = [(l,languages.get(part1=l).name) for l in ["en"] + i18n.languages]

SECRET = os.environ.get("flr_jwt_secret")

def encrypt_password(fields):
    if 'password' in fields:
        if not fields["password"].startswith("$pbkdf2-sha512$"):
            crypt_password = CryptContext(schemes=["pbkdf2_sha512"]).encrypt(fields["password"])
            fields["password"] = crypt_password


class FlrUser(BaseModel):
    name = pw.CharField(verbose_name=n_("Name"))
    active = pw.BooleanField(verbose_name=n_("Active"), null=True, default=True)
    login = pw.CharField(verbose_name=n_("Login"), unique=True, null=True)
    email = pw.CharField(verbose_name=n_("Email"), unique=True, null=True)
    password = pw.CharField(verbose_name=n_("Password"))
    role = pw.CharField(verbose_name=n_("Role"), null=True)
    email_notifications = pw.BooleanField(verbose_name=n_("Email notifications"), null=True, default=True)
    lang = pw.CharField(verbose_name=n_("Language"), null=True, choices=LANG_CHOICES)

    @staticmethod
    def auth(login, password):
        crypt_password = CryptContext(schemes=["pbkdf2_sha512"]).encrypt(password)
        auth_field_name = os.environ.get("flr_auth_field", "login")
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

    @classmethod
    def get_permissions(cls, model=False):
        superuser_id = m("flruser_admin").id
        data = {}
        if not model:
            models = [model for model in Registry]
        else:
            models = [model]
        for model in models:
            data.setdefault(model, {
                'perm_read': request.uid == superuser_id,
                'perm_update': request.uid == superuser_id,
                'perm_create': request.uid == superuser_id,
                'perm_delete': request.uid == superuser_id,
            })
        ACL = Registry["FlrACL"]
        global_acls = ACL.select().where(ACL.group_id.is_null())
        all_acls = []
        for group in u().groups:
            for rule in group.acls:
                all_acls.append(rule)
        for rule in global_acls:
            all_acls.append(rule)
        for rule in all_acls:
            if rule.model in models:
                model_rule = data[rule.model]
                model_rule["perm_read"] = model_rule["perm_read"] or rule.perm_read
                model_rule["perm_update"] = model_rule["perm_update"] or rule.perm_update
                model_rule["perm_create"] = model_rule["perm_create"] or rule.perm_create
                model_rule["perm_delete"] = model_rule["perm_delete"] or rule.perm_delete
        return data

    @classmethod
    def check_access(cls, model, operation):
        if Registry[model]._transient:
            return True
        if has_request_context():
            permissions = FlrUser.get_permissions(model)
            if not permissions[model]["perm_" + operation]:
                raise Exception(_("Access denied for operation %s on model %s by ACL")%(operation, model))
        else:
            return True

    @classmethod
    def groups_check_any(cls, list_of_meta_ids):
        if isinstance(list_of_meta_ids, str):
            list_of_meta_ids = [list_of_meta_ids]
        """Check that user belongs to at least one of the groups, which are passed as a list of meta ids"""
        group_ids = []
        FlrMeta = Registry["FlrMeta"]
        for meta_id in list_of_meta_ids:
            for rec in FlrMeta.select().where(FlrMeta.meta_id==meta_id, FlrMeta.model=="FlrGroup"):
                group_ids.append(rec.rec_id)
        if has_request_context():
            user = cls.get_by_id(request.uid)
            user_group_ids = [g.id for g in user.groups]
            inter = set(user_group_ids).intersection(set(group_ids))
            if len(inter):
                return True
        return False

    @classmethod
    def get_user_name_and_company(cls):
        user = cls.get_by_id(request.uid)
        result = [user.name]
        if FlrUser.groups_check_any(["flrgroup_multicompany"]):
            if user.company_id:
                result.append(user.company_id.name)
        return ' - '.join(result)

    @classmethod
    def get_lang(cls):
        user = cls.get_by_id(request.uid)
        return user.lang


class FlrGroup(BaseModel):
    name = pw.CharField(verbose_name=n_("Name"))

FlrUser._meta.add_field("groups", pw.ManyToManyField(FlrGroup))

FlrUser.r()
FlrGroup.r()

class FlrACL(BaseModel):
    name = pw.CharField()
    group_id = pw.ForeignKeyField(FlrGroup, verbose_name=n_("Group"), backref="acls", null=True)
    model = pw.CharField()
    perm_read = pw.BooleanField(verbose_name=n_("Read permission"), null=True, default=False)
    perm_update = pw.BooleanField(verbose_name=n_("Update permission"), null=True, default=False)
    perm_create = pw.BooleanField(verbose_name=n_("Create permission"), null=True, default=False)
    perm_delete = pw.BooleanField(verbose_name=n_("Delete permission"), null=True, default=False)

FlrACL.r()

class FlrUserChangePassword(BaseModel):
    _transient = True
    user_id = pw.ForeignKeyField(FlrUser, verbose_name=n_("User"))
    password = pw.CharField(verbose_name=n_("New password"))

    @classmethod
    def get_default(cls):
        defaults = super(FlrUserChangePassword, cls).get_default()
        G = request and request.flr_globals or {}
        if G.get("user_id"):
            user = FlrUser.get_by_id(G["user_id"])
            defaults.update({
                "user_id": user.get_dict_id_and_name(),
            })
        return defaults

    @classmethod
    def flr_create(cls, **fields):
        res = super(FlrUserChangePassword, cls).flr_create(**fields)
        user = FlrUser.get_by_id(fields['user_id']['id'])
        password = fields['password']
        fields = {
            'password': password
            }
        filters = [['id','=',user.id]]
        FlrUser.flr_update(fields=fields, filters=filters)
        cls.new_password_update(user, password)
        return res

    @classmethod
    def new_password_update(cls, user, password):
        if user.email_notifications:
            if user.email:
                message = _("Your password has been reset, it is:\r\n"\
                "<strong>{}</strong>\r\n"\
                "We suggest you to change it the next time you login"\
                "").format(password)
                sendmail("", user.email, _('Reset password'), message)
FlrUserChangePassword.r()