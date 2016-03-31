from flask import render_template, url_for, redirect, flash, request
from . import auth
from flask_login import login_user, logout_user, login_required
from ..models import User, generate_token, confirm_token
from .forms import LoginForm, RegisterForm
from app import db
from flask_login import current_user
from ..email import send_email
from  .forms import ChangerPasswordForm, ResetPasswordForm, BeforeResetPasswordForm, ChangeMailAddrForm, NewMailForm
from flask import abort

@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('auth.login'))
    if current_user.confirm(token):
        flash("You have confirmed your account . Thanks !")
    else:
        flash("The confirmation link is invalid or has expired .")
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'confirm', user=current_user, token=token)
    flash('A new confirmation has been sent to you by email .')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=["POST", "GET"])
@login_required
def change_password():
    form = ChangerPasswordForm()
    if form.validate_on_submit():
        if current_user.is_authenticated and current_user.confirmed and current_user.verify_password(form.oldpassword.data) :
            current_user.password = form.newpassword.data
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
    return render_template('changepassword.html', form=form)


@auth.route('/reset-password/<token>', methods=["POST", "GET"])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if confirm_token(token):
            temp_user = User.query.filter_by(email=form.email.data).first()
            temp_user.password = form.newpassword.data
            db.session.add(temp_user)
            db.session.commit()
            return redirect(url_for("auth.login"))
        else:
            abort(404)
    return render_template('resetpassword.html', form=form)


@auth.route('/reset', methods=["POST", "GET"])
def reset():
    form = BeforeResetPasswordForm()
    if form.validate_on_submit():
        token = generate_token()
        send_email(form.email.data, 'Reset Your Password', 'reset', user=form.username.data, token=token)
        flash('A confirmation has been sent to you by email .')
        return redirect(url_for('main.index'))
    return render_template('beforeresetpassword.html', form=form)


@auth.route('/changemailaddr', methods=["POST", "GET"])
@login_required
def change_mail_addr():
    form = ChangeMailAddrForm()
    if form.validate_on_submit():
        token = generate_token()
        send_email(form.email2.data, 'Reset Your Password', 'change', user=current_user.username, token=token)
        flash('A confirmation has been sent to you by email .')
        return redirect(url_for('main.index'))
    return render_template('changemailaddr.html', form=form)


@auth.route('/changemailaddr/<token>', methods=["POST", "GET"])
@login_required
def change(token):
    form = NewMailForm()
    if form.validate_on_submit():
        if confirm_token(token):
            current_user.email = form.email.data
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
    return render_template('newmail.html', form=form)



