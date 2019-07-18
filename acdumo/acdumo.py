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
        )
    )
    headers = {'Cookie': cookie}
    req = Request(ticker_url, headers=headers)
    with urlopen(req) as response:
        return response.read().decode()


def main():
    parse_arguments()
    cookie, crumb, valid_cookie_crumb = get_cookie_crumb()
    result_from_yahoo = get_yahoo_finance_data('SPY', cookie, crumb)
    print(result_from_yahoo)

if __name__ == '__main__':
    main()
