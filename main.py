import tkinter as tk
import logging
from connectors.binance_futures import *
from connectors.bitmex import *
from configparser import ConfigParser, NoSectionError, ParsingError

logger = logging.getLogger()


logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s ')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# logger.debug("Debug purpose")
# logger.info("shows basic info")
# logger.warning("warning message / pay attention")
# logger.error("error message that will help us debug")

# write_log()


if __name__ == "__main__":
    # bitmex_contracts = get_contracts_bit()

    config = ConfigParser()
    config.read('api_keys.conf')

    # set up api keys
    binance_key = config.get('APIKEY','binancekey')
    binance_secret = config.get('APIKEY','binanceSecret')
    # print(binance_secret)

    # initiate binance client
    binance = BinanceFutureClient(binance_key, binance_secret, True)
    # print(binance.get_historical_candles("BTCUSDT", "1h"))
    # print(binance.get_contracts())
    print(binance.get_balances())
    # print(binance.place_order("BTCUSDT", "BUY", 0.01, "LIMIT", 20000,"GTC"))
    # print(binance.get_order_status("BTCUSDT", 2612334776))
    # print(binance.cancel_order("BTCUSDT", 2612334776))
    # open the window
    root = tk.Tk()
    # root.configure(bg='grey12')
    # i = 0
    # j = 0
    # font = ('Calibri',11,'normal')
    # for contract in bitmex_contracts:
    #     # label_widget = tk.Label(root, text=contract, borderwidth=1, relief=tk.SOLID)
    #     label_widget = tk.Label(root, text=contract, bg='gray12', fg='SteelBlue', width=13, font=font)
    #     label_widget.grid(row=i, column=j, sticky='ew')

    #     if i == 4:
    #         j += 1
    #         i = 0
    #     else:
    #         i+=1



    # root.mainloop()