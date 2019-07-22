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
from ucsd_bisb_unofficial.models import get_db, User, Role
from ucsd_bisb_unofficial.email import send_confirmation_email




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
        return redirect(url_for('jumbotron.index'))
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
        user.add_role(Role.query.filter_by(name='named_user').first())
        db.session.commit()
        send_confirmation_email(user)
        flash(
            'Thanks for registering!  Please check your email to '
            'confirm your email address.'
        )
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/register.html',
        title='Register',
        form=form
    )