from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from os import path
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
# Flask config
app.config['SECRET_KEY'] = 'test_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mail.db'
UPLOAD_FOLDER = path.join(path.dirname(path.realpath(__file__)), 'static/uploads/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1000

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '' #example: test@gmail.com
app.config['MAIL_PASSWORD'] = '' #example: password
app.config['DOMAIN_NAME'] = 'http://127.0.0.1:5000' #example: https://test.com
mail = Mail(app)


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message = "You don't authorized"