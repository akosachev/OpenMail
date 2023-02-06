from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[Email()])
    password = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=32)])
    submit = SubmitField('Sign up')

class RecoveryForm(FlaskForm):
    email = StringField('Email: ', validators=[Email()])
    submit = SubmitField('Recovery')


class AvatarUpload(FlaskForm):
    avatar = FileField('Avatar: ', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Upload')


class EditUserForm(FlaskForm):
    email = StringField('Email: ', validators=[Email()])
    username = StringField('Username: ', validators=[Length(min=4, max=32)])
    password = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=32)])
    password2 = PasswordField('Repeat password: ', validators=[
                                                                DataRequired(),
                                                                Length(min=4, max=32),
                                                                EqualTo('password')])
    submit = SubmitField('Save')


class MailForm(FlaskForm):
    title = StringField('Title: ', validators=[DataRequired(), Length(min=4, max=32)])
    message = TextAreaField('Mail text: ', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Send')