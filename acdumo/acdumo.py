#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

<<<<<<< HEAD
import re

from argparse import ArgumentParser
from datetime import datetime
from urllib.request import Request, urlopen
=======
import pandas as pd
import statistics

from argparse import ArgumentParser
from datetime import datetime, timedelta
from yahoofinancials import YahooFinancials
>>>>>>> 5795ffc44253c21c70fdcf541017862ffcf8bcac




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


<<<<<<< HEAD
def get_cookie_crumb(index=1):
    url = 'https://finance.yahoo.com/lookup?s=bananas'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    req = Request(url, headers=headers)
    with urlopen(req) as response:
        cookie = response.info()['Set-Cookie'].split(';')[0]
        response_text = response.read().decode()
        crumb_start = tuple(
            m.end() for m in re.finditer('"crumb":"', response_text)
        )[index]
        crumb = response_text[crumb_start:crumb_start + 11]
        print(crumb)
        return cookie, crumb, (len(crumb) == 11)


def get_yahoo_finance_data(
    stock_ticker: str,
    crumb_index=8,
    # cookie: str,
    # crumb: str,
    start_date: str = '1929-03-08',
    end_date: str = datetime.now().strftime('%Y-%m-%d'),
    frequency: str = 'd'
):
    cookie, crumb, _ = get_cookie_crumb(index=crumb_index)
    ticker_url = ''.join(
        (
            'https://query1.finance.yahoo.com/v7/finance/download/',
            stock_ticker,
            '?period1=', start_date,
            '&period2=', end_date,
            '&interval=', frequency,
            '&events=history',
            '&crumb=', crumb
=======
def compute_signal(df):
    current_month_price = statistics.mean(
        p for p in df['adjclose'][:4] if not pd.isnull(p)
    )
    return sum(
        current_month_price / statistics.mean(
            p for p in df['adjclose'][x:x+4] if not pd.isnull(p)
>>>>>>> 5795ffc44253c21c70fdcf541017862ffcf8bcac
        )
        for x in (4, 12, 24)
    )
<<<<<<< HEAD
    headers = {'Cookie': cookie}
    req = Request(ticker_url, headers=headers)
    with urlopen(req) as response:
        return response.read().decode()


def main():
    parse_arguments()
    cookie, crumb, valid_cookie_crumb = get_cookie_crumb()
    result_from_yahoo = get_yahoo_finance_data('SPY', cookie, crumb)
    print(result_from_yahoo)
=======


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

>>>>>>> 5795ffc44253c21c70fdcf541017862ffcf8bcac

if __name__ == '__main__':
    main()
