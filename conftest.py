import pytest


@pytest.fixture
def symbols_fixture():
    # symbols for testing
    return [
      "btcusd",
      "ltcbtc",
      "ethusd"
    ]


def candles_fixture():
    return [[
        1518272040000,
        8791,
        8782.1,
        8795.8,
        8775.8,
        20.01209543
      ],
      [
        1518271980000,
        8768,
        8790.7,
        8791,
        8768,
        38.41333393
      ],
      [
        1518271920000,
        8757.3,
        8768,
        8770.6396831,
        8757.3,
        20.92449167
      ]]
