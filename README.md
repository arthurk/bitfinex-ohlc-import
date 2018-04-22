## bitfinex-ohlc-import

A script that imports all historical OHLC data from the Bitfinex API and stores it in a local database.

The data has a 1-minute interval and can be used to carry out further in-depth analysis of market trends or backtest trading bots.

All currently traded symbols (e.g. BTC-USD, ETH-USD, ...) are supported (check `symbols.json` for a list of them). The import will begin from the earliest trading date (defined in `symbols_trading_start_days.json`). The script can be invoked periodically (for example with a cronjob) to fetch the latest data. It will automatically resume from the latest saved date.

API rate limits are respected and will not be exceeded. The script will re-try fetching with an incremental backoff time and continue to the next symbol after 3 failed attempts.

Experimental support for the Websocket API is also available. It currently subscribes to all trading updates (buy/sell) but does not store that data.

## Installation

The script can be run in a virtualenv (via pipenv) or by using the Docker. For local development the virtualenv is recommended. For production deployments the Docker image is recommended.

### virtualenv (pipenv)

You need the `sqlite3` library installed on your system. On macOS you can use homebrew: `brew install sqlite3`.

To install the development environment, clone the repo and run:

    $ pipenv install --dev

The `--dev` flag will install development tools such as `py.test`.

### Docker

You can build the Docker image with:

    $ docker build -t bitfinex .

The Docker image will not install development tools such as `py.test`.

## Usage

You can run the script with the following command:

    $ pipenv run python bitfinex/main.py --debug

Or if you prefer Docker:

    $ docker run --rm bitfinex python bitfinex/main.py --debug

The `--debug` flag will print detailed information for each request/response, which is very useful for debugging.

    $ pipenv run python bitfinex/main.py --debug
	2018-04-22 20:48:49,326 INFO     Found 105 symbols
	2018-04-22 20:48:49,326 DEBUG    Found previous db entries. Resuming from latest
	2018-04-22 20:48:49,327 INFO     1/105 | btcusd | Processing from 2013-04-20 02:59:00
	2018-04-22 20:48:49,328 DEBUG    2013-04-20T02:59:00+00:00 -> 2013-04-20T19:39:00+00:00
	2018-04-22 20:48:49,399 DEBUG    Starting new HTTPS connection (1): api.bitfinex.com
	2018-04-22 20:48:49,624 DEBUG    https://api.bitfinex.com:443 "GET /v2/candles/trade:1m:tBTCUSD/hist?start=1366426740000&end=1366486740000&limit=1000 HTTP/1.1" 200 None
	2018-04-22 20:48:49,633 DEBUG    Fetched 288 candles

The script will import OHLC data for all symbols defined in the `symbols.json` file. If the import is started for the first time, the date defined in `symbols_trading_start_days.json` will be used as a starting point. Otherwise the database is queried for the last date and the import will continue from there on.

The data is saved in a file called `bitfinex.sqlite3` in the same directory as the script. You can change it by passing it as an argument:

    $ pipenv run python bitfinex/main.py /path/to/my/db.sqlite3

## Database schema

The data is stored in a Sqlite3 database and has a `"candles"` table with the following structure:

    symbol (the trading symbol e.g. btcusd)
    time (time in unix timestamp with milliseconds added)
    open
    close
    high
    low
    volume

Example output:

    $ sqlite3 bitfinex.sqlite3
    sqlite> select * from candles;
    btcusd|1366366980000|122.7|122.4|122.7|122.4|1
    btcusd|1366366920000|123.2|122.7|123.2|122.7|82.9
    btcusd|1366366800000|123.7|123.7|123.7|123.7|1.1

## Export to CSV

The data can easily be exported to CSV:

    $ sqlite3 bitfinex.sqlite3
    sqlite> .headers on
    sqlite> .mode csv
    sqlite> .output data.csv
    sqlite> SELECT * FROM candles;
    sqlite> .quit

The data will be in a file called `data.csv`.

## Testing

You need to have development dependencies installed (`pipenv install --dev`). 

The tests are stored in the `tests` directory and can be run with py.test:

    $ pipenv run py.test tests/
