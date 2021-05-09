#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

import matplotlib; matplotlib.use('agg')
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

TICKERS = ['SPY', 'TLT', 'VSS', 'SCZ']
BONDS = 'TLT'
REPORT = """Date
====
{date}

Prices
======
![prices plot](prices.svg)

One Month Returns
=================
| Ticker | Return |
| ------ | ------ |
{returns}

Signals
=======
| Ticker | Signal |
| ------ | ------ |
{signals}

Strategy
========
{strategy}
"""




# Functions ====================================================================

def download_historical_price_data(date, *tickers, freq: str = 'monthly'):
    yahoo_financials = YahooFinancials(tickers)
    if freq == 'monthly':
        days = 217
    elif freq == 'weekly':
        days = 186

    def download_into_dfs(buffer=0):
        historical_price_data = yahoo_financials.get_historical_price_data(
            (date - timedelta(days=days)).strftime('%Y-%m-%d'),
            (date + timedelta(days=buffer)).strftime('%Y-%m-%d'),
            freq
        )
        return [
            pd.DataFrame(historical_price_data[ticker]['prices'][::-1])
            for ticker in tickers
        ]

    dfs = download_into_dfs()
    if freq == 'monthly':
        buffer = 0
        while date.strftime('%Y-%m-01') not in set(dfs[0].formatted_date):
            buffer += 1
            dfs = download_into_dfs(buffer=buffer)
    elif freq == 'weekly':
        dfs = [df.drop(0) for df in dfs]
    return {
        ticker: (
            df[
                [
                    d.endswith('-01') if freq == 'monthly' else True
                    for d in df.formatted_date
                ]
            ]
            .reset_index().dropna()
        )
        for ticker, df in zip(tickers, dfs)
    }


def plot_prices(historical_price_data: dict, file_name: str):
    hpd = pd.concat(
        df.assign(
            normalized_adjclose=df.adjclose / df.adjclose.iloc[-1],
            ticker=[ticker] * len(df.index)
        )[['formatted_date', 'normalized_adjclose', 'ticker']]
        for ticker, df in reversed(tuple(historical_price_data.items()))
    )
    ax = sns.lineplot(
        x='formatted_date',
        y='normalized_adjclose',
        hue='ticker',
        data=hpd[::-1]
    )
    ax.set_xlabel('')
    ax.set_ylabel(f'adjclose relative to {hpd.formatted_date.iloc[-1]}')
    ax.set_xticklabels(labels=hpd.formatted_date[::-1], rotation=30, ha='right')
    if len(ax.get_xticklabels()) > 8:
        for ind, label in enumerate(ax.get_xticklabels()):
            if ind % 4 == 0:
                label.set_visible(True)
            else:
                label.set_visible(False)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(file_name, format='svg')
    fig.clf()


def compute_one_month_return(df, freq: str = 'monthly'):
    if freq == 'monthly':
        return df.adjclose[0] / df.adjclose[1] - 1
    elif freq == 'weekly':
        return (
            df.adjclose[0] / df.adjclose[4] - 1
        )


def compute_one_month_returns(
    historical_price_data: dict,
    freq: str = 'monthly'
):
    return {
        ticker: compute_one_month_return(df, freq=freq)
        for ticker, df in historical_price_data.items()
    }


def compute_signal(df, freq: str = 'monthly'):
    if freq == 'monthly':
        return sum(df.adjclose[0] / df.adjclose[x] - 1 for x in (1, 3, 6))
    elif freq == 'weekly':
        current_month_price = df.adjclose[0]
        return sum(
            current_month_price / df.adjclose[x] - 1
            for x in (4, 12, 24)
        )


def compute_signals(historical_price_data: dict, freq: str = 'monthly'):
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


def generate_report(date, returns: dict, signals: dict, strategy: str):
    return REPORT.format(
        date=date.strftime('%Y-%m-%d'),
        returns='\n'.join(
            f'|    {t} | {s*100:.3}% |' for t, s in returns.items()
        ),
        signals='\n'.join(
            f'|    {t} | {s*100:.4}% |' for t, s in signals.items()
        ),
        strategy=strategy
    )


def parse_arguments():
    parser = ArgumentParser(description='Accelerated Dual Momentum')
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
    returns = compute_one_month_returns(
        historical_price_data, freq=args.frequency
    )
    signals = compute_signals(historical_price_data, freq=args.frequency)
    strategy = decide_strategy(signals, bonds=args.bonds)
    report_text = generate_report(date, returns, signals, strategy)
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
            historical_price_data,
            os.path.join(args.report_dir, 'prices.svg')
        )
        with open(os.path.join(args.report_dir, 'acdumo.html'), 'w') as f:
            f.write(m.html(report_text, extensions=['tables']))




# Execute ======================================================================

if __name__ == '__main__':
    main()
