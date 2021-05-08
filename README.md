# acdumo

This app is a simple implementation of the [Accelerated Dual Momentum](https://engineeredportfolio.com/2018/05/02/accelerating-dual-momentum-investing/) investment strategy. It
queries a Yahoo Finance API for historical ticker price data, calculates ADM
statistics, and suggests a strategy.

## Installation (command line)

Install with pip:

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

```sh
acdumo
```


## Installation (full app)

To run the app locally:

```sh
git clone https://github.com/anthony-aylward/acdumo.git
cd acdumo
python3 -m venv venv
source venv/bin/activate
pip3 install -e . # if on macOS, also run: python3 acdumo/install_certifi.py
export FLASK_APP=acdumo
export FLASK_ENV=development
mkdir -p instance/protected
python3 config/__init__.py instance/
flask db upgrade
flask run
```