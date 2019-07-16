#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

import re

from argparse import ArgumentParser
from datetime import datetime
from urllib.request import Request, urlopen




# Constants ====================================================================

TICKERS = ('SPY', 'TLT', 'VSS', 'SCZ')




# Functions ====================================================================

def parse_arguments():
    parser = ArgumentParser(description='Accelerated dual momentum')
    return parser.parse_args()


def get_cookie_crumb():
    url = 'https://finance.yahoo.com/lookup?s=bananas'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    req = Request(url, headers=headers)
    with urlopen(req) as response:
        cookie = response.info()['set-cookie'].split(';')[0]
        response_text = response.read().decode()
        crumb_start = tuple(
            m.end() for m in re.finditer('"crumb":"', response_text)
        )[-1]
        crumb = response_text[crumb_start:crumb_start + 11]
        return cookie, crumb, (len(crumb) == 11)


def get_yahoo_finance_data(
    stock_ticker: str,
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
