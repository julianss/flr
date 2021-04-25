from flask import Flask, request, has_request_context, jsonify, send_from_directory, redirect, make_response, Response
from registry import Registry, ReportHelpers, db
from utils import normalize_filters, combine_filters, CustomJSONEncoder, add_pages, sendmail, I18n
from apscheduler.schedulers.blocking import BlockingScheduler
import peeweedbevolve
import peewee as pw
from playhouse.shortcuts import model_to_dict
import traceback
import operator as __operator__
import os
import xlsxwriter
import openpyxl
import base64
from functools import wraps
from datetime import datetime
import jwt
import tempfile
import json

SECRET = os.environ.get("flr_jwt_secret")

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

scheduler = BlockingScheduler()

def cron(year=None, month=None, day=None, day_of_week=None, hour=None, minute=None, second=None):
    def inner(func):
        scheduler.add_job(func, 'cron', year=year, month=month, day=day, day_of_week=day_of_week, hour=hour, minute=minute, second=second)
        return func
    return inner

if os.environ.get("flr_enable_cors") == "True":
    from flask_cors import CORS
    CORS(app)

if os.environ.get("flr_legacy_table_names") == "False":
    ltn = False
else:
    ltn = True

def get_current_user():
    if has_request_context:
        return Registry["FlrUser"].get_by_id(request.uid)
    else:
        return None

def get_obj_from_meta(meta_id):
    FlrMeta = Registry["FlrMeta"]
    meta = FlrMeta.get(FlrMeta.meta_id == meta_id)
    return Registry[meta.model].get_by_id(meta.rec_id)

u = get_current_user
m = get_obj_from_meta
r = Registry

#Setup translations to translate always to the user's preferred language
#Fallback to application default language if user preferred language can't be determined
i18n = I18n()
def _(message):
    if has_request_context and hasattr(request, "uid"):
        lang = u().lang
    else:
        lang = os.environ.get("flr_default_lang", "en")
    return i18n.translate(message, lang)
#Also define a noop gettext so some strings (e.g. field names) can be marked as translatable
#but be translated until needed
def n_(message):
    return message

#Functions to get the 'human readable' version of field names
def prettifyName(field_name):
    return field_name.capitalize().replace("_", " ")
#Note the call to _ to translate the fields name (marked with n_ upon definition)
def get_field_verbose_name(k, obj):
    verbose = False
    htext = False
    doc = False
    pretty = prettifyName(k)
    if obj is not None:
        if hasattr(obj, "verbose_name"):
            verbose = obj.verbose_name
        if hasattr(obj, "help_text"):
            htext = obj.help_text
        if hasattr(obj, "__doc__"):
            doc = obj.__doc__
    return _(verbose or htext or doc or pretty)

class FlrException(Exception):
    pass

