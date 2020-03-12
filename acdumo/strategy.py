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

import os.path

from datetime import datetime
from flask import (
    Blueprint, render_template, current_app, url_for, redirect, request
)
from flask_login import login_required

from acdumo.forms import StrategyForm
from acdumo.acdumo import (
    TICKERS, BONDS, download_historical_price_data, compute_one_month_returns,
    compute_signals, decide_strategy, plot_prices
)



# Blueprint assignment =========================================================

bp = Blueprint('strategy', __name__)




# Constants ====================================================================

REPORT = """Date
----
{date}

Strategy
--------
{strategy}

Signals
-------
| Ticker | Signal |
| ------ | ------ |
{signals}

One Month Returns
-----------------
| Ticker | Return |
| ------ | ------ |
{returns}

Prices
------
![prices plot]({prices_svg})

CSV Data
--------
{csv_links}
"""




# Functions ====================================================================


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    f"""Render the strategy index"""

    form = StrategyForm()
    if form.validate_on_submit():
        return redirect(
            url_for(
                'strategy.index',
                date=form.date.data,
                tickers=form.tickers.data
            )
        )

    date = datetime.strptime(
        request.args.get('date', datetime.today().strftime('%Y-%m-%d')),
        '%Y-%m-%d'
    )
    tickers = request.args.get('tickers', ' '.join(TICKERS)).split()

    hpd = download_historical_price_data(date, *tickers, freq='weekly')
    plot_prices(
        hpd,
        os.path.join(current_app.config['PROTECTED_DIR'], f"prices-{'-'.join(tickers)}-{date.strftime('%Y-%m-%d')}.svg")
    )
    returns = compute_one_month_returns(hpd, freq='weekly')
    signals = compute_signals(hpd, freq='weekly')
    strategy = decide_strategy(signals, bonds=BONDS)
    formatted_date = date.strftime('%Y-%m-%d')
    for ticker, df in hpd.items():
        df.to_csv(
            os.path.join(current_app.config['PROTECTED_DIR'], f"{ticker}-{formatted_date}.csv"),
            index=False
        )
    return render_template(
        'strategy/index.html',
        report=REPORT.format(
            date=formatted_date,
            strategy=strategy,
            signals='\n'.join(
                f'|    {t} | {s*100:.4}% |' for t, s in signals.items()
            ),
            returns='\n'.join(
                f'|    {t} | {s*100:.3}% |' for t, s in returns.items()
            ),
            prices_svg=url_for(
                'protected.protected',
                filename=f"prices-{'-'.join(tickers)}-{formatted_date}.svg"
            ),
            csv_links='\n'.join(
                f"<a href=\"{url_for('protected.protected',filename=f'{ticker}-{formatted_date}.csv')}\" class='btn btn-outline-primary'>{ticker}</a>"
                for ticker in tickers
            )
        ),
        form=form,
        date=formatted_date,
        tickers=' '.join(tickers)
    )
