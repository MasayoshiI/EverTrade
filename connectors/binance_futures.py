
import logging
from symtable import Symbol
from urllib.parse import urlencode
import requests
import pprint

import time
import hmac
import hashlib

import websocket
import threading
import ssl 
import json

from ..models import *


logger = logging.getLogger()

# def write_log():
#     logger.info("Hello fro Binance connector")

class BinanceFutureClient:

    """
    Binance Client Connector class: it helps the bot to connect Binance,
    and provides basic functions such as gettting contracts, historical data, and bid ask
    """

    def __init__(self, public_key, secret_key, testmode):
        """initiate with testmode input (testmode = True then it is on a testmode)"""
        if testmode:
            self.base_url = "https://testnet.binancefuture.com"
            self.wss_url = "wss://stream.binancefuture.com/ws"
        else:
            self.base_url = "https://fapi.binance.com"
            self.wss_url = "wss://fstream.binance.com/ws"

        self.public_key = public_key
        self.secret_key = secret_key

        self.headers = {'X-MBX-APIKEY': self.public_key}
        
        self.prices = dict()

        self.id = 1

        self.ws = None

        t = threading.Thread(target=self.start_ws())
        t.start()
        
        
        logger.info("Binance client successfully initialized...")

    def generate_signature(self, data):
        print(hmac.new(self.secret_key.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest())
        return hmac.new(self.secret_key.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()

    def make_request(self, method, endpoint, data):
        """this function construct the request based on given inputs: method, endpoint, and data"""
        if method == "GET":
            response = requests.get(self.base_url + endpoint, params=data, headers=self.headers)
        
        elif method == "POST":
            response = requests.post(self.base_url + endpoint, params=data, headers=self.headers)
        
        elif method == "DELETE":
            response = requests.delete(self.base_url + endpoint, params=data, headers=self.headers)

        else:
            raise ValueError

        if response.status_code == 200:
            # successful = return the json
            return response.json()

        else:
            # in case of an error display the error message & code
            logger.error("Error while %s request to %s: %s (Error Code: %s", method, endpoint, response.json, response.status_code)
            return None

    def get_contracts(self):

        exchange_info = self.make_request("GET", "/fapi/v1/exchangeInfo", None)

        contracts = dict()
        if exchange_info is not None:
            for contracts_data in exchange_info["symbols"]:
                contracts[contracts_data['pair']] = contracts_data


        return contracts
    
    def get_historical_candles(self, symbol, interval):
        data = dict()
        data["symbol"] = symbol
        data["interval"] = interval
        data["limit"] = 1000

        raw_candles = self.make_request("GET", '/fapi/v1/klines', data)
        
        candles = []

        if raw_candles is not None:
            for c in raw_candles:
                candles.append(Candle(c))
        
        return candles

    def get_bid_ask(self, symbol):
        """aaa"""
        data = dict()
        data["symbol"] = symbol
        ob_data = self.make_request("GET", "/fapi/v1/ticker/bookTicker", data)

        if ob_data is not None:
            if symbol not in self.prices:
                """if the input symbol is not """
                # print(ob_data)
                self.prices[symbol] = {'bid': float(ob_data['bidPrice']), 'ask': float(ob_data['askPrice'])}

            else:
                self.prices[symbol]['bid'] = float(ob_data['bidPrice'])
                self.prices[symbol]['ask'] = float(ob_data['askPrice'])
                
        return self.prices[symbol]

    def get_balances(self):

        data = dict()
        
        data['timestamp'] = int(time.time()*1000)
        data['signature'] = self.generate_signature(data)
        
        account_data = self.make_request("GET", "/fapi/v1/account", data)
        
        balances = dict()

        if account_data is not None:
            for a in account_data['assets']:
                balances[a['asset']] = Balance(a)

        return balances
    
    def place_order(self, symbol, side, quantity, order_type, price=None, tif=None):
        
        data = dict()

        data['symbol'] = symbol
        data['side'] = side
        data['quantity'] = quantity
        data['type'] = order_type
        
        if price is not None:
            data['price'] = price
        
        if tif is not None:
            data['timeInFrame'] = tif

        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("POST", "/fapi/v1/order", data)

        print(order_status)
        return order_status

    def cancel_order(self, symbol, order_id):

        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['symbol'] = symbol
        data['orderId'] = order_id
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("DELETE", "/fapi/v1/order", data)
        print(order_status)
        return order_status

    def get_order_status(self, symbol, order_id):
        
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['symbol'] = symbol
        data['orderId'] = order_id
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("GET", "/fapi/v1/order", data)
        print(order_status)
        return order_status

    def start_ws(self):
        self.ws = websocket.WebSocketApp(self.wss_url, on_open=self.on_open, on_close=self.on_close, 
                                    on_error=self.on_error, on_message=self.on_message  )
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def on_open(self):
        logger.info("Binance Websocket connection established..")

    def on_close(self):
        logger.warning("Binance Websocket connnection is closed")

    def on_error(self, msg):
        logger.error("Binance Websocket connection error: %s", msg)

    def on_message(self, msg):
        
        # print(msg)
        data = json.loads(msg)

        if "e" in data:
            if data["e"] == 'bookTicker':

                symbol = data["s"]

                if symbol not in self.prices:
                    """if the input symbol is not """
                    # print(ob_data)
                    self.prices[symbol] = {'bid': float(data['b']), 'ask': float(data['a'])}

                else:
                    self.prices[symbol]['bid'] = float(data['b'])
                    self.prices[symbol]['ask'] = float(data['a'])

                print(self.prices[symbol])
                

    def subscribe_channel(self, symbol):
        data = dict()
        data["method"] = "SUBSCRIBE"
        data["params"] = []
        data["params"].append(symbol.lower(), "@bookTicker")
        
        data["id"] = self.id

        print(data, type=data)
        print(json.dumps(data), type(json.dumps(data)))

        self.ws.send()

        self.id += 1
    
    