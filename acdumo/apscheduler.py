from flask_apscheduler import APScheduler
from acdumo.email import send_notification_email

scheduler = APScheduler()

@scheduler.task(
    'cron',
    id='send_notification_email',
    minute='*',
    misfire_grace_time=900
)
def notification_email():
    send_notification_email()
