import peewee as pw
from flask import request, Response
from flare import app, BaseModel, Registry as r, ReportHelpers, add_pages
from jinja2 import Template
import subprocess
import os
import tempfile
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO
import jwt

SECRET = os.environ.get("jwt_secret")

class FlrReport(BaseModel):
    name = pw.CharField(verbose_name="Name", unique=True)
    model = pw.CharField(verbose_name="Model")
    template_path = pw.CharField(verbose_name="Template file path", null=True)
    report_helper = pw.CharField(verbose_name="Report helper class", null=True)
    report_type = pw.CharField(verbose_name="Report type", default="default", choices=[
        ('default','Default'), ('custom', 'Custom')])
    renderer_method = pw.CharField(verbose_name="Renderer method", null=True)
    mime_type = pw.CharField(verbose_name="MIME Type", default="application/pdf")

    @classmethod
    def request_report(cls, report_name, ids):
        report = cls.get(cls.name==report_name)
        filename, data = report.render(ids)
        fd, fname = tempfile.mkstemp()
        os.close(fd)
        with open(fname, "wb") as f:
            f.write(data)
        payload = {
            'path': fname,
            'filename': filename,
            'mime_type': report.mime_type
        }
        encoded = jwt.encode(payload, SECRET, algorithm='HS256')
        return {
            'token': encoded.decode("ascii"),
        }

    def render(self, ids):
        if self.report_type == "default":
            return self._render_default(ids)
        else:
            return self._render_custom(ids)

    def _render_default(self, ids):
        Model = r[self.model]
        report_name = self.name
        if not self.template_path:
            raise Exception("No template provided")
        with open(self.template_path) as f:
            template = Template(f.read())
        final_pdf = PdfFileWriter()
        for rec in Model.select().where(Model.id.in_(ids)):
            context = {'rec': rec}
            helper = False
            if self.report_helper and self.report_helper in ReportHelpers:
                helper = ReportHelpers[self.report_helper]()
            # Report helper classes can implement the method get_context to update the variables
            # that will be sent to the render function
            if helper and hasattr(helper, "get_context"):
                context.update(helper.get_context(rec))
            rendered = template.render(**context)
            # Helper classes can implement the method post_render to edit the generated html
            if helper and hasattr(helper, "post_render"):
                rendered = helper.post_render(rec, rendered)
            fd, fname = tempfile.mkstemp(".html")                           
            os.close(fd)                                                    
            with open(fname, "w") as f:                                     
                f.write(rendered)
            fd, outfname = tempfile.mkstemp(".pdf")                         
            os.close(fd)                          
            subprocess.call(["wkhtmltopdf", fname, outfname])
            with open(outfname, "rb") as f:                                 
                data = f.read()
            # Helper classes can implement the method post_convert to edit the generated pdf
            if helper and hasattr(helper, "post_convert"):
                data = helper.post_convert(rec, data)
            reader = PdfFileReader(BytesIO(data))
            add_pages(reader, final_pdf)
        output = BytesIO()
        final_pdf.write(output)
        data = output.getvalue()
        # Helper classes can provide a custom filename, if not just use the report name
        if helper and hasattr(helper, "get_filename"):
            filename = helper.get_filename(ids)
        else:
            if len(ids) == 1:
                filename = report_name + str(ids[0]) + ".pdf"
            else:
                filename = report_name + ".pdf"
        return filename, data

    def _render_custom(self, ids):
        Model = r[self.model]
        report_name = self.name
        if not self.renderer_method:
            raise Exception("No renderer method provided")
        method = getattr(Model, self.renderer_method)
        filename, data = method(ids)
        return filename, data

FlrReport.r()

@app.route("/report/download", methods=["GET"])
def download_report():
    token = request.args["reqToken"]
    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    with open(decoded.get("path"), "rb") as f:
        data = f.read()
    os.unlink(decoded.get("path"))
    response = Response(data, mimetype=decoded.get("mime_type"))
    filename = decoded.get("filename")
    response.headers["Content-Disposition"] = "attachment; filename=%s"%filename
    return response