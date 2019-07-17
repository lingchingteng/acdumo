#===============================================================================
# acdumo.py
#===============================================================================

# Imports ======================================================================

from argparse import ArgumentParser
from datetime import datetime, timedelta
from urllib.request import urlopen
from yahoofinancials import YahooFinancials




# Constants ====================================================================

TICKERS = ('SPY', 'TLT', 'VSS', 'SCZ')



# Functions ====================================================================

def download_data(*tickers):
    today = datetime.today()
    yahoo_financials = YahooFinancials(tickers)
    return yahoo_financials.get_historical_price_data(
        (today - timedelta(days=186)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        'monthly'
    )
    


def parse_arguments():
    parser = ArgumentParser(description='Accelerated dual momentum')
    return parser.parse_args()


def main():
    parse_arguments()


if __name__ == '__main__':
    main()
