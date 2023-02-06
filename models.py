from config import db
from flask_login import UserMixin

class Mails(db.Model):
    mail_hash = db.Column(db.String(128), primary_key=True, unique=True)
    title = db.Column(db.String(32), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='mails', uselist=False, viewonly=True)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    username = db.Column(db.String(64), unique=True)
    avatar = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(100), nullable=False)
    recovery_link = db.Column(db.String(64), nullable=True)
    mails_list = db.relationship('Mails', cascade='all, delete')
