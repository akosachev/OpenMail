from flask import flash
from hashlib import sha512
from flask_mail import Message
from config import mail, app

def text_hasher(title, message, created_time):
    title = title
    message = message
    created_time = created_time
    result = sha512((title + message + created_time).encode('ascii')).hexdigest()
    return result


def form_error(errors):
    for key, value in errors:
        for error in value:
            error = error.replace('Field', f'Field {key}')
            flash(error)

def send_recovery_link(link, email):
    link = link
    email = email
    msg = Message("Recovery link",
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[],
                              body=f"You recovery link {app.config['DOMAIN_NAME']}{link}")
    msg.recipients.append(email)
    mail.send(msg)
