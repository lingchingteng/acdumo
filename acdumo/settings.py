#===============================================================================
# settings.py
#===============================================================================

"""Settings blueprint

Attributes
----------
bp : Blueprint
    blueprint object, see the flask tutorial/documentation:

    http://flask.pocoo.org/docs/1.0/tutorial/views/

    http://flask.pocoo.org/docs/1.0/blueprints/
"""




# Imports ======================================================================

from flask import (
    Blueprint, render_template, current_app, flash, redirect, url_for
)
from flask_login import current_user, login_required
from werkzeug.exceptions import abort

from ucsd_bisb_unofficial.principals import named_permission
from ucsd_bisb_unofficial.models import get_db, User
from ucsd_bisb_unofficial.forms import SubscribeForm, UnsubscribeForm




# Blueprint assignment =========================================================

bp = Blueprint('settings', __name__, url_prefix='/settings')




# Functions ====================================================================

@bp.route('/index', methods=('GET', 'POST'))
@login_required
@named_permission.require(http_exception=403)
def index():
    """Render the settings index"""
    
    user = User.query.get(current_user.id)
    if not user:
        flash('Strange, no account found.', 'error')
    if user.subscribed:
        form = UnsubscribeForm()
        if form.validate_on_submit():
            user.subscribed = False
            db = get_db()
            db.session.add(user)
            db.session.commit()
            flash('You have unsubscribed from UCSD BISB Unofficial email alerts')
            return redirect(url_for('settings.index'))
    else:
        form = SubscribeForm()
        if form.validate_on_submit():
            user.subscribed = True
            db = get_db()
            db.session.add(user)
            db.session.commit()
            flash('You are now subscribed to UCSD BISB Unofficial email alerts')
            return redirect(url_for('settings.index'))
    return render_template(
        'settings/index.html',
        form=form,
        not_subscribed=not user.subscribed
    )
