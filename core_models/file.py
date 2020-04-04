import peewee as pw
from flare import BaseModel, app, db, Registry, request
from flask import send_file, jsonify, make_response
import uuid
import os
import traceback

FILESTORE_PATH = os.environ.get("filestore_path", "./filestore")
APP = os.environ.get("app")

class AttachmentsMixin:
    @property
    def attachments(self): 
        return FlrFile.read(["name"], [['rec_id','=',self.id], ['model','=',self.__class__.__name__]])

class FlrFile(BaseModel):
    name = pw.CharField(help_text="Name")
    path = pw.CharField(help_text="Filestore Path")
    model = pw.CharField(help_text="Model", null=True)
    rec_id = pw.CharField(help_text="Record id", null=True)

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
            raise Exception("No file")
        file = request.files['file']
        if file.filename == '':
            raise Exception("No file")
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