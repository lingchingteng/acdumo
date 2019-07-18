#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

import pandas as pd
import statistics

from argparse import ArgumentParser
from datetime import datetime, timedelta
from operator import itemgetter
from yahoofinancials import YahooFinancials




# Constants ====================================================================

TICKERS = ('SPY', 'VSS', 'SCZ', 'TLT')
BONDS = 'TLT'




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


def signals_dict(date, *tickers):
    return dict(
        zip(
            tickers,
            (
                compute_signal(df)
                for df in download_historical_price_data(date, *tickers)
            )
        )
    )


def decide_strategy(signals: dict):
    if any(s > 0 for s in signals.values()):
        choice = max(signals.items(), key=itemgetter(1))[0]
    else:
        choice = BONDS
    return f'Buy/Hold {choice}'


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
    return parser.parse_args()


def main():
    args = parse_arguments()
    date = datetime.strptime(args.date, '%Y-%m-%d')
    if date > datetime.today():
        raise RuntimeError(
            "I can't predict the future! Choose an earlier date."
        )
    signals = signals_dict(date, *args.tickers)
    print('\nDATE\n----')
    print(args.date)
    print('\nSIGNALS\n-------')
    for ticker, signal in signals.items():
        print(f'{ticker}: {signal}')
    print('\nSTRATEGY\n-------')
    print(decide_strategy(signals))


if __name__ == '__main__':
    main()
