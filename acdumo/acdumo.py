#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

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

def download_historical_price_data(date, *tickers, freq='monthly'):
    yahoo_financials = YahooFinancials(tickers)
    historical_price_data = yahoo_financials.get_historical_price_data(
        (date - timedelta(days={'monthly': 217, 'weekly': 186}[freq])).strftime(
            '%Y-%m-%d'
        ),
        date.strftime('%Y-%m-%d'),
        freq
    )
    return {
        ticker: pd.DataFrame(
            historical_price_data[ticker]['prices'][::-1]
        ).dropna()
        for ticker in tickers
    }


def plot_prices(historical_price_data, file_name):
    hpd = pd.concat(
        df.assign(
            normalized_adjclose=df.adjclose / df.adjclose.iloc[-1],
            ticker=[ticker] * len(df.index)
        )[['formatted_date', 'normalized_adjclose', 'ticker']]
        for ticker, df in historical_price_data.items()
    )
    ax = sns.lineplot(
        x='formatted_date',
        y='normalized_adjclose',
        hue='ticker',
        data=hpd
    )
    ax.set_xlabel('')
    ax.set_ylabel(f'Price relative to {hpd.formatted_date.iloc[-1]}')
    ax.set_xticklabels(labels=hpd.formatted_date[::-1], rotation=30)
    if len(ax.get_xticklabels()) > 7:
        for ind, label in enumerate(ax.get_xticklabels()):
            if ind % 4 == 0:
                label.set_visible(True)
            else:
                label.set_visible(False)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(file_name, format=file_name.split('.')[-1])


def compute_signal(df, freq='monthly'):
    if freq == 'monthly':
        return sum(df.adjclose[0] / df.adjclose[x] - 1 for x in (1, 3, 6))
    elif freq == 'weekly':
        current_month_price = statistics.mean(df.adjclose[:4])
        return sum(
            current_month_price / statistics.mean(df.adjclose[x:x+4]) - 1
            for x in (4, 12, 24)
        )


def compute_signals(historical_price_data, freq='monthly'):
    return {
        ticker: compute_signal(df, freq=freq)
        for ticker, df in historical_price_data.items()
    }


def decide_strategy(signals: dict, bonds: str = BONDS):
    signals_sans_bonds = dict((t, s) for t, s in signals.items() if t != bonds)
    if any(s > 0 for s in signals_sans_bonds.values()):
        choice = max(signals_sans_bonds.items(), key=itemgetter(1))[0]
    else:
        choice = bonds
    return f'Buy/Hold {choice}'


def generate_report(date, signals: dict, strategy: str):
    return REPORT.format(
        date.strftime('%Y-%m-%d'),
        '\n'.join(f'|    {t} | {s:.4f} |' for t, s in signals.items()),
        strategy
    )


def parse_arguments():
    parser = ArgumentParser(description='Accelerated dual momentum')
    parser.add_argument(
        'report_dir',
        metavar='<path/to/report/dir/>',
        nargs='?',
        help='write a HTML report'
    )
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
        '--frequency',
        choices=('monthly', 'weekly'),
        default='monthly',
        help='frequency of data to fetch (default: monthly)'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    date = datetime.strptime(args.date, '%Y-%m-%d')
    if date > datetime.today():
        raise RuntimeError(
            "I can't predict the future! Choose an earlier date."
        )
    historical_price_data = download_historical_price_data(
        date, *args.tickers, freq=args.frequency
    )
    signals = compute_signals(historical_price_data, freq=args.frequency)
    strategy = decide_strategy(signals, bonds=args.bonds)
    report_text = generate_report(date, signals, strategy)
    print(report_text, end='')
    if args.report_dir:
        if not os.path.isdir(args.report_dir):
            os.mkdir(args.report_dir)
        for ticker, df in historical_price_data.items():
            df.to_csv(
                os.path.join(args.report_dir, f'{ticker}.csv'),
                index=False
            )
        plot_prices(
            historical_price_data, os.path.join(args.report_dir, 'prices.svg')
        )
        with open(os.path.join(args.report_dir, 'acdumo.html'), 'w') as f:
            f.write(m.html(report_text, extensions=['tables']))




# Execute ======================================================================

if __name__ == '__main__':
    main()
