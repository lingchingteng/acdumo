# acdumo

This app is a simple implementation of the [Accelerated Dual Momentum](https://engineeredportfolio.com/2018/05/02/accelerating-dual-momentum-investing/) investment strategy. It
queries a Yahoo Finance API for historical ticker price data, calculates ADM
statistics, and suggests a strategy.

## Installation (command line)

For simple command line use of this app, you can install with pip:

```sh
pip3 install acdumo
```
or
```sh
pip3 install --user acdumo
```

Installation will require an extra step on macOS systems. Run the included `acdumo-install-certifi` command.

```sh
acdumo-install-certifi
```

## Usage (command line)

To generate a report for the current date, simply run:

```sh
acdumo
```

Optional arguments can be used to generate reports for different dates or
tickers:

```sh
acdumo --help
```

```
usage: acdumo [-h] [--date <yyyy-mm-dd>] [--tickers <TIC> [<TIC> ...]] [--bonds <TIC>] [--frequency {monthly,weekly}] [<path/to/report/dir/>]

Accelerated dual momentum

positional arguments:
  <path/to/report/dir/>
                        write a HTML report

optional arguments:
  -h, --help            show this help message and exit
  --date <yyyy-mm-dd>   date of interest (default: today)
  --tickers <TIC> [<TIC> ...]
                        tickers to use (default: SPY TLT VSS SCZ)
  --bonds <TIC>         ticker representing bonds (default: TLT)
  --frequency {monthly,weekly}
                        frequency of data to fetch (default: monthly)
```


## Installation (full app)

To run the app locally, use the following procedure. By default it is
configured to use a gmail account of your choice for account confirmation
emails. The gmail account must be configured to allow [less secure apps](https://support.google.com/accounts/answer/6010255?hl=en).

```sh
git clone https://github.com/anthony-aylward/acdumo.git
cd acdumo
python3 -m venv venv
source venv/bin/activate
pip3 install -e . # if on macOS, also run: python3 acdumo/install_certifi.py
export FLASK_APP=acdumo
export FLASK_ENV=development
mkdir -p instance/protected
python3 config/__init__.py --email <gmail address> instance/
flask db upgrade
flask run
```

You can then use a web browser to navigate to the app (by default at localhost:5000)
