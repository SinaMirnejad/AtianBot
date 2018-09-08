#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import time
from os import system, name

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="ATIAN"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=1
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

price = {"AAPL"	: [], "BABA": [], "BABZ": [], "BOND": [], "GOOG": [], "MSFT": [], "XLK": []}

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)


def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")


def read_from_exchange(exchange):
    return json.loads(exchange.readline())


def moving_average(history, time_length):
    cutoff = time.time() - time_length
    total_price = 0
    price_count = 0
    for i in range(len(history) - 1, -1, -1):
        if history[i][0] < cutoff and price_count != 0:
            return total_price / price_count
        total_price += history[i][1]
        price_count += 1
    return total_price / price_count

def main():
    id = 0
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})

    newAvrages= {}
    oldAvrages= {}

    MyAvragePrice={}

    sympbols = ["BOND",
                "BABZ",
                "BABA",
                "AAPL",
                "MSFT",
                "GOOG",
                "XLK"]

    for s in sympbols:
        newAvrages[s] = (0, 0)


    oldAvrages = newAvrages

    while 1 == 1:

        oldAvrages = newAvrages
        for s in sympbols:
            newAvrages[s] = (0,0)


        from_exchange = read_from_exchange(exchange)
        #print(from_exchange)

        if from_exchange["type"] == "book":

            symbol = from_exchange["symbol"]

            while len(price[symbol]) > 0 and price[symbol][0][0] < time.time() - 60:
                price[symbol].pop(0)

            total_price = 0
            price_count = 0

            total_priceS = 0
            price_countS = 0

            for s in from_exchange["sell"]:
                total_price += s[0] * s[1]
                price_count += s[1]
            for s in from_exchange["buy"]:
                total_priceS += s[0] * s[1]
                price_countS += s[1]

            price_count += 1
            price_countS += 1
            average_price = total_price / price_count
            average_priceS = total_priceS / price_countS



            price[symbol].append([time.time(), average_price])
            newAvrages[symbol] = (average_priceS,average_priceS)



            for s in sympbols:
                print(s, average_price, average_priceS)

            #print(symbol, average_price, moving_average(price[symbol], 15), moving_average(price[symbol], 60))


        for s in sympbols:

            T = oldAvrages[s][0];
            TS = oldAvrages[s][1];

            if newAvrages[s][0] < TS:
                write_to_exchange(exchange,
                                  {"type": "add", "order_id": id, "symbol": s,
                                   "dir": "SELL", "price": newAvrages[s], "size": 1})
                id += 1
            if newAvrages[s][1] > T:
                write_to_exchange(exchange,
                                  {"type": "add", "order_id": id, "symbol": s,
                                   "dir": "BUY", "price": newAvrages[s], "size": 1})
                id += 1

        #system('clear')
        #print(json.dumps(price, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()