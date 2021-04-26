import peewee as pw
from flask import request, has_request_context
from flare import BaseModel, Registry as r, normalize_filters, combine_filters, _, n_, FlrException
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha512
import jwt
import os


class FlrPreferences(BaseModel):
    _transient = True

    user = pw.ForeignKeyField(r["FlrUser"], verbose_name=n_("User"))
    old_password = pw.CharField(verbose_name=n_("Current password"), null=True)
    new_password = pw.CharField(verbose_name=n_("New password"), null=True)
    confirm_new_password = pw.CharField(verbose_name=n_("Confirm new password"), null=True)
    old_company = pw.ForeignKeyField(r["FlrCompany"], verbose_name=n_("Current company"), null=True)
    new_company = pw.ForeignKeyField(r["FlrCompany"], verbose_name=n_("Change to"), null=True)

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
                raise FlrException(_("Entered password is incorrect"))
            if fields.get('new_password') or fields.get('confirm_new_password'):
                if not fields.get('new_password') == fields.get('confirm_new_password'):
                    raise FlrException(_("Password confirmation doesn't match "))
                r["FlrUser"].flr_update({'password': fields.get('new_password')},
                    [('id','=',user.id)])
            else:
                raise FlrException(_("New password is empty"))
        else:
            if fields.get('new_password') or fields.get('confirm_new_password'):
                raise FlrException(_("To set a new password please enter current password"))
        if fields.get('new_company'):
            r["FlrUser"].flr_update({'company_id': fields['new_company']},
                [('id','=',user.id)])
        return super(FlrPreferences, cls).flr_create(**fields)

FlrPreferences.r()

