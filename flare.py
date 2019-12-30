from flask import Flask, request, jsonify, send_from_directory, redirect
from registry import Registry, db
import peeweedbevolve
import peewee as pw
from playhouse.shortcuts import model_to_dict
import traceback
import operator as __operator__
import os

app = Flask(__name__)

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
                expr = op(field, value)
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
        query = query.where(*stack)
        if paginate:
            query = query.paginate(paginate[0], paginate[1])
        return query

    @classmethod
    def flr_create(cls, **fields):
        created = cls.create(**fields)
        for field_name in fields:
            if hasattr(cls, field_name):
                pw_field = getattr(cls, field_name)
                if type(pw_field) == pw.BackrefAccessor:
                    for fields2 in fields[field_name]:
                        fields2[pw_field.field.name] = created.id
                        pw_field.rel_model.create(**fields2)
        return created.id

    @classmethod
    def flr_update(cls, fields, filters):
        query = cls.update(**fields)
        if filters:
            query = cls.filter_query(query, filters)
        modified = query.execute()
        return modified

    @classmethod
    def flr_delete(cls, filters):
        query = cls.delete()
        if filters:
            query = cls.filter_query(query, filters)
        deleted = query.execute()
        return deleted

    @classmethod
    def read(cls, fields, filters=[], paginate=False, order=None):
        only = None
        if fields:
            if "id" not in fields:
                fields.append("id")
            only = []
            for field_name in fields:
                field = getattr(cls, field_name)
                only.append(field)
        results = []
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
        if filters or paginate:
            query = cls.filter_query(query, filters, paginate)
        #Add foreign key fields so model_to_dict renders the name of the related record
        if only:
            for pw_field in only:
                if type(pw_field) == pw.ForeignKeyField:
                    only.append(getattr(pw_field.rel_model, "id"))
                    if hasattr(pw_field.rel_model, "name"):
                        only.append(getattr(pw_field.rel_model, "name"))
        for model in query:
            data = model_to_dict(model, only=only, recurse=True)
            results.append(data)
        return results

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
        return send_from_app_public_directory('index.html')
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