from flask_wtf import Form
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('keep me log in')
    submit = SubmitField('Login')


class RegisterForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(), Length(1, 64),
                                                Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                'Usernames must have only letters, '
                                                'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='password must math')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    @staticmethod
    def validate_email(field):
        email = User.query.filter_by(email=field.data).first()
        if email is not None:
            raise ValidationError('Email already registered .')

    @staticmethod
    def validate_username(field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')


class ChangerPasswordForm(Form):
    oldpassword = PasswordField('Old Password', validators=[Required()])
    newpassword = PasswordField('New Password', validators=[Required()])
    newpassword2 = PasswordField('Confirm new Password', validators=[Required(),
                                                                     EqualTo('newpassword',
                                                                      'password must math')])
    submit = SubmitField('Change Password')


class BeforeResetPasswordForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    confirm = SubmitField("Confirm")


class ResetPasswordForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    newpassword = PasswordField('New Password', validators=[Required()])
    confirm = SubmitField("Confirm")


class ChangeMailAddrForm(Form):
    email2 = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    confirm = SubmitField('Confirm')


class NewMailForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    confirm = SubmitField('Confirm')
