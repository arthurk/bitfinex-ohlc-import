#!/usr/bin/env python
"""
This is for testing purposes only.

TODO: make timout configurable
"""

import asyncio
import json
import websockets

URL = 'wss://api.bitfinex.com/ws/2'

# Symbols to which to subscribe to
SYMBOLS = [
    "btcusd",
    "ltcusd",
    "ltcbtc",
    "ethusd",
    "ethbtc",
    "etcbtc",
    "etcusd",
    "rrtusd",
    "rrtbtc",
    "zecusd",
    "zecbtc",
    "xmrusd",
    "xmrbtc",
    "dshusd",
    "dshbtc",
    "btceur",
    "xrpusd",
    "xrpbtc",
    "iotusd",
    "iotbtc",
    "ioteth",
    "eosusd",
    "eosbtc",
    "eoseth",
    "sanusd",
    "sanbtc",
    "saneth",
    "omgusd",
    "omgbtc",
    "omgeth",
    "bchusd",
    "bchbtc",
    "bcheth",
    "neousd",
    "neobtc",
    "neoeth",
    "etpusd",
    "etpbtc",
    "etpeth",
    "qtmusd",
    "qtmbtc",
    "qtmeth",
    "avtusd",
    "avtbtc",
    "avteth",
    "edousd",
    "edobtc",
    "edoeth",
    "btgusd",
    "btgbtc",
    "datusd",
    "datbtc",
    "dateth",
    "qshusd",
    "qshbtc",
    "qsheth",
    "yywusd",
    "yywbtc",
    "yyweth",
    "gntusd",
    "gntbtc",
    "gnteth",
    "sntusd",
    "sntbtc",
    "snteth",
    "ioteur",
    "batusd",
    "batbtc",
    "bateth",
    "mnausd",
    "mnabtc",
    "mnaeth",
    "funusd",
    "funbtc",
    "funeth",
    "zrxusd",
    "zrxbtc",
    "zrxeth",
    "tnbusd",
    "tnbbtc",
    "tnbeth",
    "spkusd",
    "spkbtc",
    "spketh",
    "trxusd",
    "trxbtc",
    "trxeth",
    "rcnusd",
    "rcnbtc",
    "rcneth",
    "rlcusd",
    "rlcbtc",
    "rlceth",
    "aidusd",
    "aidbtc",
    "aideth",
    "sngusd",
    "sngbtc",
    "sngeth",
    "repusd",
    "repbtc",
    "repeth",
    "elfusd",
    "elfbtc",
    "elfeth"
]


async def create_connection():
    websocket = await websockets.connect(URL, timeout=5)
    return websocket


async def consumer(msg):
    """
    Handle messages from the websocket.

    Messages can be dicts for events. Examples:

        {'event': 'subscribed', 'channel': 'trades',
         'chanId': 61, 'symbol': 'tLTCUSD', 'pair': 'LTCUSD'}
        {'event': 'info', 'version': 2}
        {'event': 'pong', 'cid': 1234, 'ts': 1519761108102}

    or lists with values. For the trades this would be:

        [10164, 'te', [203219379, 1519657613999, 26.2937, 35.879]]
        [16742, 'te', [203219446, 1519657618483, 12.31369845, 0.00079106]]

        Format: msg[2] = id, timestamp, amount (+ or -), price

    Other events that happened:

        {'event': 'info', 'code': 20051,
         'msg': 'Stopping. Please try to reconnect'}

         websockets.exceptions.ConnectionClosed:
            WebSocket connection is closed: code = 1006
            (connection closed abnormally [internal]), no reason


    """
    # Events
    if isinstance(msg, dict):
        # print all events so we can see what happened later in the log
        print(msg)

        # Right after connecting you receive an info message
        # that contains the actual version of the websocket stream.
        # {"event":"info","version":2,"platform":{"status":1}}
        if msg['event'] == 'info' and msg['platform']['status'] == 1:
            print('connection successful')
            return

        # a new subscription to a channel
        # if msg['event'] == 'subscribed':
        #     print(msg)
        # else:
        #     print(msg)
    # Values
    elif isinstance(msg, list):
        # heartbeat
        # Maybe later we can use it to figure out if the connection is failing
        # e.g. if 10sec between heartbeats we force re-connect
        if msg[1] == 'hb':
            return

        # trade execution
        if msg[1] in ('te', 'tu'):
            return

        # all other ones we print out
        print(msg)


async def subscribe(ws):
    # subscribe to trade channels
    for symbol in SYMBOLS:
        msg = {'event': 'subscribe',
               'channel': 'trades',
               'symbol': f't{symbol.upper()}'}
        await ws.send(json.dumps(msg))


async def run():
    # create connection
    websocket = await create_connection()

    # subscribe to trade channels
    await subscribe(websocket)

    num_msg = 0
    while True:
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=15)
        except asyncio.TimeoutError:
            # No data in `timeout` seconds, check the connection.
            print('timeout')
            try:
                print('ping')
                pong_waiter = await websocket.ping()
                await asyncio.wait_for(pong_waiter, timeout=5)
            except asyncio.TimeoutError:
                # No response to ping in 10 seconds, disconnect.
                print('ping failed, disconnect')
                break
        except websockets.exceptions.ConnectionClosed:
            # reconnect
            pass
        else:
            data = json.loads(message)

            # printing out how many messages we got
            num_msg += 1
            if num_msg % 1000 == 0:
                print(num_msg)
                print(data)

            # do something with msg
            await consumer(data)

    websocket.close()

asyncio.get_event_loop().run_until_complete(run())
