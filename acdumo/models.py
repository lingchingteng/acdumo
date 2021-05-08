#===============================================================================
# models.py
#===============================================================================

"""Databse models

Attributes
----------
db : SQLAlchemy
    The database object (see Flask-SQLAlchemy:
    http://flask-sqlalchemy.pocoo.org/2.3/ )
migrate : Migrate
    The Migrate object (see Flask-Migrate:
    https://flask-migrate.readthedocs.io/en/latest/ )
"""




# Imports ======================================================================

import jwt

from time import time
from datetime import datetime
from flask import g, current_app
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash




# Database initialization ======================================================

db = SQLAlchemy()
migrate = Migrate()




# Classes ======================================================================

# Models -----------------------------------------------------------------------



class User(UserMixin, db.Model):
    """A user

    Attributes
    ----------
    id : int
    username : str
    email : str
    password_hash : str
    email_confirmation_sent_on : datetime
    email_confirmed : bool
    email_confirmed_on : datetime
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email_confirmation_sent_on = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, default=False, nullable=True)
    email_confirmed_on = db.Column(db.DateTime, nullable=True)
    subscribed = db.Column(db.Boolean, default=False, nullable=True)

    def __repr__(self):
        """String representation of the user
        
        Returns
        -------
        str
            String representation of the user
        """

        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set the user's password

        Parameters
        ----------
        password : str
            The password to hash
        """

        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check the provided password against the user's database record
        
        Parameters
        ----------
        password : str
            The provided password
        
        Returns
        -------
        bool
            The result of the hash check
        """

        return check_password_hash(self.password_hash, password)
    
    def get_confirm_email_token(self, expires_in=600):
        """Generate an email confirmation token

        Parameters
        ----------
        expires_in : int
            The lifetime of the token in seconds
        
        Returns
        -------
        bytes
            The token
        """

        return (
            jwt.encode(
                {'confirm_email': self.id, 'exp': time() + expires_in},
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        )
    
    @staticmethod
    def verify_confirm_email_token(token):
        """Verify an email confirmation token

        Parameters
        ----------
        token
            The token to be verified
        
        Returns
        -------
        User or None
            The user corresponding to the token if it is successfully verified,
            otherwise None.
        """
        
        try:
            id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['confirm_email']
        except:
            return
        return User.query.get(id)
    
    def get_reset_password_token(self, expires_in=600):
        """Generate a password reset token

        Parameters
        ----------
        expires_in : int
            The lifetime of the token in seconds
        
        Returns
        -------
        bytes
            The token
        """

        return (
            jwt.encode(
                {'reset_password': self.id, 'exp': time() + expires_in},
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            .decode('utf-8')
        )

    @staticmethod
    def verify_reset_password_token(token):
        """Verify a password reset token

        Parameters
        ----------
        token
            The token to be verified
        
        Returns
        -------
        User or None
            The user corresponding to the token if it is successfully verified,
            otherwise None.
        """

        try:
            id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['reset_password']
        except:
            return
        return User.query.get(id)




# Functions ====================================================================

def get_db():
    """Retrieve the database from the application context
    
    Returns
    -------
    SQLAlchemy
        The database object
    """

    if 'db' not in g:
        g.db = db
    return g.db
