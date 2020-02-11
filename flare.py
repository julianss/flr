from flask import Flask, request, jsonify, send_from_directory, redirect
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
    def flr_create(cls, **fields):
        m2m = []
        #Identify many2many fields, create record without them, will be added later
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                if type(pw_field) == pw.ManyToManyField:
                    m2m.append(field_name)
        fields_no_m2m = {k:fields[k] for k in fields if k not in m2m}
        created = cls.create(**fields_no_m2m)
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                if type(pw_field) == pw.BackrefAccessor:
                    for fields2 in fields[field_name]:
                        fields2[pw_field.field.name] = created.id
                        pw_field.rel_model.create(**fields2)
                elif type(pw_field) == pw.ManyToManyField:
                    to_add = []
                    for related_id in fields[field_name]:
                        to_add.append(pw_field.rel_model.get_by_id(related_id))
                    if to_add:
                        getattr(created, field_name).add(to_add)
                        created.save()
        return created.id

    @classmethod
    def flr_update(cls, fields, filters):
        #Identify many2many fields, take them out they must be updated separately
        m2m = []
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                if type(pw_field) == pw.ManyToManyField:
                    m2m.append(field_name)
        fields_no_m2m = {k:fields[k] for k in fields if k not in m2m}
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
                        getattr(record, m2m_field).add(fields[m2m_field])
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
        only = None
        extra_attrs = []
        if not fields:
            fields = ["id"]
        if fields:
            if "id" not in fields:
                fields.append("id")
            only = []
            m2m = []
            for field_name in fields:
                field = getattr(cls, field_name)
                #if field name is a @property of the model, it must be added to the extra_attrs list
                if type(field) == property:
                    extra_attrs.append(field_name)
                #if field is many2many it must be handled separately, we want to render it as array of ids
                elif type(field) == pw.ManyToManyField:
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
            #Add foreign key fields so model_to_dict renders the name of the related record
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
                        data[field_name] = [x.id for x in getattr(model, field_name)]
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
        login = params.get("login")
        password = params.get("password")
        jwt = Registry["FlrUser"].auth(login, password)
        if jwt:
            return jsonify({
                'result': jwt
            })
        else:
            return jsonify({
            'error': {
                'message': 'Incorrect credentials',
                'data': 'Incorrect credentials'
            }
        })
    except Exception as ex:
        print(traceback.format_exc())
        return jsonify({
            'error': {
                'message': str(ex),
                'data': traceback.format_exc()
            }
        })

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
            return jsonify({
                'error': {
                    'message': str(ex),
                    'data': traceback.format_exc()
                }
            })

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