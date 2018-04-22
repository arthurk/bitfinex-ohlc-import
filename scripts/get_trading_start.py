"""
This script tries to find out when each symbol
started to trade.

It reduces the end date in steps until no data is returned,
which means that the previous step was the first trading period.
"""
import simplejson as json
from time import sleep
import requests
import pendulum

result = {}

end_date = pendulum.now()
limit = 1000
previous_data = None

with open('symbols.json') as f:
    symbols = json.load(f)

for symbol in symbols:
    print(f'Processing {symbol}')
    while True:
        # ts + milliseconds
        end_ts = end_date.int_timestamp * 1000
        url = f"https://api.bitfinex.com/v2/candles/trade:1D:t{symbol.upper()}/hist?end={end_ts}&limit={limit}"
        print(url)
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        # if we request 1000 results and got back 1000 results, there is a high
        # chance that there might be an earlier date
        if len(data) == limit:
            # save this data and make another request
            # with reduced end_ts
            previous_data = data
            end_date = end_date - pendulum.Interval(days=limit)
            print(f'hit limit, new end date is {end_date}')
            print('sleep...')
            sleep(5)
            continue
        else:
            # we got less than `limit` results, which means that the
            # earliest trading date is in the current results

            # if we got no results, it means we went too far back
            # and need to use the previous data
            if len(data) == 0:
                start_ts = previous_data[-1][0]
            else:
                start_ts = data[-1][0]
            print(f'Found start date for {symbol}')
            print(start_ts, pendulum.from_timestamp(start_ts/1000))
            result[symbol] = start_ts
            previous_data = None
            end_date = pendulum.now()
            print('sleep...')
            sleep(5)
            break
print(json.dumps(result))
