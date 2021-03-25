import datetime
from flask.json import JSONEncoder
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re

def sendmail(fromaddr, toaddrs, subject, message):
    """Function to send email loading enviroment variables of the AppName.
    formaddr -- str like 'System <email@domain.com>' or 'email@domain.com'
    toaddrs -- list or str separated by space or comma
    subject -- str
    message -- str
    """
    msg = MIMEMultipart('alternative')
    if isinstance(toaddrs, str):
        toaddrs = re.split(',| ', toaddrs.strip())
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddrs)
    message = message.replace('\r\n', '<br>')
    message = message.replace('\n', '<br>')
    msg.attach(MIMEText(message, 'html'))
    # message.encode('utf-8')
    server = smtplib.SMTP_SSL(os.getenv('flr_mail_host'), port=int(os.getenv('flr_mail_port', 0)))
    server.login(os.getenv('flr_mail_user'), os.getenv('flr_mail_pass'))
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.quit()

# To render dates in a format different to Flask's default we need a Custom JSON encoder
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")

            elif isinstance(obj, datetime.date):
                return obj.strftime("%Y-%m-%d")

            elif isinstance(obj, datetime.time):
                return obj.strftime()

            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

# Functions used to combine filters. Needed for combining the forced filters
# of the security rules Filters are more easily combined when the expressions
# are normalized, meaning all '&' are explicit.
# These two functions where taken from the odoo codebase almost verbatim.
def normalize_filters(filters):
    result = []
    expected = 1
    operators = {
        '!': 1,
        '|': 2,
        '&': 2
    }
    for token in filters:
        if expected == 0:
            result.insert(0, '&')
            expected = 1
        result.append(token)
        if type(token) in (list, tuple):
            expected -= 1
        else:
            nary = operators[token]
            expected += nary - 1
    assert expected == 0, 'Invalid filters syntax'
    return result

def combine_filters(operator, filters_list):
    result = []
    count = 0
    for filters in filters_list:
        result += filters
        count += 1
    result = [operator] * (count - 1) + result
    return result

#Function to combine various pdfs into one.
# from_here - PdfFileReader from which pages will be read
# to_here - PdfFileWriter where pages will be written
def add_pages(from_here, to_here):
    for n in range(from_here.getNumPages()):
        to_here.addPage(from_here.getPage(n))