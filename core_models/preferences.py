import peewee as pw
from flask import request, has_request_context
from flare import BaseModel, Registry as r, normalize_filters, combine_filters
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha512
import jwt
import os


class FlrPreferences(BaseModel):
    _transient = True

    user = pw.ForeignKeyField(r["FlrUser"], help_text="Usuario")
    old_password = pw.CharField(help_text="Password anterior", null=True)
    new_password = pw.CharField(help_text="Password nuevo", null=True)
    confirm_new_password = pw.CharField(help_text="Password confirmación", null=True)
    old_company = pw.ForeignKeyField(r["FlrCompany"], help_text="Current company", null=True)
    new_company = pw.ForeignKeyField(r["FlrCompany"], help_text="Change to", null=True)

    @classmethod
    def get_default(cls):
        user = r["FlrUser"].get_by_id(request.uid)
        return {
            'user': user.get_dict_id_and_name(),
            'old_company': user.company_id.get_dict_id_and_name()
        }

    @classmethod
    def flr_create(cls, **fields):
        user = r["FlrUser"].get_by_id(request.uid)
        if fields.get("old_password"):
            if not pbkdf2_sha512.verify(fields.get("old_password"), user.password):
                raise Exception("El password anterior no coincide")
            if fields.get('new_password') or fields.get('confirm_new_password'):
                if not fields.get('new_password') == fields.get('confirm_new_password'):
                    raise Exception("El password nuevo y el password de confirmación no son iguales")
                r["FlrUser"].flr_update({'password': fields.get('new_password')},
                    [('id','=',user.id)])
            else:
                raise Exception("Debe registrar el Password nuevo y su confirmación")
        else:
            if fields.get('new_password') or fields.get('confirm_new_password'):
                raise Exception("Para cambiar la contraseña debe ingresar la contraseña anterior")
        if fields.get('new_company'):
            r["FlrUser"].flr_update({'company_id': fields['new_company']},
                [('id','=',user.id)])
        return super(FlrPreferences, cls).flr_create(**fields)

FlrPreferences.r()

