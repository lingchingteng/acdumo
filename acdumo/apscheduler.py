from flask import g
from datetime import datetime, timedelta
from flask_apscheduler import APScheduler
from acdumo import create_app
from acdumo.email import send_notification_email
from acdumo.models import get_db, User
from acdumo.acdumo import (
    TICKERS, BONDS, download_historical_price_data,
    compute_signals, decide_strategy, plot_prices
)

scheduler = APScheduler()

REPORT = """Date
====
{date}

Signals
=======
| Ticker | Signal |
| ------ | ------ |
{signals}

Strategy
========
{strategy}
"""


@scheduler.task(
    'cron',
    id='send_notification_email',
    minute='*',
    misfire_grace_time=900
)
def notification_email():
    date = datetime.today()
    hpd_yesterday = download_historical_price_data(date - timedelta(days=1), *TICKERS, freq='weekly')
    signals_yesterday = compute_signals(hpd_yesterday, freq='weekly')
    strategy_yesterday = decide_strategy(signals_yesterday, bonds=BONDS)
    hpd = download_historical_price_data(date, *TICKERS, freq='weekly')
    signals = compute_signals(hpd, freq='weekly')
    strategy = decide_strategy(signals, bonds=BONDS)
    formatted_date = datetime.today().strftime('%Y-%m-%d')
    signals_sans_bonds = dict((t, s) for t, s in signals.items() if t != BONDS)
    # if any(abs(signals[BONDS] - signals[s]) < 10 for s in signals_sans_bonds.keys()) or (strategy != strategy_yesterday):
    app = create_app(configure_scheduler=False)
    with app.app_context():
        db = get_db()
        for user in User.query.all():
            if user.subscribed:
                send_notification_email(
                    user,
                    formatted_date,
                    REPORT.format(
                        date=formatted_date,
                        signals='\n'.join(
                            f'|    {t} | {s*100:.4}% |' for t, s in signals.items()
                        ),
                        strategy=strategy
                    )
                )
