#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

import json
import misaka as m
import os
import pandas as pd
import statistics
import seaborn as sns

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

Prices
======
![prices plot](prices.svg)

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
    return {
        ticker: pd.DataFrame(historical_price_data[ticker]['prices'][::-1])[[
            'adjclose', 'date', 'formatted_date'
        ]]
        for ticker in tickers
    }


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


def compute_signals(historical_price_data):
    return {
        ticker: compute_signal(df)
        for ticker, df in historical_price_data.items()
    }


def plot_prices(historical_price_data, file_name):
    hpd = pd.concat(
        df.assign(
            ticker=[ticker] * len(df.index),
            normalized_adjclose=df.adjclose / df.adjclose.iloc[-1]
        )
        for ticker, df in historical_price_data.items()
    )
    ax = sns.lineplot(x='date', y='normalized_adjclose', hue='ticker', data=hpd)
    ax.set_xticklabels(labels=hpd.formatted_date, rotation=30)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(file_name, format=file_name.split('.')[-1])


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
    historical_price_data = download_historical_price_data(date, *args.tickers)
    signals = compute_signals(historical_price_data)
    strategy = decide_strategy(signals, bonds=args.bonds)
    if args.report:
        report = report_md(date, signals, strategy)
        if not os.path.isdir(args.report):
            os.mkdir(args.report)
        plot_prices(
            historical_price_data,
            os.path.join(args.report, 'prices.svg')
        )
        with open(os.path.join(args.report, 'acdumo.html'), 'w') as f:
            f.write(m.html(report, extensions=['tables']))
    if args.json:
        report = report_dict(date, signals, strategy)
        emit_json(report)
    else:
        report = report_md(date, signals, strategy)
        print(report, end='')




# Execute ======================================================================

if __name__ == '__main__':
    main()
