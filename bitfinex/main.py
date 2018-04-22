import json
import logging
import time

import click
import pendulum

from db import SqliteDatabase
from utils import date_range, get_data

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

API_URL = 'https://api.bitfinex.com/v2'


def symbol_start_date(symbol):
    """
    Return the datetime when `symbol` first started trading.
    """
    with open('symbols_trading_start_days.json') as f:
        data = json.load(f)

    # objects are timestamps with milliseconds, divide
    # by 1000 to remove milliseconds
    return pendulum.from_timestamp(int(data[symbol])/1000)


def get_symbols():
    """
    Return the symbols that are being traded on Bitfinex.

    This is taken from APIv1 as v2 doesn't have this endpoint.
    https://bitfinex.readme.io/v1/reference#rest-public-symbols

    Note: APIv1 returns symbol names in lowercase ('btcusd') but
    APIv2 endpoints require them in uppercase ('BTCUSD')
    """
    with open('symbols.json') as f:
        return json.load(f)


def get_candles(symbol, start_date, end_date, timeframe='1m', limit=1000):
    """
    Return symbol candles between two dates.
    https://docs.bitfinex.com/v2/reference#rest-public-candles
    """
    # timestamps need to include milliseconds
    start_date = start_date.int_timestamp * 1000
    end_date = end_date.int_timestamp * 1000

    url = f'{API_URL}/candles/trade:{timeframe}:t{symbol.upper()}/hist' \
          f'?start={start_date}&end={end_date}&limit={limit}'
    data = get_data(url)
    return data


@click.command()
@click.argument('db_path', default='bitfinex.sqlite3',
                type=click.Path(resolve_path=True))
@click.option('--debug', is_flag=True, help='Set debug mode')
def main(db_path, debug):
    if debug:
        logger.setLevel(logging.DEBUG)

    db = SqliteDatabase(path=db_path)
    end_date = pendulum.now()
    step = pendulum.Interval(minutes=1000)

    symbols = get_symbols()
    logging.info(f'Found {len(symbols)} symbols')
    for i, symbol in enumerate(symbols, 1):
        # get start date for symbol
        # this is either the last entry from the db
        # or the trading start date (from json file)
        latest_candle_date = db.get_latest_candle_date(symbol)
        if latest_candle_date is None:
            logging.debug('No previous entries in db. Starting from scratch')
            # TODO: handle case when symbol is missing from trading start days
            # e.g. symbol is in symbols.json but not in symbols_trading_start_days.json
            start_date = symbol_start_date(symbol)
        else:
            logging.debug('Found previous db entries. Resuming from latest')
            start_date = latest_candle_date

        logging.info(f'{i}/{len(symbols)} | {symbol} | Processing from {start_date.to_datetime_string()}')
        for d1, d2 in date_range(start_date, end_date, step):
            logging.debug(f'{d1} -> {d2}')
            # returns (max) 1000 candles, one for every minute
            candles = get_candles(symbol, d1, d2)
            logging.debug(f'Fetched {len(candles)} candles')
            if candles:
                db.insert_candles(symbol, candles)

            # prevent from api rate-limiting
            time.sleep(3)
    db.close()


if __name__ == '__main__':
    main()
