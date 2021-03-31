import peewee as pw
from flare import BaseModel, app, db, Registry, _, n_
from flask import send_file, jsonify, make_response, request
import uuid
import os
import traceback
import base64

FILESTORE_PATH = os.environ.get("flr_filestore_path", "./filestore")
APP = os.environ.get("flr_app")


class AttachmentsMixin:
    @property
    def attachments(self):
        return FlrFile.read(["name"], [['rec_id','=',self.id], ['model','=',self.__class__.__name__]])

    def update_attachments(self, new_ids):
        old_ids = [rec["id"] for rec in self.attachments]
        if set(old_ids) != set(new_ids):
            FlrFile.flr_update({
                'model': type(self).__name__,
                'rec_id': self.id
            }, [('id','in',new_ids)])
            for old_id in old_ids:
                if old_id not in new_ids:
                    FlrFile.flr_delete([('id','=',old_id)])
        return True

class FlrFile(BaseModel):
    name = pw.CharField(verbose_name=n_("Name"))
    path = pw.CharField(verbose_name=n_("Filestore Path"))
    model = pw.CharField(verbose_name=n_("Model"), null=True)
    rec_id = pw.CharField(verbose_name=n_("Record id"), null=True)

    @classmethod
    def create_from_data(cls, data, name=False):
        generated_name = str(uuid.uuid4()).replace("-","")
        if not os.path.isdir(FILESTORE_PATH):
            os.mkdir(FILESTORE_PATH)
        if not os.path.isdir(os.path.join(FILESTORE_PATH, APP)):
            os.mkdir(os.path.join(FILESTORE_PATH, APP))
        folder = os.path.join(FILESTORE_PATH, APP, generated_name[0:2])
        if not os.path.isdir(folder):
            os.mkdir(folder)
        fullpath = os.path.join(folder, generated_name[2:])
        with open(fullpath, "wb") as f:
            f.write(base64.b64decode(data))
        vals = {
            'name': name or generated_name,
            'path': fullpath,
        }
        created = Registry["FlrFile"].create(**vals)
        return created.id

    def get_content(self):
        f = open(self.path, "rb")
        content = f.read()
        f.close()
        return content

FlrFile.r()

@app.route("/flrattach", methods=["POST"])
def flr_attach():
    try:
        Registry["FlrUser"].decode_jwt(request)
        if 'file' not in request.files:
            raise Exception(_("No file given"))
        file = request.files['file']
        if file.filename == '':
            raise Exception(_("No file given"))
        if file:
            generated_name = str(uuid.uuid4()).replace("-","")
            if not os.path.isdir(FILESTORE_PATH):
                os.mkdir(FILESTORE_PATH)
            if not os.path.isdir(os.path.join(FILESTORE_PATH, APP)):
                os.mkdir(os.path.join(FILESTORE_PATH, APP))
            folder = os.path.join(FILESTORE_PATH, APP, generated_name[0:2])
            if not os.path.isdir(folder):
                os.mkdir(folder)
            fullpath = os.path.join(folder, generated_name[2:])
            file.save(fullpath)
            vals = {
                'name': file.filename,
                'path': fullpath,
            }
            if 'model' in request.form and 'rec_id' in request.form:
                vals.update({
                    'model': request.form["model"],
                    'rec_id': request.form["rec_id"]
                })
            created = FlrFile.create(**vals)
            return jsonify({
                'result': created.id
            })
    except Exception as ex:
        print(traceback.format_exc())
        return make_response(jsonify({
            'error': {
                'message': str(ex),
                'data': traceback.format_exc()
            }
        }), 500)

@app.route("/flrdownload/<int:file_id>", methods=["GET"])
def flr_download(file_id):
    token = request.args.get("token")
    Registry["FlrUser"].decode_jwt(request, token)
    file = FlrFile.get_by_id(file_id)
    return send_file(file.path, as_attachment=True, attachment_filename=file.name)