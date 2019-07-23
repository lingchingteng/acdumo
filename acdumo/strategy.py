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
    Blueprint, render_template
)
from flask_login import login_required

from acdumo.acdumo import



# Blueprint assignment =========================================================

bp = Blueprint('strategy', __name__, url_prefix='/strategy')




# Constants ====================================================================

REPORT = """Date
----
2019-07-22

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
|    SPY | 4.51% |
|    TLT | 0.78% |
|    VSS | 2.94% |
|    SCZ | 1.24% |
{returns}

Prices
------
![prices plot]({prices_svg}})

"""




# Functions ====================================================================

@bp.route('/index')
@login_required
def index():
    f"""Render the strategy index"""

    return render_template(
        'strategy/index.html',
        report=REPORT
    )