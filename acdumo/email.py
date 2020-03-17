#===============================================================================
# email.py
#===============================================================================

"""Instantiation of the Mail object, along with helper functions for email
handling

Attributes
----------
mail : Mail
    A Mail object (see Flask-Mail: https://pythonhosted.org/Flask-Mail/ )
"""




# Imports ======================================================================

from flask import render_template, current_app
from flask_mail import Mail, Message
from threading import Thread

from acdumo import create_app





# Initialization ===============================================================

mail = Mail()




# Functions ====================================================================

def send_async_email(app, msg):
    """Send an email asynchronously

    An application context is pushed so that the mail operation can use its own
    thread. See the Flask documentation for more on application contexts:

    http://flask.pocoo.org/docs/1.0/appcontext/

    Parameters
    ----------
    app : Flask
        The application from which to push a context
    msg : Message
        The message to be sent
    """

    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """Send an email

    A Message object is instantiated using the provided subject, sender and
    recippients, then filled using the provided text/html data. A new app is
    created to support sending mail asynchrounously, and finally
    send_async_email is called with its own thread.

    Parameters
    ----------
    subject
        The subject of the email
    sender
        The sender of the email
    recipients
        The recipients of the email
    text_body
        The body of the email (text version)
    html_body
        The body of the email (html version)
    """

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    app = create_app(configure_scheduler=False)
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    """Send a password reset email

    A JSON web token is created, then included in an email to the account for
    which a password reset has been requested.

    Parameters
    ----------
    user : User
        User whose password is to be reset
    """

    token = user.get_reset_password_token()
    send_email(
        '[acdumo] Reset Your Password',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template(
            'email/reset_password.txt',
            user=user,
            token=token
        ),
        html_body=render_template(
            'email/reset_password.html',
            user=user,
            token=token
        )
    )


def send_confirmation_email(user):
    """Send a confirmation email

    A JSON web token is created, then included in an email to the account for
    which the email is to be confirmed

    Parameters
    ----------
    user : User
        The user whose email is to be confirmed
    """

    token = user.get_confirm_email_token()
    send_email(
        '[acdumo] Confirm Your Email Address',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template(
            'email/email_confirmation.txt',
            user=user,
            token=token
        ),
        html_body=render_template(
            'email/email_confirmation.html',
            user=user,
            token=token
        )
    )


def send_notification_email(user, date, report, alert):
    """Send a password reset email

    An email with a signal update is sent

    Parameters
    ----------
    user : User
        User to whom email will be sent
    date
        date for the report
    report
        report to send
    """

    send_email(
        '[acdumo] signal notification',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template(
            'email/notification.txt',
            date=date,
            report=report,
            alert=alert
        ),
        html_body=render_template(
            'email/notification.html',
            date=date,
            report=report,
            alert=alert
        )
    )
