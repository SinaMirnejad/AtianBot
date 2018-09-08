#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
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


# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})

    book = {}
    price = {}

    AVOld = {}
    AVnew = {}

    from_exchange = read_from_exchange(exchange)

    while 1 == 1:

        #calculating average prices

        if from_exchange["type"] == "book":


            book[from_exchange["symbol"]] = from_exchange

            p = 0
            pc = 0

            for s in from_exchange["sell"]:
                p += s[0] * s[1]
                pc += s[1]

            for s in from_exchange["buy"]:
                p += s[0] * s[1]
                pc += s[1]

            price[from_exchange["symbol"]] = p / pc

            print(from_exchange["symbol"], price[from_exchange["symbol"]])
            print(from_exchange["type"], from_exchange, file=sys.stderr)


        #trading
        #while  not AVOld == -1 and not AVnew == -1: pass
        # Do trade based on Average values trade



        # A common mistake people make is to call write_to_exchange() > 1
        # time for every read_from_exchange() response.
        # Since many write messages generate marketdata, this will cause an
        # exponential explosion in pending messages. Please, don't do that!
        #system('clear')
        #for page in book:
            #print(book[page], file=sys.stderr)


if __name__ == "__main__":
    main()