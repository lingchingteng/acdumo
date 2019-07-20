#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

import json
import misaka as m
import pandas as pd
import statistics

from argparse import ArgumentParser
from datetime import datetime, timedelta
from operator import itemgetter
from yahoofinancials import YahooFinancials




# Constants ====================================================================

TICKERS = ('SPY', 'TLT', 'VSS', 'SCZ')
BONDS = 'TLT'
REPORT = """Date
====
{}

Signals
=======
| Ticker | Signal |
| ------ | ------ |
{}

Strategy
========
{}
"""



# Functions ====================================================================

def download_historical_price_data(date, *tickers):
    yahoo_financials = YahooFinancials(tickers)
    historical_price_data = yahoo_financials.get_historical_price_data(
        (date - timedelta(days=186)).strftime('%Y-%m-%d'),
        date.strftime('%Y-%m-%d'),
        'weekly'
    )
    yield from (
        pd.DataFrame(historical_price_data[ticker]['prices'][::-1])
        for ticker in tickers
    )


def compute_signal(df):
    current_month_price = statistics.mean(
        p for p in df.adjclose[:4] if not pd.isnull(p)
    )
    return sum(
        current_month_price
        / statistics.mean(p for p in df.adjclose[x:x+4] if not pd.isnull(p))
        -1
        for x in (4, 12, 24)
    )


def compute_signals(date, *tickers):
    yield from zip(
        tickers,
        (
            compute_signal(df)
            for df in download_historical_price_data(date, *tickers)
        )
    )


def signals_dict(date, *tickers):
    return dict(compute_signals(date, *tickers))


def decide_strategy(signals: dict, bonds: str = BONDS):
    signals_sans_bonds = dict((t, s) for t, s in signals.items() if t != bonds)
    if any(s > 0 for s in signals_sans_bonds.values()):
        choice = max(signals_sans_bonds.items(), key=itemgetter(1))[0]
    else:
        choice = bonds
    return f'Buy/Hold {choice}'


def report_dict(date, signals: dict, strategy: str):
    return {
        'date': date.strftime('%Y-%m-%d'),
        'signals': signals,
        'strategy': strategy
    }

def report_md(date, signals: dict, strategy: str):
    return REPORT.format(
        date.strftime('%Y-%m-%d'),
        '\n'.join(f'|    {t} | {s:.4f} |' for t, s in signals.items()),
        strategy
    )


def emit_json(report: dict, indent=None):
    print(json.dumps(report, indent=indent), end='')


def parse_arguments():
    parser = ArgumentParser(description='Accelerated dual momentum')
    parser.add_argument(
        '--date',
        metavar='<yyyy-mm-dd>',
        default=datetime.today().strftime('%Y-%m-%d'),
        help=f'date of interest (default: today)'
    )
    parser.add_argument(
        '--tickers',
        metavar='<TIC>',
        nargs='+',
        default=TICKERS,
        help=f"tickers to use (default: {' '.join(TICKERS)})"
    )
    parser.add_argument(
        '--bonds',
        metavar='<TIC>',
        default=BONDS,
        help=f"ticker representing bonds (default: {BONDS})"
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='write JSON to stdout'
    )
    parser.add_argument(
        '--report',
        metavar='<path/to/report/dir/>',
        help='write a HTML report'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    date = datetime.strptime(args.date, '%Y-%m-%d')
    if date > datetime.today():
        raise RuntimeError(
            "I can't predict the future! Choose an earlier date."
        )
    signals = signals_dict(date, *args.tickers)
    strategy = decide_strategy(signals, bonds=args.bonds)
    if args.pdf:
        report = report_md(date, signals, strategy)
        pypandoc.convert_text(report, 'pdf', format='md', outputfile=args.pdf)
    if args.json:
        report = report_dict(date, signals, strategy)
        emit_json(report)
    else:
        report = report_md(date, signals, strategy)
        print(report, end='')




# Execute ======================================================================

if __name__ == '__main__':
    main()
