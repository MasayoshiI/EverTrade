import logging
import requests
import pprint

logger = logging.getLogger()

# def write_log():
#     logger.info("Hello fro Bitmex connector")

def get_contracts_bit():

    response = requests.get("https://www.bitmex.com/api/v1/instrument/active")
    print(response.status_code)
    symbols = response.json()
    # pprint.pprint(symbols)
    contracts = []
    for contract in symbols:
        contracts.append(contract['symbol'])

    return contracts

print(get_contracts_bit())