class BaseModel(pw.Model):
    _transient = False
    _rbac = {}
    _default_related_read = []

    class Meta:
        database = db
        legacy_table_names = ltn

    @classmethod
    def r(cls):
        if cls.__name__ in Registry:
            raise Exception(cls.__name__ + " already exists in the model registry")
        Registry[cls.__name__] = cls
        cls._meta.add_field("created_by", pw.ForeignKeyField(Registry["FlrUser"], null=True,
            verbose_name=n_("Created by")))
        cls._meta.add_field("created_on", pw.DateTimeField(null=True,
            verbose_name=n_("Created on")))
        cls._meta.add_field("updated_by", pw.ForeignKeyField(Registry["FlrUser"], null=True,
            verbose_name=n_("Last updated by")))
        cls._meta.add_field("updated_on", pw.DateTimeField(null=True,
            verbose_name=n_("Last updated on")))

    @classmethod
    def get_default(cls):
        defaults = {}
        for k in cls._meta.fields.keys():
            field = cls._meta.fields[k]
            if getattr(field, 'default'):
                defaults[k] = field.default
            else:
                if type(field) in (pw.IntegerField, pw.FloatField):
                    defaults[k] = 0
        return defaults

    def get_dict_id_and_name(self):
        return {
            'id': self.id,
            'name': self.name if hasattr(self, "name") else "%s,%s"%(self.__class__.__name__, self.id)
        }

    @classmethod
    def dict_get_id(cls, value):
        if type(value) == int:
            return value
        elif type(value) == dict:
            return value.get("id")
        else:
            return None

    @classmethod
    def get_fields(cls, with_verbose_name=False):
        fields = []
        def get_what_to_append(k, f):
            if not with_verbose_name:
                return k
            else:
                return {
                    'verbose_name': get_field_verbose_name(k, f),
                    'name': k
                }
        for k in cls._meta.fields.keys():
            fields.append(get_what_to_append(k, cls._meta.fields.get(k)))
        for k in cls._meta.manytomany.keys():
            fields.append(get_what_to_append(k, cls._meta.manytomany.get(k)))
        for k in dir(cls):
            tattr = type(getattr(cls, k))
            if tattr == property:
                if k not in ("dirty_fields", "_pk"):
                    fields.append(get_what_to_append(k, getattr(cls, k)))
            if tattr == pw.BackrefAccessor:
                if issubclass(getattr(cls, k).rel_model, BaseModel):
                    if not getattr(cls, k).rel_model._transient:
                        fields.append(get_what_to_append(k, None))
        return fields

    @classmethod
    def get_fields_desc(cls, which=[]):
        related_fields = []
        for field in which:
            if "." in field:
                related_fields.append(field)
        fields = {}
        if not "id" in which:
            which.insert(0, "id")
        for k in cls._meta.fields.keys():
            if k not in which:
                continue
            field = cls._meta.fields[k]
            desc = {
                'label': get_field_verbose_name(k, getattr(cls, k)),
                'type': field.__class__.__name__.replace("Field", "").lower(),
                'required': not field.null
            }
            if desc["type"] == "foreignkey":
                desc["model"] = field.rel_model.__name__
            if field.choices:
                desc.update({
                    'type': 'select',
                    'options': field.choices
                })
            fields[k] = desc
        for k in cls._meta.manytomany.keys():
            if k not in which:
                continue
            field = cls._meta.manytomany[k]
            fields[k] = {
                'label': get_field_verbose_name(k, getattr(cls, k)),
                'type': 'manytomany',
                'model': field.rel_model.__name__,
                'related_fields': []
            }
            rfs = []
            for rf in related_fields:
                parent, child = rf.split(".")
                if parent == k:
                    rfs.append(child)
            if rfs:
                fields[k]["related_fields"] = field.rel_model.get_fields_desc(rfs)
        for k in dir(cls):
            if k not in which:
                continue
            tattr = type(getattr(cls, k))
            if tattr == property:
                fields[k] = {
                    'label': getattr(cls, k).__doc__,
                    'type': 'char'
                }
            if tattr == pw.BackrefAccessor:
                field = getattr(cls, k)
                fields[k] = {
                    'label': prettifyName(k),
                    'type': 'backref',
                    'model': field.rel_model.__name__,
                    'related_fields': []
                }
                rfs = []
                for rf in related_fields:
                    parent, child = rf.split(".")
                    if parent == k:
                        rfs.append(child)
                if rfs:
                    fields[k]["related_fields"] = field.rel_model.get_fields_desc(rfs)
        fields["id"].update({
            "label": "ID",
            "required": False,
            "readonly": True
        })
        return fields

    @classmethod
    def get_batch_actions(cls):
        actions = []
        perm = Registry["FlrUser"].get_permissions(cls.__name__)
        if perm[cls.__name__]["perm_delete"]:
            actions.append({
                'method': 'delete',
                'label': _('Delete'),
                'confirm': _('Confirm the deletion of the selected records?')
            })
        return actions

    @classmethod
    def get_rbac_read_filters(cls):
        if not has_request_context():
            return []
        if not cls._rbac.get("read"):
            return []
        user = u()
        user_groups = [g.id for g in user.groups]
        or_filters = []
        and_filters = []
        for group_meta_id in cls._rbac["read"]:
            spec = cls._rbac["read"][group_meta_id]
            if type(spec) == list:
                filters = spec
            elif type(spec) == str:
                filters = getattr(cls, spec)()
            else:
                filters = spec()
            if not filters:
                continue
            filters = normalize_filters(filters)
            if group_meta_id == "*":
                and_filters.append(filters)
            elif m(group_meta_id).id in user_groups:
                or_filters.append(filters)
        or_filters = combine_filters("|", or_filters)
        and_filters = combine_filters("&", and_filters)
        if and_filters and not or_filters:
            final = and_filters
        elif or_filters and not and_filters:
            final = or_filters
        elif and_filters and or_filters:
            all_filters = []
            all_filters.append(and_filters)
            all_filters.append(or_filters)
            final = combine_filters("&", all_filters)
        else:
            final = []
        return final

    @classmethod
    def check_rbac(cls, operation, ids):
        if not has_request_context():
            return True
        if not cls._rbac.get(operation):
            return True
        user = u()
        user_groups = [g.id for g in user.groups]
        ands = []
        ors = []
        for group_meta_id in cls._rbac[operation]:
            spec = cls._rbac[operation][group_meta_id]
            if type(spec) == str:
                result = getattr(cls, spec)(ids)
            else:
                result = spec(ids)
            if group_meta_id == "*":
                ands.append(result)
            elif m(group_meta_id).id in user_groups:
                ors.append(result)
        ands_ok = not ands or all(ands)
        ors_ok = not ors or any(ors)
        if not (ands_ok and ors_ok):
            raise Exception(_("Access denied for operation %s on the selected records")%operation)
        return True

    @classmethod
    def filter_query(cls, query, filters=[], paginate=False):
        operator_table = {
            '=':     __operator__.eq,
            '>':     __operator__.gt,
            '<':     __operator__.lt,
            '>=':    __operator__.ge,
            '<=':    __operator__.le,
            '!=':    __operator__.ne,
            'in':    lambda fld,lkp: fld.in_(lkp),
            'not in':lambda fld,lkp: fld.not_in(lkp),
            'like':  __operator__.mod,
            'ilike': __operator__.pow
        }
        op_and = __operator__.and_
        op_or = __operator__.or_
        op_not = __operator__.inv
        stack = []
        nary = []
        n_exprs = 0
        for node in filters:
            if node == '|':
                stack.append(op_or)
                nary.append(2)
            elif node == '&':
                stack.append(op_and)
                nary.append(2)
            elif node == '!':
                stack.append(op_not)
                nary.append(1)
            elif len(node) == 3:
                field_name, operator, value = node
                field = getattr(cls, field_name)
                op = operator_table[operator]
                if type(field) != pw.ManyToManyField:
                    if operator in ("like", "ilike"):
                        value = "%" + value + "%"
                    expr = op(field, value)
                else:
                    rel_model_field_id = field.rel_model.__name__.lower() + "_id"
                    m2m_filter = cls.select().join(field._through_model).where(getattr(field._through_model, rel_model_field_id).in_(value))
                    expr = op(getattr(cls, "id"), [rec.id for rec in m2m_filter])
                stack.append(expr)
                n_exprs += 1

            while nary:
                if n_exprs == nary[-1]:
                    c = []
                    for i in range(0, nary[-1]):
                        c.insert(0, stack.pop())
                    logic_op = stack.pop()
                    new_expr = logic_op(*c)
                    stack.append(new_expr)
                    n_exprs = 1
                    nary.pop()
                else:
                    break
        if stack:
            query = query.where(*stack)
        if paginate:
            query = query.paginate(paginate[0], paginate[1])
        return query

    @classmethod
    def create(cls, **fields):
        fields["created_on"] = datetime.now()
        if request and hasattr(request, "uid"):
            fields["created_by"] = request.uid
            if hasattr(cls, "company_id"):
                if not fields.get("company_id"):
                    fields["company_id"] = Registry["FlrUser"].get_by_id(request.uid).company_id.id
        return super(BaseModel, cls).create(**fields)

    @classmethod
    def flr_create(cls, **fields):
        r["FlrUser"].check_access(cls.__name__, "create")
        #Attachments may be present (files that have already been created)
        #Attach them to the created model at the end
        attachments = []
        if 'attachments' in fields:
            attachments = fields["attachments"]
            del fields["attachments"]
        #Take out @properties, only regular fields can be created
        fields = {k:fields[k] for k in fields if type(getattr(cls, k)) != property}
        m2m = []
        filefields = []
        #Identify many2many and file fields, create record without them, will be added later
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                if type(pw_field) == pw.ManyToManyField:
                    m2m.append(field_name)
                elif type(pw_field) == pw.FileField:
                    filefields.append(field_name)
        fields_no_m2m = {k:fields[k] for k in fields if k not in m2m and k not in filefields}
        #ForeignKey fields can be sent in object format, if so extract id
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                if type(pw_field) == pw.ForeignKeyField:
                    if type(fields_no_m2m[field_name]) == dict:
                        fields_no_m2m[field_name] = fields_no_m2m[field_name]["id"]
        created = cls.create(**fields_no_m2m)
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                #Create files from the base64 data
                if type(pw_field) == pw.FileField:
                    value = fields.get(field_name)
                    if value is not None:
                        data = value.get("datab64", "")
                        name = value.get("name", "untitled")
                        file_id = Registry["FlrFile"].create_from_data(data, name)
                        setattr(created, field_name, file_id)
                        created.save()
                #Create one2many related records
                elif type(pw_field) == pw.BackrefAccessor:
                    if fields.get(field_name) is not None:
                        for fields2 in fields.get(field_name,[]):
                            fields2[pw_field.field.name] = created.id
                            if "id" in fields2:
                                del fields2["id"]
                            pw_field.rel_model.flr_create(**fields2)
                #Associate many to many records
                elif type(pw_field) == pw.ManyToManyField:
                    if fields.get(field_name) is not None:
                        to_add = []
                        related_ids = [
                            (x["id"] if type(x)==dict else x)
                            for x in fields.get(field_name)
                        ] or []
                        for related_id in related_ids:
                            to_add.append(pw_field.rel_model.get_by_id(related_id))
                        if to_add:
                            getattr(created, field_name).add(to_add)
                            created.save()
        created_id = created.id
        cls.check_rbac("create", [created_id])
        if attachments:
            Registry["FlrFile"].flr_update({
                'model': cls.__name__,
                'rec_id': created_id
            }, [('id', 'in', attachments)])
        return created_id

    @classmethod
    def flr_update(cls, fields, filters):
        r["FlrUser"].check_access(cls.__name__, "update")
        #Determine which ids will be updated
        query = cls.select(cls.id)
        if filters:
            query = cls.filter_query(query, filters)
        ids = [x.id for x in query]
        cls.check_rbac("update", ids)
        #Take out @properties, only regular fields can be updated
        #Take out also non-existing fields that could have been sent by mistake or for example
        #the "virtual" name field that is generated when a model has no name field.
        fields = {k:fields[k] for k in fields
            if hasattr(cls, k) and type(getattr(cls, k)) not in (property,)}
        m2m = []
        o2m = []
        filefields = []
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                #Identify many2many, one2many and file fields, take them out they must be updated separately
                if type(pw_field) == pw.ManyToManyField:
                    m2m.append(field_name)
                elif type(pw_field) == pw.BackrefAccessor:
                    o2m.append(field_name)
                elif type(pw_field) == pw.FileField:
                    filefields.append(field_name)
        fields_no_m2m = {k:fields[k] for k in fields if k not in m2m and k not in o2m and k not in filefields}
        #ForeignKey fields can be sent in object format, if so extract id
        #Also, if the value is falsy, null the field
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                if type(pw_field) == pw.ForeignKeyField:
                    if type(fields_no_m2m[field_name]) == dict:
                        fields_no_m2m[field_name] = fields_no_m2m[field_name]["id"]
                    elif not fields_no_m2m[field_name]:
                        fields_no_m2m[field_name] = None
        modified = 0
        if fields_no_m2m:
            query = cls.update(**fields_no_m2m).where(cls.id.in_(ids))
            modified = query.execute()
        if m2m:
            query = cls.select(cls.id).where(cls.id.in_(ids))
            for record in query:
                for m2m_field in m2m:
                    getattr(record, m2m_field).clear()
                    getattr(record, m2m_field).add([
                        x["id"] if type(x) == dict else x
                        for x in fields[m2m_field]])
        if o2m:
            #for the moment o2m updating will be supported only for a single record
            assert len(ids) == 1, "one2many fields can only be updated for a single record"
            updated_id = ids[0]
            for field_name in o2m:
                pw_field = getattr(cls, field_name)
                #If there are missing records, we must delete them, so take note of the records
                #currently stored in the database and compare them to the incoming ones
                original_ids = set([x.id for x in getattr(cls.get_by_id(updated_id), field_name)])
                new_ids = set([x["id"] for x in fields[field_name] if "id" in x])
                to_delete = original_ids - new_ids
                if to_delete:
                    pw_field.rel_model.flr_delete(to_delete)
                #Now process the incoming values to create or edit the child records as needed
                for fields2 in fields[field_name]:
                    #It's new, create it
                    if not fields2.get("id") or str(fields2.get("id")).startswith("tmp"):
                        fields2[pw_field.field.name] = updated_id
                        if "id" in fields2:
                            del fields2["id"]
                        pw_field.rel_model.flr_create(**fields2)
                    #Already exists, update it
                    #TODO only update it if it's dirty
                    else:
                        rel_id = fields2["id"]
                        del fields2["id"]
                        pw_field.rel_model.flr_update(fields2, [("id","=",rel_id)])
        if filefields:
            FlrFile = Registry["FlrFile"]
            for filefield in filefields:
                value = fields.get(filefield)
                #Delete old file
                if value is None or value.get("datab64"):
                    query = cls.select(getattr(cls, filefield)).where(cls.id.in_(ids))
                    file_ids = []
                    for record in query:
                        file_id = getattr(record, filefield)
                        if file_id:
                            file_ids.append(file_id.id)
                    FlrFile.delete().where(FlrFile.id.in_(file_ids)).execute()
                #Create new file
                if value is not None:
                    for id in ids:
                        data = value.get("datab64", "")
                        name = value.get("name", "untitled")
                        file_id = FlrFile.create_from_data(data, name)
                        record = cls.get_by_id(id)
                        setattr(record, filefield, file_id)
                        record.save()
        return modified

    @classmethod
    def flr_delete(cls, ids):
        r["FlrUser"].check_access(cls.__name__, "delete")
        cls.check_rbac("delete", ids)
        for k in cls._meta.manytomany.keys():
            field = cls._meta.manytomany[k]
            for rec in cls.select().where(getattr(cls, "id").in_(ids)):
                getattr(rec, k).clear()
        query = cls.delete().where(cls.id.in_(ids))
        deleted = query.execute()
        return deleted

    @classmethod
    def read(cls, fields, ids=[], filters=[], paginate=False, order=None, count=False, options={}):
        #Check ACL and rules
        FlrUser = Registry["FlrUser"]
        FlrUser.check_access(cls.__name__, "read")
        forced_filters = cls.get_rbac_read_filters()
        #If the shorthand 'ids' parameter was used append the ids to the filters
        if ids:
            filters.append(("id","in",ids))
        #If there are forced filters because of rbac rules combine them into the existing filters
        if forced_filters:
            if not filters:
                filters = forced_filters
            else:
                filters = normalize_filters(filters)
                filters = combine_filters('&', [filters, forced_filters])
        #If no order is specified and model has a default order defined, use it
        if order is None:
            if hasattr(cls, "_order"):
                order = cls._order
            else:
                order = "id"
        only = None
        extra_attrs = []
        related_fields_m2m = {}
        if not fields:
            fields = ["id"]
        if fields:
            if "id" not in fields:
                fields.append("id")
            only = []
            m2m = []
            for field_name in fields:
                #Take note of the related fields (dot notation), will be used to render the dicts
                #of many-to-many and one-to-many records
                if "." in field_name:
                    parent, child = field_name.split(".")
                    field = getattr(cls, parent)
                    if type(field) in (pw.ManyToManyField, pw.BackrefAccessor):
                        related_fields_m2m.setdefault(parent, []).append(child)
                else:
                    field = getattr(cls, field_name)
                    #if field name is a @property of the model, it must be added to the extra_attrs list
                    if type(field) == property:
                        extra_attrs.append(field_name)
                    #if field is many2many or one2many it must be handled separately
                    elif type(field) in (pw.ManyToManyField, pw.BackrefAccessor):
                        m2m.append(field_name)
                    else:
                        only.append(field)
        if only:
            query = cls.select(*only)
        else:
            query = cls.select()
        if order is not None:
            order = order.split(" ")
            order_attr = getattr(cls, order[0])
            if "desc" in order:
                order_attr = order_attr.desc()
            query = query.order_by(order_attr)
        #If model has active attribute read only those that are active
        if hasattr(cls, "active"):
            query = query.where(getattr(cls, 'active') == True)
        #Filter only records from current company
        if hasattr(cls, "company_id"):
            query = query.where(getattr(cls, 'company_id') == FlrUser.get_by_id(request.uid).company_id)
        if filters or paginate:
            query = cls.filter_query(query, filters, paginate)
        if count:
            return query.count()
        else:
            fk_2b_named = []
            results = []
            # Add foreign key fields so model_to_dict renders the name of the related record
            if only:
                for pw_field in only:
                    if type(pw_field) == pw.ForeignKeyField or type(pw_field) == pw.FileField:
                        only.append(getattr(pw_field.rel_model, "id"))
                        if hasattr(pw_field.rel_model, "name"):
                            name_attr = pw_field.rel_model.name
                            if type(name_attr) != property:
                                only.append(name_attr)
                            else:
                                #if the name of the related model is a property it will have to be computed later
                                fk_2b_named.append(pw_field.name)
                        # Add other name attr passed through options
                        other_name = options.get('name_field', {}).get(pw_field.name)
                        if other_name:
                            if hasattr(pw_field.rel_model, other_name):
                                other_name = getattr(pw_field.rel_model, other_name)
                                only.append(other_name)
            for model in query:
                data = model_to_dict(model, only=only, recurse=True, extra_attrs=extra_attrs)
                if fk_2b_named:
                    for fk_field_name in fk_2b_named:
                        data[fk_field_name]["name"] = getattr(model, fk_field_name).name
                # Add many-to-many and one-to-many fields. For this, the array of related records
                # will be added one by one, creating the dicts for the records using the list
                # of related fields (the ones that were specified using dot notation)
                if m2m:
                    for field_name in m2m:
                        related_records = getattr(model, field_name)
                        related_records_dicts = []
                        for relr in related_records:
                            rendered = relr.get_dict_id_and_name()
                            related_fields = related_fields_m2m.get(field_name, [])
                            if not related_fields and relr.__class__._default_related_read:
                                related_fields = relr.__class__._default_related_read
                            if related_fields and not "name" in related_fields:
                                del rendered["name"]
                            for related_field in related_fields:
                                if type(getattr(relr.__class__, related_field)) in (pw.ForeignKeyField, pw.FileField):
                                    rel = getattr(relr, related_field)
                                    rendered[related_field] = rel.get_dict_id_and_name()
                                else:
                                    rendered[related_field] = getattr(relr, related_field)
                            related_records_dicts.append(rendered)
                        data[field_name] = related_records_dicts
                results.append(data)
            return results

    @classmethod
    def export(cls, fields, filters=[], paginate=False, order=None):
        fields_desc = cls.get_fields_desc(fields)
        results = cls.read(fields, filters=filters, paginate=paginate, order=order)
        fd, fname = tempfile.mkstemp()
        os.close(fd)
        wb = xlsxwriter.Workbook(fname)
        ws = wb.add_worksheet()
        date_format = wb.add_format({'num_format': "yyyy-mm-dd"})
        datetime_format = wb.add_format({'num_format': "yyyy-mm-dd hh:mm AM/PM"})
        row = 0
        for col, field in enumerate(fields):
            f = getattr(cls, field)
            label = get_field_verbose_name(field, f)
            ws.write(row, col, label)
        row += 1
        for rec in results:
            for col, field in enumerate(fields):
                fmt = False
                val = rec[field]
                if fields_desc[field]["type"] in ("foreignkey","file"):
                    if val:
                        val = val.get("name", val["id"])
                    else:
                        val = ""
                elif fields_desc[field]["type"] == "select":
                    for value, label in fields_desc[field]["options"]:
                        if value == val:
                            val = label
                            break
                elif fields_desc[field]["type"] == "date":
                    fmt = date_format
                elif fields_desc[field]["type"] == "datetime":
                    fmt = datetime_format
                elif fields_desc[field]["type"] in ("backref","manytomany","json"):
                    val = json.dumps(val)
                if fmt:
                    ws.write(row, col, val, fmt)
                else:
                    ws.write(row, col, val)
            row += 1
        wb.close()
        payload = {
            'path': fname,
            'filename': cls.__name__ + ".xlsx",
            'mime_type': "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        encoded = jwt.encode(payload, SECRET, algorithm='HS256')
        return {
            'token': encoded.decode("ascii"),
        }

    @classmethod
    def import_from_file(cls, fields, file_path):
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        no_id = "id" not in fields
        fields_desc = cls.get_fields_desc(fields)
        if no_id:
            fields.remove("id")
        errors = []
        affected_ids = []
        num_columns = 0
        for i,row in enumerate(ws,1):
            if i == 1:
                for column in row:
                    if column.value:
                        num_columns += 1
                if num_columns != len(fields):
                    errors.append(_("Number of columns in file (%s) doesn't match the number of fields selected (%s)")%(num_columns,len(fields)))
                    break
                continue
            vals = {}
            for n in range(0, num_columns):
                field = fields[n]
                column = row[n]
                errors_row = []
                try:
                    if fields_desc[field]["type"] in ("auto", "integer", "float", "text", "char", "boolean", "date", "datetime"):
                        vals[field] = column.value
                    elif fields_desc[field]["type"] == "foreignkey":
                        RelModel = r[fields_desc[field]["model"]]
                        q = RelModel.select(RelModel.id).where(RelModel.name == column.value or '')
                        if not q.exists():
                            err = _("Row %s, Field %s: record with name %s does not exist")%(i, fields_desc[field]["label"], column.value)
                            errors_row.append(err)
                            errors.append(err)
                        else:
                            vals[field] = q.first().id
                    elif fields_desc[field]["type"] == "select":
                        for value,label in fields_desc[field]["options"]:
                            if label == column.value:
                                vals[field] = value
                                break
                        else:
                            error_msg = _("Row %s, Field %s: %s is not a valid option")%(i, fields_desc[field]["label"], column.value)
                            errors_row.append(error_msg)
                            errors.append(error_msg)
                    else:
                        if column.value:
                            vals[field] = json.loads(column.value)
                        else:
                            vals[field] = None
                except Exception as ex:
                    err_msg = "Row %s, Field %s: %s"%(i, fields_desc[field]["label"], str(ex))
                    errors.append(err_msg)
            if not errors_row:
                try:
                    if vals.get("id"):
                        rec_id = vals["id"]
                        del vals["id"]
                        cls.flr_update(vals, [('id','=',rec_id)])
                        affected_ids.append(rec_id)
                    else:
                        affected_ids.append(cls.flr_create(**vals))
                except Exception as ex:
                    err_msg = _("Row %s: Error when creating/updating record. %s")%(i, str(ex))
                    errors.append(err_msg)
        if errors:
            raise Exception("\n".join(errors))
        return {
            'affected_ids': affected_ids
        }        

@cron(minute="*/30")
def delete_temporary_records():
    for model in Registry:
        Model = Registry[model]
        if Model._transient:
            db.execute_sql("delete from {} where age(now(), created_on) > interval '30 minutes'".format(Model._meta.table_name))

@app.route("/auth", methods=["POST"])
def auth():
    try:
        params = request.get_json()
        if "login" in params:
            login = params.get("login")
        elif "email" in params:
            login = params.get("email")
        password = params.get("password")
        jwt = Registry["FlrUser"].auth(login, password)
        if jwt:
            return jsonify({
                'result': jwt
            })
        else:
            return make_response(jsonify({
            'error': {
                'message': 'Incorrect credentials',
                'data': 'Incorrect credentials'
            }
        }), 401)
    except Exception as ex:
        print(traceback.format_exc())
        return make_response(jsonify({
            'error': {
                'message': str(ex),
                'data': traceback.format_exc()
            }
        }), 500)

@app.route("/call", methods=["POST"])
def call():
    with db.atomic() as transaction:
        try:
            Registry["FlrUser"].decode_jwt(request)
            params = request.get_json()
            request.flr_globals = params.get("$globals", {})
            model_name = params.get("model")
            method_name = params.get("method")
            if method_name in ("create", "update", "delete"):
                method_name = "flr_" + method_name
            args = params.get("args", [])
            kwargs = params.get("kwargs", {})
            rec_id = False
            if ":" in model_name:
                model_name, rec_id = model_name.split(":")
                rec_id = int(rec_id)
            model = Registry[model_name]
            if rec_id:
                record = model.get_by_id(rec_id)
                method = getattr(record, method_name)
            else:
                method = getattr(model, method_name)
            res = method(*args, **kwargs)
            return jsonify({
                'result': res
            })
        except Exception as ex:
            transaction.rollback()
            if isinstance(ex, FlrException):
                return make_response(jsonify({
                    'error': {
                        'message': str(ex),
                        'FlrException': True,
                    }
                }), 500)
            else:
                return make_response(jsonify({
                    'error': {
                        'message': traceback.format_exc(),
                    }
                }), 500)

@app.route("/recoverypassword", methods=["POST"])
def recoverypassword():
    params = request.get_json()
    try:
        email = params.get('email')
        user = Registry["FlrUser"].select().where(Registry["FlrUser"].email==email)
        if not user:
            return make_response(jsonify({
                'error': {
                    'message': _('The email address you entered does not correspond to any user')
                }
            }), 500)
        user = user.first()
        request.uid = user.id
        token = jwt.encode({"id":user.id}, SECRET, algorithm="HS256")
        host = os.getenv('flr_db_host')
        url = "http://%s:%s/resetPassword?token=%s" % (host, os.environ.get("flr_port", 6800), token.decode('ascii'))
        message = _('Click <a href="%s"><strong>here</strong></a> to reset your password') % url
        sendmail("", email, _('Reset password'), message)
        return make_response(jsonify({
            'result': True
        }))
    except Exception as ex:
        print(traceback.format_exc())
        return make_response(jsonify({
            'error': {
                'message': _("Sorry, an error occurred and the email couldn't be sent")
            }
        }), 500)

@app.route("/send_error", methods=["POST"])
def send_error():
    params = request.get_json()
    try:
        message = _('Error sent by the user through the web client:') + '\n%s' % params.get('data', '')
        sendmail("", os.getenv('flr_mail_user'), _('Error report'), message)
        return make_response(jsonify({
            'result': True
        }))
    except Exception as ex:
        return make_response(jsonify({
            'error': {
                'message': str(ex),
                'data': traceback.format_exc(),
            }
        }), 500)

@app.route("/flrimport", methods=["POST"])
def import_from_file():
    with db.atomic() as transaction:
        try:
            token = request.form["token"]
            Registry["FlrUser"].decode_jwt(request, token)
            if 'file' not in request.files:
                raise Exception("No file")
            file = request.files['file']
            if file.filename == '':
                raise Exception("No file")
            if file:
                fd, fname = tempfile.mkstemp(".xlsx")
                os.close(fd)
                file.save(fname)
                fields = request.form["fields"].split(",")
                result = r[request.form["model"]].import_from_file(fields, fname)
                return make_response(jsonify({'result': result}))
        except Exception as ex:
            transaction.rollback()
            print(traceback.format_exc())
            return make_response(jsonify({
                'error': {
                    'message': str(ex),
                    'data': traceback.format_exc()
                }
            }), 500)

@app.route("/app_name", methods=["GET"])
def get_app_name():
    return os.environ["flr_app"]

@app.route("/app_title", methods=["GET"])
def get_app_title():
    return os.environ.get("flr_app_title", os.environ["flr_app"])

@app.route("/send_error_btn", methods=["GET"])
def get_send_error_btn():
    return os.environ.get("flr_send_error_btn")

@app.route("/create_user", methods=["POST"])
def create_user():
    try:
        Registry["FlrUser"].create(name=request.form["name"],
                    password=request.form["password"],
                    login=request.form["login"])
        return redirect('/')
    except:
        print(traceback.format_exc())
        return "Error intente más tarde"

# Serve static files
def send_from_app_public_directory(file):
    #First try to serve it from the app's public directory then from the svelte_client/public folder
    app_public_folder = os.path.join("apps", os.environ["flr_app"], "public")
    if os.path.exists(os.path.join(app_public_folder, file)):
        return send_from_directory(app_public_folder, file)
    else:
        return send_from_directory(os.path.join('svelte_client', 'public'), file)
@app.route("/")
def base():
    return send_from_app_public_directory('index.html')

@app.route("/<path:path>")
def home(path):
    return send_from_app_public_directory(path)

@app.route("/resetPassword", methods=["GET", "POST"])
def resetpassword():
    if request.method == "GET":
        return send_from_app_public_directory('index.html')
    else:
        params = request.get_json()
        decoded = jwt.decode(params.get('token'), SECRET, algorithms=['HS256'])
        Registry["FlrUser"].flr_update({
            'password': params.get('password'),
        }, [('id','=',decoded.get('id'))])
        return make_response(jsonify({
            'result': True
        }))

#Resful API helpers
class api:

    specs = {}

    def wrapper(f):
        @wraps(f)
        def g(*args, **kwargs):
            with db.atomic() as transaction:
                try:
                    Registry["FlrUser"].decode_jwt(request)
                    return jsonify(f(*args, **kwargs))
                except Exception as ex:
                    transaction.rollback()
                    code = 500
                    if str(ex) == "Invalid JWT" or str(ex) == "Needs Authorization":
                        code = 401
                    print(traceback.format_exc())
                    return make_response(jsonify({
                        'error': {
                            'message': str(ex),
                            'data': traceback.format_exc()
                        }
                    }), code)
        return g

    @wrapper
    def get(model, fields):
        page = int(request.args.get("page", "0"))
        limit = int(request.args.get("limit", "0"))
        count = Registry[model].read([], count=True)
        paginate = False
        if page and limit:
            paginate = (page, limit)
        Model = Registry[model]
        if not fields:
            fields = Model.get_fields()
            fields = [f for f in fields if f!='password']
        result = Model.read(fields, paginate=paginate, order="id desc")
        return {
            'count': count,
            'result': result
        }

    @wrapper
    def post(model):
        params = request.get_json()
        Registry[model].flr_create(**params)
        return {'result': _('Record successfully created')}

    @wrapper
    def put(model, id):
        params = request.get_json()
        updated = Registry[model].flr_update(params, [('id','=',id)])
        if updated:
            return {'result': _('Record successfully updated')}
        else:
            return {'result': _('No record was updated')}

    @wrapper
    def delete(model, id):
        deleted = Registry[model].flr_delete([id])
        if deleted:
            return {'result': _('Record successfully deleted')}
        else:
            return {'result': _('No record was deleted')}

    def make_restful(name, model, post_func=False, put_func=False, specs=False, get_fields=[]):
        if not post_func:
            post_func = lambda: api.post(model)
        if not put_func:
            put_func = lambda id: api.put(model, id)
        routes = (
            ('get_%s'%name, 'GET', '/%s'%name, lambda: api.get(model, get_fields)),
            ('post_%s'%name, 'POST', '/%s'%name, post_func),
            ('put_%s'%name, 'PUT', '/%s/<int:id>'%name, put_func),
            ('delete_%s'%name, 'DELETE', '/%s/<int:id>'%name, lambda id: api.delete(model, id))
        )
        for name, method, url, func in routes:
            api.add_url_rule(name, method, url, func, specs=specs)

    def add_url_rule(name, method, url, func, specs=False):
        app.add_url_rule(url, name, func, methods=[method])
        if specs:
            api.specs[name] = specs

ROUTES_UNDOCUMENTED = ("/","/<path:path>","/static/<path:filename>","/flrroutes","/create_user")

@app.route("/flrroutes", methods=["GET"])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        rule_str = "%s"%rule
        if rule_str not in ROUTES_UNDOCUMENTED:
            routes.append([rule.endpoint,
            ",".join([m for m in rule.methods if m in ("GET","POST","DELETE","PUT")]),
            rule_str,
            ])
    routes.sort(key=lambda x:x[2])
    routes = ["{:20s} {:10s} {:50s}".format(route[0], route[1], route[2]) for route in routes]
    resp = Response("\n".join(routes))
    resp.headers["Content-type"] = "text/plain"
    return resp
