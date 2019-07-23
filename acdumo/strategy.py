#===============================================================================
# strategy.py
#===============================================================================

"""Strategy blueprint

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
    Blueprint, flash, g, redirect, render_template, request, url_for,
    current_app
)
from flask_login import current_user, login_required
from werkzeug.exceptions import abort



# Blueprint assignment =========================================================

bp = Blueprint('blog', __name__, url_prefix='/strategy')




# Functions ====================================================================

@bp.route('/index')
@login_required
def index():
    f"""Render the strategy index"""

    return render_template(
        'strategy/index.html'
    )