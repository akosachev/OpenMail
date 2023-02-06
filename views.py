from config import app, db
from forms import LoginForm, MailForm, EditUserForm, AvatarUpload, RecoveryForm
from models import Users, Mails
from flask import render_template, url_for, redirect, request, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from os import path, remove
from func import text_hasher, form_error, send_recovery_link
from UserLogin import UserLogin
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, current_user, logout_user
from secrets import token_hex


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404', error=error), 404


@app.errorhandler(403)
def page_not_found(error):
    return render_template('403.html', title='403', error=error), 403


@app.route('/', methods=['POST', 'GET'])
def index():
    form = LoginForm()
    next = request.args.get('next')
    return render_template('index.html', form=form, next=next)


@app.route('/login', methods=['POST', 'GET'])
@app.route('/login/<string:recovery_link>', methods=['POST', 'GET'])
def login(recovery_link=None):
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if recovery_link:
        user = Users.query.filter_by(recovery_link=recovery_link).first()
        if user:
            userLogin = UserLogin().create(user.id)
            login_user(userLogin, remember=True)
            try:
                user.recovery_link = None
                db.session.commit()
            except:
                print('remove recovery link error ', recovery_link)
            flash('Change password')
            return redirect(url_for('profile_edit'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = Users.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                userLogin = UserLogin().create(user.id)
                login_user(userLogin, remember=True)
            else:
                flash(f'Wrong email or password. <a href=\'{url_for("recovery", email=email)}\'>Recovery</a>')
        else:
            try:
                user = Users(email=email, password=generate_password_hash(password, method='sha512'))
                db.session.add(user)
                db.session.commit()
                userLogin = UserLogin().create(user.id)
                login_user(userLogin, remember=True)
            except:
                flash('Error create user function')
    if form.errors:
        form_error(form.errors.items())
    return redirect(request.args.get('next') or url_for('profile'))


@app.route('/new_mail', methods=['GET', 'POST'])
@login_required
def new_mail():
    form = MailForm()
    if form.validate_on_submit():
        title = form.title.data
        message = form.message.data
        created_time = datetime.utcnow()
        mail_hash = text_hasher(title, message, str(created_time))
        mail = Mails(mail_hash=mail_hash, title=title, message=message, created_time=created_time,
                     user_id=current_user.id)
        try:
            db.session.add(mail)
            db.session.commit()
            return redirect(url_for('get_mail', mail_hash=mail_hash))
        except:
            return f'Error create mail function'
    if form.errors:
        form_error(form.errors.items())
    return render_template('new_mail.html', form=form)


@app.route('/mail/<string:mail_hash>')
def get_mail(mail_hash):
    status = False
    mail = Mails.query.get_or_404(mail_hash)
    text_hash = text_hasher(mail.title, mail.message, str(mail.created_time))
    if mail_hash == text_hash:
        status = True
    mail.message = mail.message.replace('\r\n', '<br>')
    return render_template('view_mail.html', mail=mail, hash=mail_hash, status=status, text_hash=text_hash)


@app.route('/mail/<string:mail_hash>/delete')
@login_required
def del_mail(mail_hash):
    mail = Mails.query.get_or_404(mail_hash)
    if current_user.id == mail.user_id or current_user.id == 1:
        try:
            db.session.delete(mail)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'Error remove mail function'
    else:
        abort(403)


@app.route('/search', methods=["GET", "POST"])
def search():
    mail = Mails.query.get_or_404(request.form.get('mail_hash'))
    return redirect(url_for('get_mail', mail_hash=request.form.get('mail_hash')))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logout')
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = AvatarUpload()
    user = Users.query.get(current_user.id)
    if form.validate_on_submit():
        file = form.avatar.data
        filename = str(current_user.id) + '_' + secure_filename(file.filename)
        if user.avatar:
            try:
                remove(path.join(app.config['UPLOAD_FOLDER'], user.avatar))
            except:
                print(f"File {user.avatar} not removed")
        file.save(path.join(app.config['UPLOAD_FOLDER'], filename))
        try:
            user.avatar = filename
            db.session.commit()
        except:
            flash('Error create avatar function')
        flash('Avatar updated')
    else:
        flash('Avatar file not valid')
    return redirect(url_for('profile_edit'))


@app.route('/profile')
@app.route('/profile/<int:page>')
@login_required
def profile(page=1):
    page = page
    user = Users.query.get(current_user.id)
    mails_list = Mails.query.filter(Mails.user_id == current_user.id).order_by(Mails.created_time.desc()).paginate(
        page=page, per_page=25, error_out=False)
    return render_template('profile.html', user=user, mails=mails_list)


@app.route('/profile/users')
@app.route('/profile/users/<int:page>')
@login_required
def users(page=1):
    if current_user.id == 1:
        page = page
        user = Users.query.get(current_user.id)
        users_list = Users.query.filter(Users.id != 1).paginate(page=page, per_page=25, error_out=False)
        return render_template('users.html', user=user, users=users_list)
    else:
        abort(404)


@app.route('/profile/mails')
@app.route('/profile/mails/<int:page>')
@login_required
def mails(page=1):
    if current_user.id == 1:
        page = page
        mails_list = Mails.query.order_by(Mails.created_time.desc()).paginate(page=page, per_page=25, error_out=False)
        return render_template('mails.html', mails=mails_list)
    else:
        abort(404)


@app.route('/profile/<int:user_id>/delete')
@login_required
def del_profile(user_id):
    if current_user.id == 1:
        user = Users.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('users'))
        except:
            return 'Error remove user function'
    else:
        abort(404)


@app.route('/profile/edit', methods=['POST', 'GET'])
@login_required
def profile_edit():
    form_upload = AvatarUpload()
    form_edit = EditUserForm()
    user = Users.query.get(current_user.id)
    if form_upload.errors:
        form_error(form_upload.errors.items())

    if form_edit.validate_on_submit():
        email = form_edit.email.data.lower()
        username = form_edit.username.data
        password = form_edit.password.data
        if email != user.email:
            if Users.query.filter_by(email=email).count() == 0:
                try:
                    user.email = email
                    flash('Email updated')
                except:
                    print(f'Error edit user function')
            else:
                flash('Please select another mail.')
        if username != user.username:
            if Users.query.filter_by(username=username).count() == 0:
                try:
                    user.username = username
                    flash('Username updated')
                except:
                    print(f'Error edit user function')
            else:
                flash('Please select another username.')
        try:
            user.password = generate_password_hash(password, method='sha512')
            flash('Password updated')
            db.session.commit()
        except:
            db.session.rollback()
    if form_edit.errors:
        form_error(form_edit.errors.items())
    return render_template('profile_edit.html', user=user, form_upload=form_upload, form_edit=form_edit)


@app.route('/recovery/<string:email>', methods=['GET', 'POST'])
def recovery(email):
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = RecoveryForm()
    form.email.data = email
    if form.validate_on_submit():
        email = form.email.data
        user = Users.query.filter_by(email=email).first()
        if user:
            try:
                recovery_link = token_hex()
                user.recovery_link = recovery_link
                db.session.commit()
                link = url_for('login', recovery_link=recovery_link)
                try:
                    send_recovery_link(link=link, email=email)
                except:
                    print('Link no send')
                    print('You recovery link: ', recovery_link)
                flash('Recovery link send from you email')
                return redirect(url_for('index'))
            except:
                flash('Recovery password function error')
        else:
            flash('This mail not found')

    return render_template('recovery.html', form=form)
