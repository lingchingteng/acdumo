#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

from argparse import ArgumentParser
from datetime import datetime
from urllib.request import urlopen




# Constants ====================================================================

TICKERS = ('SPY', 'TLT', 'VSS', 'SCZ')



# Functions ====================================================================

def parse_arguments():
    parser = ArgumentParser(description='Accelerated dual momentum')
    return parser.parse_args()


def get_cookie_crumb()


def get_yahoo_finance_data(
    stock_ticker: str,
    cookie: str,
    crumb: str,
    start_date: str = '1929-03-08',
    end_date: str = datetime.now().strftime('%Y-%m-%d'),
    frequency: str = 'd'
):
    ticker_url = ''.join(
        (
            'https://query1.finance.yahoo.com/v7/finance/download/',
            stock_ticker,
            '?period1=', start_date,
            '&period2=', end_date,
            '&interval=', frequency,
            '&events=history',
            '&crumb=', crumb
        )
    )
    with urlopen(ticker_url) as response:
        return response.read().decode()


def main():
    parse_arguments()
    result_from_yahoo = get_yahoo_finance_data('SPY')
    print(result_from_yahoo)

if __name__ == '__main__':
    main()
