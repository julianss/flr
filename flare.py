from flask import Flask, request, jsonify, send_from_directory, redirect, make_response, Response
from registry import Registry, db
import peeweedbevolve
import peewee as pw
from playhouse.shortcuts import model_to_dict
import traceback
import operator as __operator__
import os
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
import base64
from functools import wraps
from datetime import datetime

app = Flask(__name__)

if os.environ.get("enable_cors") == "True":
    from flask_cors import CORS
    CORS(app)

class BaseModel(pw.Model):
    class Meta:
        database = db

    @classmethod
    def r(cls):
        if cls.__name__ in Registry:
            raise Exception(cls.__name__ + " already exists in the model registry")
        Registry[cls.__name__] = cls
        cls._meta.add_field("created_by", pw.ForeignKeyField(Registry["FlrUser"], null=True))
        cls._meta.add_field("created_on", pw.DateTimeField(null=True))
        cls._meta.add_field("updated_by", pw.ForeignKeyField(Registry["FlrUser"], null=True))
        cls._meta.add_field("updated_on", pw.DateTimeField(null=True))

    @classmethod
    def get_fields(cls):
        fields = ["id"]
        for k in cls._meta.fields.keys():
            fields.append(k)
        for k in cls._meta.manytomany.keys():
            fields.append(k)
        for k in dir(cls):
            tattr = type(getattr(cls, k))
            if tattr == property:
                if k not in ("dirty_fields", "_pk"):
                    fields.append(k)
            if tattr == pw.BackrefAccessor:
                fields.append(k)
        return fields

    @classmethod
    def get_fields_desc(cls, which=[]):
        related_fields = []
        for field in which:
            if "." in field:
                related_fields.append(field)
        fields = {}
        which.append("id")
        for k in cls._meta.fields.keys():
            if k not in which:
                continue
            field = cls._meta.fields[k]
            desc = {
                'label': field.verbose_name or field.help_text,
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
            verbose_name = field.verbose_name if hasattr(field, "verbose_name") else False
            help_text = field.help_text if hasattr(field, "help_text") else False
            fields[k] = {
                'label': verbose_name or help_text,
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
                fields[k] = {}
            if tattr == pw.BackrefAccessor:
                field = getattr(cls, k)
                fields[k] = {
                    'label': k.capitalize(),
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
        fields["id"]["label"] = "ID"
        return fields

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
        return super(BaseModel, cls).create(**fields)

    @classmethod
    def flr_create(cls, **fields):
        #Take out @properties, only regular fields can be created, except attachments
        attachments = []
        if 'attachments' in fields:
            attachments = fields["attachments"]
            del fields["attachments"]
        fields = {k:fields[k] for k in fields if type(getattr(cls, k)) != property}
        m2m = []
        #Identify many2many fields, create record without them, will be added later
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                if type(pw_field) == pw.ManyToManyField:
                    m2m.append(field_name)
        fields_no_m2m = {k:fields[k] for k in fields if k not in m2m}
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
        created = cls.create(**fields_no_m2m)
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                #Create one2many related records
                if type(pw_field) == pw.BackrefAccessor:
                    for fields2 in fields[field_name]:
                        fields2[pw_field.field.name] = created.id
                        pw_field.rel_model.create(**fields2)
                elif type(pw_field) == pw.ManyToManyField:
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
        if attachments:
            Registry["FlrFile"].flr_update({
                'model': cls.__name__,
                'rec_id': created_id
            }, [('id', 'in', attachments)])
        return created_id

    @classmethod
    def flr_update(cls, fields, filters):
        #Take out @properties and reference fields, only regular fields can be updated
        fields = {k:fields[k] for k in fields if type(getattr(cls, k)) not in (property, pw.BackrefAccessor)}
        m2m = []
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                #Identify many2many fields, take them out they must be updated separately
                if type(pw_field) == pw.ManyToManyField:
                    m2m.append(field_name)
                #One2many related records can be either created or updated now
                elif type(pw_field) == pw.BackrefAccessor:
                    for fields2 in fields[field_name]:
                        #It's new, create it
                        if not "id" in fields2:
                            fields2[pw_field.field.name] = created.id
                            pw_field.rel_model.create(**fields2)
                        #Already exists, update it
                        else:
                            rel_id_field = getattr(pw_field.rel_model, "id")
                            rel_id = fields2["id"]
                            del fields2["id"]
                            pw_field.rel_model.update(**fields2).where(rel_id_field==rel_id)
                    #Take it out so a normal update isn't attempted on this field
                    del fields[field_name]
        fields_no_m2m = {k:fields[k] for k in fields if k not in m2m}
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
            query = cls.update(**fields_no_m2m)
            if filters:
                query = cls.filter_query(query, filters)
            modified = query.execute()
        if m2m:
            query = cls.select(cls.id)
            if filters:
                query = cls.filter_query(query, filters)
            for record in query:
                for m2m_field in m2m:
                    getattr(record, m2m_field).clear()
                    getattr(record, m2m_field).add([
                        x["id"] if type(x) == dict else x
                        for x in fields[m2m_field]])
        return modified

    @classmethod
    def flr_delete(cls, filters):
        query = cls.delete()
        if filters:
            query = cls.filter_query(query, filters)
        deleted = query.execute()
        return deleted

    @classmethod
    def read(cls, fields, filters=[], paginate=False, order=None, count=False):
        if order is None and hasattr(cls, "_order"):
            order = cls._order
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
        if filters or paginate:
            query = cls.filter_query(query, filters, paginate)
        if count:
            return query.count()
        else:
            results = []
            # Add foreign key fields so model_to_dict renders the name of the related record
            if only:
                for pw_field in only:
                    if type(pw_field) == pw.ForeignKeyField:
                        only.append(getattr(pw_field.rel_model, "id"))
                        if hasattr(pw_field.rel_model, "name"):
                            only.append(getattr(pw_field.rel_model, "name"))
            for model in query:
                data = model_to_dict(model, only=only, recurse=True, extra_attrs=extra_attrs)
                if m2m:
                    for field_name in m2m:
                        related_records = getattr(model, field_name)
                        related_records_dicts = []
                        for relr in related_records:
                            rendered = {
                                'id': relr.id,
                                'name': relr.name if hasattr(relr,"name") else None,
                            }
                            for related_field in related_fields_m2m[field_name]:
                                rendered[related_field] = getattr(relr, related_field)
                            related_records_dicts.append(rendered)
                        data[field_name] = related_records_dicts
                results.append(data)
            return results

    @classmethod
    def export(cls, fields, filters=[], paginate=False, order=None):
        results = cls.read(fields, filters, paginate, order)
        wb = Workbook()
        ws = wb.active
        row = 1
        for col,field in enumerate(fields,1):
            f = getattr(cls, field)
            if field == 'id':
                label = "ID"
            elif hasattr(f, "help_text"):
                label = f.help_text
            else:
                label = f.__doc__ #get field name from property docstring
            ws.cell(row=row, column=col, value=label)
        row += 1
        for rec in results:
            for col,field in enumerate(fields,1):
                val = rec[field]
                if type(val) == dict:
                    val = val.get("name", val["id"])
                ws.cell(row=row, column=col, value=val)
            row += 1
        datas = save_virtual_workbook(wb)
        return {
            'datas': base64.b64encode(datas).decode("ascii")
        }


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
            print(traceback.format_exc())
            return make_response(jsonify({
                'error': {
                    'message': str(ex),
                    'data': traceback.format_exc()
                }
            }), 500)

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
    return send_from_directory(os.path.join('apps',os.environ["app"],'client','public'), file)
@app.route("/")
def base():
    return send_from_app_public_directory('index.html')
@app.route("/<path:path>")
def home(path):
    return send_from_app_public_directory(path)

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
        return {'result': 'Ítem agregado con éxito'}

    @wrapper
    def put(model, id):
        params = request.get_json()
        updated = Registry[model].flr_update(params, [('id','=',id)])
        if updated:
            return {'result': 'Ítem actualizado con éxito'}
        else:
            return {'result': 'No se actualizó ningún ítem'}

    @wrapper
    def delete(model, id):
        deleted = Registry[model].flr_delete([('id','=',id)])
        if deleted:
            return {'result': 'Ítem eliminado con éxito'}
        else:
            return {'result': 'No se eliminó ningún ítem'}

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
        if rule_str not in ("/","/<path:path>","/static/<path:filename>","/flrroutes","/create_user"):
            routes.append([",".join([m for m in rule.methods if m in ("GET","POST","DELETE","PUT")]), rule_str])
    routes.sort(key=lambda x:x[1])
    routes = ["{:20s} {:50s}".format(route[0], route[1]) for route in routes]
    resp = Response("\n".join(routes))
    resp.headers["Content-type"] = "text/plain"
    return resp
