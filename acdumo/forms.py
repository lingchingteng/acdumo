#===============================================================================
# forms.py
#===============================================================================

"""Forms (subclasses of FlaskForm, see Flask-WTF:
http://flask-wtf.readthedocs.io/en/stable/ )
"""




# Imports  =====================================================================

from datetime import datetime

from flask import request, current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, TextAreaField
)
from wtforms.validators import (
    ValidationError, DataRequired, Email, EqualTo, Length
)
from acdumo.models import User




# Classes ======================================================================

# Forms ------------------------------------------------------------------------

class LoginForm(FlaskForm):
    """A form for user login credentials

    Attributes
    ----------
    username : StringField
    password : PasswordField
    remember_me : BooleanField
    submit : SubmitField
    """

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    """A form for user registration info

    Attributes
    ----------
    username : StringField
    email : StringField
    password : PasswordField
    password2 : PasswordField
    submit : SubmitField
    """

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    """A form for a password reset request

    Attributes
    ----------
    username : StringField
    email : StringField
    submit : SubmitField
    """

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    """A form for providing a new password

    Attributes
    ----------
    password : PasswordField
    password2 : PasswordField
    submit : SubmitField
    """

    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Request Password Reset')


class StrategyForm(FlaskForm):
    """A form for strategy queries

    Attributes
    ----------
    date : StringField
    tickers : StringField
    submit : SubmitField
    """

    date = StringField('yyyy-mm-dd', default=datetime.today().strftime('%Y-%m-%d'))
    tickers = StringField('TK1 TK2 TK3...', default='SPY TLT VSS SCZ')
    submit = SubmitField('Submit')


class SubscribeForm(FlaskForm):
    """A form for email subscription

    Attributes
    ----------
    tickers : StringField
    submit : SubmitField
    """
    
    tickers = StringField('TK1 TK2 TK3...', default='SPY TLT VSS SCZ')
    submit = SubmitField('Subscribe')


class UnsubscribeForm(FlaskForm):
    """A form for email subscription

    Attributes
    ----------
    submit : SubmitField
    """

    submit = SubmitField('Unsubscribe')
