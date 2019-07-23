#===============================================================================
# protected.py
#===============================================================================

"""Serve protected files

Attributes
----------
bp : Blueprint
    blueprint object, see the flask tutorial/documentation:

    http://flask.pocoo.org/docs/1.0/tutorial/views/

    http://flask.pocoo.org/docs/1.0/blueprints/
"""




# Imports ======================================================================

import os

from flask import Blueprint, send_from_directory, current_app
from flask_login import login_required




# Blueprint assignment =========================================================

bp = Blueprint('protected', __name__, url_prefix='/protected')




# Functions ====================================================================

@bp.route('/<path:filename>')
@login_required
def protected(filename):
    """Serve a protected file
    
    Parameters
    ----------
    filename
        Location of the file to serve on disk
    """

    return send_from_directory(
        os.path.join(current_app.instance_path, 'protected'),
        filename
    )
