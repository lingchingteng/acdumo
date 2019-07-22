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
