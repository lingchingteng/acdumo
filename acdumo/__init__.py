#===============================================================================
# __init__.py
#===============================================================================

"""Initialization

This file contains the application factory for the acdumo app.
"""




# Imports ======================================================================

import os

from flask import Flask, render_template
from flask_login import login_required




# Functions ====================================================================

def create_app(test_config=None, configure_scheduler=True):
    """The application factory function

    This function creates and configures the Flask application object. For
    more on application factories, see the Flask documentation/tutorial:

    http://flask.pocoo.org/docs/1.0/tutorial/factory/

    http://flask.pocoo.org/docs/1.0/patterns/appfactories/

    Parameters
    ----------
    test_config : dict
        A dictionary containing configuration parameters for use during unit
        testing. If this parameter is `None`, the configuration will be loaded
        from `config.py` in the instance folder.

    Returns
    -------
    Flask
        A flask app
    """

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from acdumo.models import db, migrate
    from acdumo.login import login
    from acdumo.email import mail
    from acdumo.errors import forbidden
    from acdumo.misaka import md
    for ext in db, login, mail, md:
        ext.init_app(app)
    migrate.init_app(app, db)
    login.login_view = 'auth.login'

    if configure_scheduler:
        from acdumo.apscheduler import scheduler
        scheduler.init_app(app)
        scheduler.start()

    for error, handler in ((403, forbidden),):
        app.register_error_handler(403, forbidden)
    
    from acdumo import auth, strategy, protected, settings
    for bp in auth.bp, strategy.bp, protected.bp, settings.bp:
        app.register_blueprint(bp)
    
    app.add_url_rule('/', endpoint='auth.login')
    
    return app
