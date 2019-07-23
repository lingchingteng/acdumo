#===============================================================================
# auth.py
#===============================================================================

"""Authentication blueprint

Attributes
----------
bp : Blueprint
    blueprint object, see the flask tutorial/documentation:

    http://flask.pocoo.org/docs/1.0/tutorial/views/

    http://flask.pocoo.org/docs/1.0/blueprints/
"""




# Imports ======================================================================

from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    current_app
)
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse
from acdumo.forms import (
    LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
)
from acdumo.models import get_db, User
from acdumo.email import (
    send_confirmation_email, send_password_reset_email
)




# Blueprint assignment =========================================================

bp = Blueprint('auth', __name__, url_prefix='/auth')




# Functions ====================================================================

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user
    
    If the current user is already logged in, they will be redirected to the
    index page.

    Otherwise, the registration page will be rendered. It includes a
    RegistrationForm (see `forms.py`).
    
    If the supplied email is on the approved email list (and does not already
    have an account, see models.User), a new user will be created from the form
    data and added to the database. There it will await confirmation (see
    `confirm_email`)
    """

    if current_user.is_authenticated:
        return redirect(url_for('strategy.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.email.data not in current_app.config['APPROVED_EMAILS']:
            flash('Sorry, that email is not on the approved list.')
            return redirect(url_for('auth.login'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db = get_db()
        db.create_all()
        db.session.add(user)
        db.session.commit()
        send_confirmation_email(user)
        flash('Please check your email to confirm your email address.')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/register.html',
        title='Register',
        form=form
    )


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in to the site

    If the current user is already logged in, they will be redirected to the
    index page.

    Otherwise, the login page will be rendered. It includes a LoginForm (see
    `forms.py`). Supplying valid credentials will allow the user to log in.
    """

    if current_user.is_authenticated:
        return redirect(url_for('strategy.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or any(
            (
                not user.check_password(form.password.data),
                not user.email_confirmed
            )
        ):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('strategy.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Log In', form=form)


@bp.route('/logout')
def logout():
    """Log out the current user"""

    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/confirm/<token>')
def confirm_email(token):
    """Email confirmation page

    If the current user is already logged in, they will be redirected to the
    index page.

    This function renders the page liked to by the registration confirmation
    email. It includes a message about the success or failure of the
    confirmation.

    Parameters
    ----------
    token
        The JSON web token
    """

    if current_user.is_authenticated:
        return redirect(url_for('strategy.index'))
    user = User.verify_confirm_email_token(token)
    if not user:
        flash('Strange, no account found.', 'error')
    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.utcnow()
        db = get_db()
        db.session.add(user)
        db.session.commit()
        flash('Thank you for confirming your email address!')
    return redirect(url_for('auth.login'))


@bp.route('/reset_password_request', methods=('GET', 'POST'))
def reset_password_request():
    """Request a password reset

    If the current user is already logged in, they will be redirected to the
    index page.

    Otherwise, the reset password page will be rendered. It includes a
    ResetPasswordRequestForm (see `forms.py`). Submitting a valid
    username-email pair will cause a password reset email to be sent.
    """

    if current_user.is_authenticated:
        return redirect(url_for('strategy.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.email == form.email.data:
            send_password_reset_email(user)
            flash(
                'Check your email for the instructions to reset your password'
            )
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid username/email pair')
            return redirect(url_for('auth.reset_password_request'))
    return render_template(
        'auth/reset_password_request.html',
        title='Reset Password',
        form=form
    )


@bp.route('/reset_password/<token>', methods=('GET', 'POST'))
def reset_password(token):
    """Reset a user's password
    
    If the current user is already logged in, they will be redirected to the
    index page.

    This function renders the page linked to by the password reset email. The
    link includes a JSON web token as a variable component of the URL. If the
    token cannot be verified, the user is redirected to the login page.

    If the token is verified, the user's password will be reset according to
    the data entered into the included ResetPasswordForm (see `forms.py`).

    Parameters
    ----------
    token
        the JSON web token
    """

    if current_user.is_authenticated:
        return redirect(url_for('strategy.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db = get_db()
        db.session.commit()
        flash('Your password has been reset.')    
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
