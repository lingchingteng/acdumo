#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

import pandas as pd
import statistics

from argparse import ArgumentParser
from datetime import datetime, timedelta
from yahoofinancials import YahooFinancials




# Constants ====================================================================

TICKERS = ('SPY', 'TLT', 'VSS', 'SCZ')



# Functions ====================================================================

def download_historical_price_data(*tickers):
    today = datetime.today()
    yahoo_financials = YahooFinancials(tickers)
    historical_price_data = yahoo_financials.get_historical_price_data(
        (today - timedelta(days=186)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        'weekly'
    )
    yield from (
        pd.DataFrame(historical_price_data[ticker]['prices'][::-1])
        for ticker in tickers
    )


def compute_signal(df):
    current_month_price = statistics.mean(
        p for p in df['adjclose'][:4] if not pd.isnull(p)
    )
    return sum(
        current_month_price / statistics.mean(
            p for p in df['adjclose'][x:x+4] if not pd.isnull(p)
        )
        for x in (4, 12, 24)
    )


def decide_strategy(spy_signal, global_small_stocks_signal):
    if spy_signal > global_small_stocks_signal:
        if spy_signal > 0:
            return 'Buy/Hold S&P 500'
        else:
            return 'Buy/Hold Long-Term Treasuries'
    else:
        if global_small_stocks_signal > 0:
            return 'Buy/Hold Global Small Stocks'
        else:
            return 'Buy/Hold Long-Term Treasuries'


def parse_arguments():
    parser = ArgumentParser(description='Accelerated dual momentum')
    parser.add_argument(
        '--tickers',
        nargs=4,
        default=TICKERS,
        help='list of four tickers'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    spy, tlt, vss, scz = download_historical_price_data(*args.tickers)
    print('\nSIGNALS\n-------')
    for ticker, df in zip(args.tickers, (spy, tlt, vss, scz)):
        print(f'{ticker}: {compute_signal(df)}')
    print('\nSTRATEGY\n-------')
    print(decide_strategy(compute_signal(spy), compute_signal(vss)))



if __name__ == '__main__':
    main()
