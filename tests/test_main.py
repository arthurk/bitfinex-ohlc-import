import json
from unittest.mock import mock_open, patch

import pendulum
from bitfinex.main import API_URL, get_candles, get_symbols, symbol_start_date


def test_get_candles():
    """
    Get all candles for symbol between two dates.
    """
    symbol = 'BTCUSD'
    start_date = pendulum.parse('2018-01-01 00:00:00')
    end_date = pendulum.parse('2018-01-01 00:02:00')
    with open('fixture_get_candles.json') as f:
        data = json.load(f)
    url = API_URL + '/candles/trade:1m:tBTCUSD/hist' \
                    '?start=1514764800000&end=1514764920000&limit=1000'

    with patch('bitfinex.main.get_data') as mock_get_data:
        mock_get_data.return_value = data
        result = get_candles(symbol, start_date, end_date)

    mock_get_data.assert_called_once_with(url)
    assert result == data


def test_trading_start_date():
    """
    Test that a datetime object is returned with the first
    trading day of the symbol
    """
    # content of "symbols_trading_start_days.json"
    file_content = """{
      "btcusd": "1431388800000",
      "ltcusd": "1431388800000",
      "ltcbtc": "1431388800000"
    }
    """
    m = mock_open(read_data=file_content)
    with patch('bitfinex.main.open', m):
        date = symbol_start_date(symbol='btcusd')

    m.assert_called_once_with('symbols_trading_start_days.json')
    assert date == pendulum.create(2015, 5, 12)


def test_get_symbols(symbols_fixture):
    """
    Should return a json of all available markets
    """
    # content of "symbols.json"
    json_data = '["btcusd", "ltcbtc", "ethusd"]'
    m = mock_open(read_data=json_data)
    with patch('bitfinex.main.open', m):
        symbols = get_symbols()

    # should read symbols.json file and return json
    m.assert_called_once_with('symbols.json')
    assert symbols == symbols_fixture
