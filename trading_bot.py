"""A crypto trading bot to place buy and sell orders automatically"""
import argparse
import csv
import hashlib
import hmac
import json
import logging
import os
import smtplib
import time
from datetime import datetime, timedelta
import pandas as pd

import requests
import yaml
from matplotlib import pyplot
from tradingview_ta import TA_Handler
import constants
import trading_bot_auth
from paths import paths

# TODO: Encrypt regardless of where the keys are coming from.
# pd.options.display.float_format = '{:.0f}'.format

PARSER = argparse.ArgumentParser()
CONFIG = constants.CONFIG
ORDER_HISTORY_FILE = constants.ORDER_HISTORY_FILE
LOGFILE = constants.LOGFILE
TODAY = constants.TODAY
SCREENER_LIST = constants.SCREENER_LIST
API_DICTS = constants.API_DICTS
INTERVAL_DICT = constants.INTERVAL_DICT
URL_DICT = constants.URL_DICT
REMOVE_CURRENCIES = constants.REMOVE_CURRENCIES

with open(constants.CONFIG_FILE) as file:
    CONFIG = yaml.safe_load(file)


logging.basicConfig(
    level=logging.INFO,
    filemode="a",
    filename=constants.LOGFILE,
    format="%(asctime)s;%(levelname)s;%(message)s",
)


def initialize():
    if not os.path.exists(os.path.join(paths.HOME_DIRECTORY, paths.MARKET_DATA_DIRECTORY)):
        logging.info(rf"{paths.MARKET_DATA_DIRECTORY} does not exist! Creating {paths.MARKET_DATA_DIRECTORY}")
        os.mkdir(os.path.join(paths.HOME_DIRECTORY, paths.MARKET_DATA_DIRECTORY))
    if not os.path.isfile(os.path.join(paths.HOME_DIRECTORY, paths.LOGFILE)):
        logging.info(rf"{paths.LOGFILE} does not exist! Creating {paths.LOGFILE}")
        with open(os.path.join(paths.HOME_DIRECTORY, paths.LOGFILE), "w") as file:
            pass
    if not os.path.isfile(os.path.join(paths.HOME_DIRECTORY, paths.CONFIG_FILE)):
        logging.info(rf"{paths.CONFIG_FILE} does not exist! Creating {paths.CONFIG_FILE}")
        with open(os.path.join(paths.HOME_DIRECTORY, paths.CONFIG_FILE), "w") as file:
            pass
    if not os.path.isfile(os.path.join(paths.MARKET_DATA_DIRECTORY, paths.ORDER_HISTORY_FILE)):
        logging.info(rf"{paths.ORDER_HISTORY_FILE} does not exist! Creating {paths.ORDER_HISTORY_FILE}")
        with open(os.path.join(paths.MARKET_DATA_DIRECTORY, paths.ORDER_HISTORY_FILE), "w") as file:
            pass
    if not os.path.isfile(os.path.join(paths.MARKET_DATA_DIRECTORY, paths.TRADING_BOT_ORDER_HISTORY_FILE)):
        logging.info(rf"{paths.TRADING_BOT_ORDER_HISTORY_FILE} does not exist! Creating {paths.TRADING_BOT_ORDER_HISTORY_FILE}")
        with open(os.path.join(paths.MARKET_DATA_DIRECTORY, paths.TRADING_BOT_ORDER_HISTORY_FILE), "w") as file:
            pass


def get_keys(first_name: str = "", last_name: str = "", username: str = "") -> tuple:
    """Get API key and secret key for the specified username. If username is not mentioned then, first name and last name of the username can be used to retrieve the keys.

    Args:
        first_name (str, optional): First name of the username. Defaults to "".
        last_name (str, optional): Last name of the username. Defaults to "".
        username (str, optional): Username to retrieve the keys. Defaults to "".

    Returns:
        tuple: The API key and the secret key.
    """
    # print(trading_bot_auth.get_user_credentials(first_name=first_name, last_name=last_name, username=username))
    return trading_bot_auth.get_user_credentials(
        first_name=first_name, last_name=last_name, username=username
    )


def add_keys(
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
) -> None:
    """Add API key and the secret key for a new username. If the username already exists. Return exception.

    Args:
        first_name (str, optional): First name of the username. Defaults to "".
        last_name (str, optional): Last name of the username. Defaults to "".
        api_key (str, optional): API key of the username.
        secret_key (str, optional): API secret of the username.
    """
    return trading_bot_auth.add_user_credentials(
        username=username,
        first_name=first_name,
        last_name=last_name,
        api_key=api_key,
        secret_key=secret_key,
        email=email,
        google_auth_key=google_auth_key,
    )


def update_keys(
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
) -> dict:
    """
    Updates the keys for a username in the trading accounts.

    Args:
        first_name (str): The first name of the username. Defaults to "".
        last_name (str): The last name of the username. Defaults to "".
        api_key (str): The API key for the username. Defaults to "".
        secret_key (str): The secret key for the username. Defaults to "".
        email (str): The email address of the username. Defaults to "".
        google_auth_key (str): The Google authentication key for the username. Defaults to "".

    Returns:
        dict: A dictionary with the HTTP status code and a message.
        If the username is not present, returns {404: "Error username not present!"}.
        If the username is updated successfully, returns {200: "User updated!"}.
    """
    return trading_bot_auth.update_user_credentials(
        username=username,
        first_name=first_name,
        last_name=last_name,
        api_key=api_key,
        secret_key=secret_key,
        email=email,
        google_auth_key=google_auth_key,
    )


def delete_keys(first_name: str, last_name: str, username: str) -> dict:
    """
    Delete the keys for a specific username in the trading bot configuration file.

    Parameters:
        first_name (str): The first name of the username.
        last_name (str): The last name of the username.
        username (str): The username of the username.

    Returns:
        None
    """
    return trading_bot_auth.delete_user_credentials(
        first_name=first_name, last_name=last_name, username=username
    )


def get_ticker(coin_1: str = "BTC", coin_2: str = "USDT", all_coins: bool = False) -> pd.DataFrame:
    """Get the ticker details of the coin

    Args:
        coin_1 (str, optional): The coin to get the ticker details of. Defaults to "BTC".
        coin_2 (str, optional): The coin against which to get the ticker details of. Defaults to "USDT".
        all_coins (bool, optional): Whether to get the ticker details of all the coins. Defaults to False.

    Returns:
        dict: The dictionary of the coins details
    """
    url = URL_DICT["TICKER_URL"]
    response = requests.get(url)
    data = response.json()
    coins_dictionary = {}
    if all_coins:
        ...
    else:
        for coins in data:
            if coins["market"] == coin_1 + coin_2:
                coins["unix_timestamp"] = coins["timestamp"]
                coins["timestamp"] = datetime.fromtimestamp(coins["timestamp"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                return pd.DataFrame.from_dict([coins])


def get_market_data(save_dataframe: bool = False) -> pd.DataFrame:
    # TODO: Add Currencies to include feature
    """Get the market data of all coins in the market currently.

    Args:
        save_dataframe (bool, optional): Whether to save the dataframe. Defaults to False.

    Returns:
        dict: The dictionary of the coins market data
    """
    coins_dictionary = {}
    url = URL_DICT["MARKET_DATA_URL"]
    response = requests.get(url)
    data = response.json()
    for coins in data:
        if "USDT" in coins["market"] and "insta" not in coins["market"]:
            coins_dictionary[coins["market"]] = coins
        elif "BTC" in coins["market"] and "insta" not in coins["market"]:
            coins_dictionary[coins["market"]] = coins
        elif "VRA" in coins["market"] and "insta" not in coins["market"]:
            coins_dictionary[coins["market"]] = coins
    dataframe = pd.DataFrame(coins_dictionary).T
    dataframe = dataframe.sort_index(ascending=True, axis=0)
    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], unit="ms") - timedelta(
        hours=7, minutes=0
    )
    if save_dataframe:
        dataframe.to_csv(
            rf"C:\Users\nadig\git\crypto_market_data\{datetime.now().strftime('%Y-%m-%d')}_market_data.csv"
        )
        return dataframe
    else:
        return dataframe


def get_markets_details(
    coin_1: str = "",
    coin_2: str = "USDT",
    coins_list: list = [],
    all_coins: bool = False,
    save_dataframe: bool = False,
) -> pd.DataFrame:
    """Get the market details of the coins listed on the exchange. This includes the max leverage of the coin, the market it trades in, the min quantity to place an order, the max quantity to place an order.

    Args:
        coin_1 (str, optional): The coin to check the price for. Defaults to "BTC".
        coin_2 (str, optional): The coin to check the price against. Defaults to "USDT".
        coins_list (list, optional): If you want the details of multiple coins then pass all the coins as a list to this argument. Defaults to [].

    Returns:
        dict: The dictionary of the market details of the coins.
    """
    url = URL_DICT["MARKET_DETAILS_URL"]
    response = requests.get(url)
    data = response.json()
    # print(data)
    coins_dictionary = {}

    if all_coins:
        for coins in data:
            if coin_2 in coins["symbol"]:
                coins_list.append(coins)
        if save_dataframe:
            pd.DataFrame.from_dict(coins_list).to_csv(
                os.path.join(
                    constants.MARKET_DATA_DIRECTORY,
                    f"{datetime.now().strftime('%Y-%m-%d')}_market_details.csv",
                )
            )
        return pd.DataFrame.from_dict(coins_list)
    elif len(coins_list) > 0:
        for coins in data:
            if coins["symbol"] == coin_1 + coin_2:
                return coins
        for coin in coins_list:
            for coins in data:
                if coins["symbol"] == coin + "USDT":
                    coins_dictionary[coins["symbol"]] = coins
        # print(coins_dictionary)
        if save_dataframe:
            pd.DataFrame.from_dict(coins_list).to_csv(
                os.path.join(
                    constants.MARKET_DATA_DIRECTORY,
                    f"{datetime.now().strftime('%Y-%m-%d')}_market_details.csv",
                )
            )
        return pd.DataFrame.from_dict(coins_dictionary)
    else:
        dataframe = pd.DataFrame(data)
        return dataframe[dataframe['coindcx_name'] == coin_1 + coin_2]


def place_buy_limit_order(
    username: str = CONFIG["Owner"]["main_username"],
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    price: float = 0.023,
    total_quantity: float = 450,
) -> None:
    """Place a buy limit order on the market pair specified.

    Args:
        username (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        price (float): The price at which to buy.
        total_quantity (float): The number of stocks or coins to buy.
    """
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    body = {
        "side": "buy",  # Toggle between 'buy' or 'sell'.
        "order_type": "limit_order",  # Toggle between a 'market_order' or 'limit_order'.
        "market": f"{coin_1+coin_2}",  # Replace 'SNTBTC' with your desired market pair.
        "price_per_unit": price,  # This parameter is only required for a 'limit_order'
        "total_quantity": 450,  # Replace this with the quantity you want
        "timestamp": time_stamp,
    }
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(URL_DICT["NEW_ORDER_URL"], data=json_body, headers=headers)
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    data = response.json()
    logging.info(data)
    with open(ORDER_HISTORY_FILE, "a", newline="") as file:
        csvwrite = csv.writer(file, dialect="excel")
        csvwrite.writerow(
            [
                "",
                coin_1 + coin_2,
                total_quantity,
                "market_order",
                "buy",
                TODAY,
            ]
        )
    logging.info(f"Bought {total_quantity} {coin_1+coin_2} at {price}")
    file.close()
    return data


def place_sell_limit_order(
    username: str = CONFIG["Owner"]["main_username"],
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    price: float = 0.25,
    total_quantity: float = 450,
) -> None:
    """Place a buy limit order on the market pair specified.

    Args:
        username (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        price (float): The price at which to sell.
        total_quantity (float): The number of stocks or coins to sell.
    """

    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))

    body = {
        "side": "sell",  # Toggle between 'buy' or 'sell'.
        "order_type": "limit_order",  # Toggle between a 'market_order' or 'limit_order'.
        "market": f"{coin_1+coin_2}",  # Replace 'SNTBTC' with your desired market pair.
        "price_per_unit": price,  # This parameter is only required for a 'limit_order'
        "total_quantity": f"{total_quantity}",  # Replace this with the quantity you want
        "timestamp": time_stamp,
    }
    json_body = json.dumps(body, separators=(",", ":"))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(URL_DICT["NEW_ORDER_URL"], data=json_body, headers=headers)
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    data = response.json()
    logging.info(data)
    with open(ORDER_HISTORY_FILE, "a", newline="") as file:
        csvwrite = csv.writer(file, dialect="excel")
        csvwrite.writerow(
            [
                "",
                coin_1 + coin_2,
                total_quantity,
                "market_order",
                "sell",
                TODAY,
            ]
        )
    logging.info(f"Sold {total_quantity} {coin_1+coin_2} at {price}")
    file.close()


def place_market_buy_order(
    username: str = CONFIG["Owner"]["main_username"],
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    total_quantity: float = 450,
) -> None:
    """Place a buy market order on the market pair specified. The order is placed at the current market price. This order gets executed immediately.

    Args:
        username (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        total_quantity (float): The number of stocks or coins to buy.
    """

    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))

    body = {
        "side": "buy",  # Toggle between 'buy' or 'sell'.
        "order_type": "market_order",  # Toggle between a 'market_order' or 'limit_order'.
        "market": f"{coin_1+coin_2}",  # Replace 'SNTBTC' with your desired market pair.
        "total_quantity": total_quantity,  # Replace this with the quantity you want
        "timestamp": time_stamp,
    }
    json_body = json.dumps(body, separators=(",", ":"))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(URL_DICT["NEW_ORDER_URL"], data=json_body, headers=headers)
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    data = response.json()

    with open(ORDER_HISTORY_FILE, "a", newline="") as file:
        csvwrite = csv.writer(file, dialect="excel")
        csvwrite.writerow(
            [
                "",
                coin_1 + coin_2,
                total_quantity,
                "market_order",
                "buy",
                TODAY,
            ]
        )
        logging.info(f"Market bought {total_quantity} {coin_1+coin_2}")
    return data


def place_market_sell_order(
    username: str = CONFIG["Owner"]["main_username"],
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    total_quantity: float = 450,
) -> None:
    """Place a sell market order on the market pair specified. The order is placed at the current market price. This order gets executed immediately.

    Args:
        username (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        total_quantity (float): The number of stocks or coins to buy.
    """

    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))

    body = {
        "side": "sell",  # Toggle between 'buy' or 'sell'.
        "order_type": "market_order",  # Toggle between a 'market_order' or 'limit_order'.
        "market": f"{coin_1+coin_2}",  # Replace 'SNTBTC' with your desired market pair.
        "total_quantity": f"{total_quantity}",  # Replace this with the quantity you want
        "timestamp": time_stamp,
    }
    json_body = json.dumps(body, separators=(",", ":"))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(URL_DICT["NEW_ORDER_URL"], data=json_body, headers=headers)
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    logging.info(response.json())
    with open(ORDER_HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        csvwrite = csv.writer(file, dialect="excel")
        csvwrite.writerow(
            [
                "",
                coin_1 + coin_2,
                total_quantity,
                "market_order",
                "sell",
                TODAY,
            ]
        )
    logging.info(f"Market sold {total_quantity} {coin_1+coin_2}")
    file.close()
    return response.json()


def create_multiple_orders(
    username: str = CONFIG["Owner"]["main_username"], orders: list = []
) -> None:
    """Create multiple orders at once.

    Args:
        username (str): The username of the account to place the order in.
        orders (str): The different orders that need to be placed for the username.
    """
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    body = {
        "orders": [
            {
                "side": "buy",  # Toggle between 'buy' or 'sell'.
                "order_type": "limit_order",  # Toggle between a 'market_order' or 'limit_order'.
                "market": "SNTBTC",  # Replace 'SNTBTC' with your desired market pair.
                "price_per_unit": 0.03244,  # This parameter is only required for a 'limit_order'
                "total_quantity": 400,  # Replace this with the quantity you want
                "timestamp": time_stamp,
                "ecode": "I",
            },
            {
                "side": "buy",  # Toggle between 'buy' or 'sell'.
                "order_type": "limit_order",  # Toggle between a 'market_order' or 'limit_order'.
                "market": "SNTBTC",  # Replace 'SNTBTC' with your desired market pair.
                "price_per_unit": 0.03244,  # This parameter is only required for a 'limit_order'
                "total_quantity": 400,  # Replace this with the quantity you want
                "timestamp": time_stamp,
                "ecode": "I",
            },
        ]
    }

    json_body = json.dumps(body, separators=(",", ":"))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }

    response = requests.post(
        URL_DICT["CREATE_MULTIPLE_ORDERS_URL"], data=json_body, headers=headers
    )
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    logging.info(response.json())
    return response.json()


def get_active_orders(username: str = CONFIG["Owner"]["main_username"]) -> dict:
    """Get the current buy or sell active orders for the username.

    Args:
        username (str): The username of the account to get the active orders from.

    Returns:
        dict: List of all the active orders
    """
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    body = {
        "side": "buy",  # Toggle between a 'buy' or 'sell' order.
        "market": "SNTBTC",  # Replace 'SNTBTC' with your desired market pair.
        "timestamp": time_stamp,
    }
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["ACTIVE_ORDERS_URL"], data=json_body, headers=headers, timeout=60
    )
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    return response.json()


def account_trade_history(username: str = CONFIG["Owner"]["main_username"], save_dataframe: bool = False, limit: int = 500) -> dict:
    """Get the account trade history of the username.

    Args:
        username (str): The username of the account for which the trade history is to be fetched.

    Returns:
        dict: The history of trades made by the username.
    """
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))

    body = {"from_id": 352622, "limit": 50, "timestamp": time_stamp, "sort": "desc", "limit": limit}

    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["ACCOUNT_TRADE_HISTORY_URL"], data=json_body, headers=headers, timeout=60
    )

    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    dataframe = pd.DataFrame(response.json())
    dataframe['timestamp'] = pd.to_datetime(dataframe["timestamp"], unit="ms") - timedelta(
            hours=7, minutes=0
        )
    if save_dataframe:
        dataframe.to_csv(paths.ORDER_HISTORY_FILE)
    return dataframe


def cancel_order(username: str = CONFIG["Owner"]["main_username"], ids: str = "") -> None:
    """Cancel a particular order of the username.

    Args:
        username (str): The username of the account for whom the order needs to be cancelled.
        id (_type_): The order id.
    """
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")

    time_stamp = int(round(time.time() * 1000))
    body = {"id": f"{ids}", "timestamp": time_stamp}  # Enter your Order ID here.
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["CANCEL_ONE_ACTIVE_ORDER_URL"], data=json_body, headers=headers, timeout=60
    )
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    logging.info(response.json())
    return response.json()


def cancel_all_orders(username: str = CONFIG["Owner"]["main_username"]) -> None:
    """Cancel all the active orders of the username.

    Args:
        username (str): The username of the account for which the order needs to be cancelled.
    """
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    active_orders = get_active_orders()
    time_stamp = int(round(time.time() * 1000))
    body = {
        "side": "buy",  # Toggle between a 'buy' or 'sell' order.
        "market": "SNTBTC",  # Replace 'SNTBTC' with your desired market pair.
        "timestamp": time_stamp,
    }
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["CANCEL_ALL_ACTIVE_ORDERS_URL"], data=json_body, headers=headers, timeout=60
    )
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    return response.json()


def cancel_multiple_by_ids(username: str = CONFIG["Owner"]["main_username"], ids: list = []) -> None:
    """Cancel multiple orders given by the list of ids for a particular username.

    Args:
        username (str): The username of the account for which the orders need to be cancelled.
        ids (list): The list of order ids to cancel.
    """
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")

    body = {"ids": ids}

    json_body = json.dumps(body, separators=(",", ":"))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url = "https://api.coindcx.com/exchange/v1/orders/cancel_by_ids"

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }

    response = requests.post(url, data=json_body, headers=headers, timeout=60)
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    return response.json()


def edit_price_of_orders(
    username: str = CONFIG["Owner"]["main_username"], ids: list = [], price: float = ""
) -> None:
    """Edit the buy or sell price of the orders.

    Args:
        username (str): The username of the account for which the price needs to be edited.
        ids (_type_): The order id for which the price needs to be edited
        price (float): _description_
    """

    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    body = {
        "id": f"{ids}",  # Enter your Order ID here.
        "timestamp": time_stamp,
        "price_per_unit": f"{price}",  # Enter the new-price here
    }
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["EDIT_PRICE_URL"], data=json_body, headers=headers, timeout=60
    )
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    return response.json()


def bot_trader(
    username: str = CONFIG["Owner"]["main_username"],
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    market: str = "Binance",
    screener_name: str = "Crypto",
    interval: str = "4h",
) -> None:
    """Execute trades automatically 24/7 based on input parameters

    Args:
        username (str): The username of the account to auto_trade in.
        coin_1 (str): Ticker Ex: "CIPLA", "TATAMOTORS", "XVG", "BTC".
        coin_2 (str): Ticker Ex: USDT, INR.
        market (str): he name of the exchange ("NSE", "BSE", "Binance").
        screener_name (str): Either "India" or "Crypto".
        interval (str): Interval of chart "1m", "5m", "30m", "1h", "2h", "4h", "1d", "1W", "1M
    """
    no_of_trades = 0
    open_position = False
    min_order_value = 0.0001
    order_size = 0
    logging.info(f"""{coin_1}{coin_2} Bot Started for {username} at {datetime.now()}!""")
    indicator_data_ = get_indicator_data(
        coin_1=coin_1, coin_2=coin_2, market=market, screener_name=screener_name, interval=interval
    )
    rsi = indicator_data_["RSI"]
    buy_price = indicator_data_["Pivot.M.Fibonacci.Middle"]
    sell_price = indicator_data_["Pivot.M.Fibonacci.R1"]
    stop_loss = indicator_data_["Pivot.M.Fibonacci.S1"] - 0.00000001
    logging.info(
        f"""RSI value for {interval} for {coin_1+coin_2} is {rsi}.\nBuy price is {buy_price}.\nTarget is {sell_price}.\nStop loss is set at {stop_loss}.
            \nOrder size is {order_size}."""
    )
    while no_of_trades <= 100:
        try:
            data = get_candles(coin_1=coin_1, coin_2=coin_2)
            indicator_data_ = get_indicator_data(
                coin_1=coin_1,
                coin_2=coin_2,
                market=market,
                screener_name=screener_name,
                interval=interval,
            )
            account_balance = get_account_balance(username=username)
        except Exception as exception:
            logging.error(exception)
            time.sleep(60)
            data = get_candles(coin_1=coin_1, coin_2=coin_2)
            indicator_data_ = get_indicator_data(
                coin_1=coin_1,
                coin_2=coin_2,
                market=market,
                screener_name=screener_name,
                interval=interval,
            )
            account_balance = get_account_balance(username=username)

        rsi = indicator_data_["RSI"]
        ema50 = indicator_data_["EMA50"]
        ema200 = indicator_data_["EMA200"]
        stochastic_k = indicator_data_["Stoch.K"]
        stochastic_d = indicator_data_["Stoch.D"]
        macd_macd = indicator_data_["MACD.macd"]
        macd_sig = indicator_data_["MACD.signal"]
        open_price = indicator_data_["open"]
        high_price = indicator_data_["high"]
        low_price = indicator_data_["low"]
        close_price = indicator_data_["close"]
        pivot = indicator_data_["Pivot.M.Fibonacci.Middle"]
        supports = [
            indicator_data_["Pivot.M.Fibonacci.S1"],
            indicator_data_["Pivot.M.Fibonacci.S2"],
            indicator_data_["Pivot.M.Fibonacci.S3"],
        ]
        resistances = [
            indicator_data_["Pivot.M.Fibonacci.R1"],
            indicator_data_["Pivot.M.Fibonacci.R2"],
            indicator_data_["Pivot.M.Fibonacci.R3"],
        ]
        dataframe = pd.DataFrame.from_dict(data)
        dataframe = dataframe.sort_values("market")
        # dataframe = dataframe[columns]
        dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], unit="ms") - timedelta(
            hours=7, minutes=0
        )
        for currency in REMOVE_CURRENCIES:
            dataframe = dataframe[~dataframe.market.str.endswith(currency)]
        dataframe = dataframe.reset_index(drop=True)
        dataframe = dataframe.sort_index(ascending=True, axis=0)
        current_price = get_ticker(coin_1=coin_1, coin_2=coin_2)["last_price"]
        # SET BUY PRICE, SELL PRICE AND STOP LOSS CONDITIONS
        if current_price < pivot and current_price > supports[0] and current_price < close_price:
            buy_price = supports[0]
            stop_loss = supports[0] - int(0.01 * buy_price)
            sell_price = pivot
        elif (
            current_price < supports[0]
            and current_price > supports[1]
            and current_price < close_price
        ):
            buy_price = supports[1]
            stop_loss = supports[1] - int(0.01 * buy_price)
            sell_price = supports[0]
        elif (
            current_price < supports[1]
            and current_price > supports[2]
            and current_price < close_price
        ):
            buy_price = supports[2]
            stop_loss = supports[2] - int(0.01 * buy_price)
            sell_price = supports[1]
        elif current_price < supports[2]:
            pass
        order_size = 0.33 * account_balance
        if (  # BUY CONDITIONS
            float(current_price) == buy_price and not open_position and order_size > min_order_value
        ) or (rsi < 37 and not open_position and order_size > min_order_value):
            place_buy_limit_order(
                username=username, market=market, price=buy_price, total_quantity=order_size
            )
            logging.info(
                f"Buy Order placed! for {coin_1+coin_2} at price {buy_price}. Stop loss is {stop_loss}"
            )
            open_position = True
        if (  # SELL CONDITIONS
            (float(current_price) == sell_price and open_position)
            or float(current_price) == stop_loss
            or (rsi > 60 and open_position)
        ):
            place_sell_limit_order(username=username, price=sell_price, total_quantity=order_size)
            logging.info(f"Sold {market} for: {sell_price}")
            logging.info(f"The current account balance is: {account_balance} BTC")
            open_position = False
            no_of_trades += 1
            profit = ((sell_price - buy_price) / buy_price) * (100)
            logging.info(f"made {profit}% profits!")
            send_mail(f"Sold {coin_2} for {profit}% profits!")


def get_account_balance(username: str = CONFIG["Owner"]["main_username"], save_dataframe: bool = False) -> dict:
    """Get the account balance of the username.

    Args:
        username (str, optional): The username of the account to get the balance of. Defaults to CONFIG['Owner']['main_username'].

    Returns:
        dict: The dictionary of the account balances of all the currencies.
    """
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    body = {"timestamp": time_stamp}
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }

    response = requests.post(
        URL_DICT["ACCOUNT_BALANCE_URL"], data=json_body, headers=headers, timeout=60
    )
    if type(response.json) == dict and 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    dataframe = pd.DataFrame(response.json())
    # print(get_ticker().keys())
    dataframe = dataframe[(dataframe['balance'].astype(float) > 0.0) | dataframe['locked_balance'].astype(float) > 0.0]
    for coin in dataframe['currency']:
        try:
            dataframe.loc[dataframe['currency'] == coin, "quantity"] = dataframe.loc[dataframe['currency'] == coin]["balance"].astype(float)
            dataframe.loc[dataframe['currency'] == coin, "balance"] = float(dataframe.loc[dataframe['currency'] == coin]["balance"]) * float(get_ticker(coin_1=coin)['last_price'])
            dataframe.loc[dataframe['currency'] == coin, "locked_balance"] = float(dataframe.loc[dataframe['currency'] == coin]["locked_balance"]) * float(get_ticker(coin_1=coin)['last_price'])
        except Exception as e:
            logging.info(e)
            try:
                dataframe.loc[dataframe['currency'] == coin, "quantity"] = dataframe.loc[dataframe['currency'] == coin]["balance"].astype(float)
                dataframe.loc[dataframe['currency'] == coin, "balance"] = float(dataframe.loc[dataframe['currency'] == coin]["balance"])* float(get_ticker(coin_1=coin, coin_2 = "USDC")['last_price'])
                dataframe.loc[dataframe['currency'] == coin, "locked_balance"] = float(dataframe.loc[dataframe['currency'] == coin]["locked_balance"]) * float(get_ticker(coin_1=coin, coin_2 = "USDC")['last_price'])
            except Exception as e:
                logging.info(e)
    dataframe = dataframe[(dataframe['balance'].astype(float) > 0.5) | dataframe['locked_balance'].astype(float) > 0.5]
    dataframe = dataframe[dataframe['quantity'] > 0.01]
    if save_dataframe:
        dataframe.to_csv(paths.ACCOUNT_BALANCE_FILE, index=False)
    return dataframe


def get_candles(
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    limit: int = 100,
    interval: str = "4h",
    save_dataframe: bool = False,
) -> pd.DataFrame:
    """Get historical candle data of a cryptocurrency for price prediction and analysis.

    Args:
        coin_1 (str): Symbol of coin_1 (BTC, XRP, SHIB, DOGE, ADA)
        coin_2 (str): Symbol of coin_2 (BTC, USDT).
        limit (int, optional): maximum 1000 candles.
        interval (str, optional): [1m   5m  15m 30m 1h  2h  4h  6h  8h  1d  3d  1w  1M] m -> minutes, h -> hours, d -> days, w -> weeks, M -> months. Defaults to "4h".

    Returns:
        pd.DataFrame: The historical candle data of the coin market pair.
    """
    try:
        url = (
            URL_DICT["CANDLES_URL"]
            + f"?pair={get_markets_details(coin_1=coin_1,coin_2=coin_2)['pair']}&interval={interval}&limit={limit}"
        )
        response = requests.get(url, timeout=60)
        data = response.json()
        dataframe = pd.DataFrame.from_dict(data)
        dataframe["time"] = pd.to_datetime(dataframe["time"], unit="ms")

        if save_dataframe:
            dataframe.to_csv(f"{coin_1}_{coin_2}_candles.csv")
            return dataframe
        else:
            return dataframe
    except Exception as e:
        print(e)
        logging.info(f"Error in get_candles for {coin_1}: {e}")
        pass


def get_indicator_data(
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    market: str = "Binance",
    screener_name: str = "Crypto",
    interval: str = "4h",
) -> dict:
    """Get complete indicator data from Trading View.

    Args:
        symbol (_type_): Ticker Ex: "CIPLA", "TATAMOTORS", "XVGBTC", "BTCUSDT"
        market (str): Exchange ("NSE", "BSE", "Binance", "Huobi", "Kucoin")
        screener_name (str, optional): Either "India" or "Crypto". Defaults to "Crypto".
        interval (str, optional): Interval of chart "1m", "5m", "30m", "1h", "2h", "4h", "1d", "1W", "1M". Defaults to "4h".

    Returns:
        list: The indicator data for the market pair in an exchange.
    """
    try:
        trading_pair = TA_Handler(
            symbol=f"{coin_1+coin_2}",
            screener=f"{screener_name}",
            exchange=f"{market}",
            interval=INTERVAL_DICT[str(interval)],
        )
        return trading_pair.get_analysis().indicators
    except Exception as e:
        logging.info(f"Error in get_indicator_data for {coin_1}: {e}")
        market = constants.MARKETS[get_markets_details(coin_1="NAKA", coin_2=coin_2)["ecode"].values[0]]
        trading_pair = TA_Handler(
            symbol=f"{coin_1+coin_2}",
            screener=f"{screener_name}",
            exchange=f"{market}",
            interval=INTERVAL_DICT[str(interval)],
        )
        return trading_pair.get_analysis().indicators



def auto_trader(username: str = CONFIG["Owner"]["main_username"]):
    """Spin up an auto trading bot to trade for a particular username.

    Args:
        username (str): The name of the username to trade for.
    """
    unneccessary_coins = ["NOAH", "XEC", "INR"]
    current_orders = get_active_orders(username=username)["orders"]
    if len(current_orders) == 0:
        coins_currently_held = get_account_balance(username=username)
        for coin in unneccessary_coins:
            if coin in coins_currently_held:
                del coins_currently_held[coin]
        for coins in coins_currently_held.items():
            if (
                float(coins_currently_held[coins]["Locked Balance"]) == 0.0
                and float(coins_currently_held[coins]["Balance"]) > 1.0
            ):
                logging.info(f"Auto trader has the following {(coins)} in hand.")
                indi_data = get_indicator_data(coin_1=coins)
                if indi_data["RSI"] > 70:
                    logging.info(f"Selling {coins}")
                    send_mail(f"Sold {coins}", receiver="nadigvishal@gmail.com")


def parser_activated_bot() -> None:
    """A CLI to spin up an instance of the bot."""
    PARSER.add_argument(
        "-u",
        "--user_name",
        required=True,
        help="Username of the account to place the trade",
        type=str,
    )
    PARSER.add_argument("-s", "--symbol", help="The symbol of the stock to trade", required=True)
    PARSER.add_argument("-m", "--market", help="The market to trade", required=True)
    PARSER.add_argument("-S", "--Screener", help="Name of screener", required=True)
    PARSER.add_argument(
        "-i",
        "--interval",
        help="The chart interval to get the indicator",
        required=True,
    )
    args = PARSER.parse_args()
    bot_trader(
        username=args.user_name,
        symbol=args.symbol,
        market=args.market,
        screener_name=args.Screener,
        interval=args.interval,
    )


def plot_historical_data(
    coin_1: str = "BTC", coin_2: str = "USDT", interval: str = "1d", limit: int = 100
) -> pyplot:
    """Plot the historical price of any cryptocurreny to perform technical and fundamental analysis

    Args:
        coin_1 (str, optional): Ticker symbol of the crypto. Defaults to "BTC".
        coin_2 (str, optional): Ticker symbol of the comparison crypto. Defaults to "USDT".
        interval (str, optional): Time interval to get the price of the crypto. Defaults to "1d".
        limit (int, optional): The number of candles to fetch. Max limit = 1000. Defaults to 100.

    Returns:
        pyplot: Plot of the data
    """
    candle_data = get_candles(coin_1=coin_1, coin_2=coin_2, interval=interval, limit=limit)
    candle_data.plot(
        x="time",
        y=["close"],
        kind="line",
        figsize=(10, 10),
        xlabel="Time",
        ylabel=f"{coin_1}{coin_2} close price",
    )
    pyplot.show()


def send_mail(message: str, receiver: str = CONFIG["Owner"]["main_username"]) -> None:
    """Send mail function to send a mail and deliver the message.

    Args:
        message (str): The message to be sent through the mail.
    """
    smtp_object = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_object.starttls()
    smtp_object.login(
        CONFIG["trading"]["gmail_creds"]["username"], CONFIG["trading"]["gmail_creds"]["password"]
    )
    smtp_object.sendmail(CONFIG["trading"]["gmail_creds"]["username"], receiver, message)
    smtp_object.quit()


def price_tracker_mail(
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    price: float = 0.0,
    mail: bool = False,
    receiver: str = CONFIG["Owner"]["main_username"],
) -> str:
    """Get the current price of the coin_1 and send a mail

    Args:
        coin_1 (str, optional): The price of the coin you want to check. Defaults to "BTC".
        coin_2 (str, optional): The coin you want to check the price against. Defaults to "USDT".
        price (float, optional): The price above which if the price of coin_1 reaches you want to send the mail. Defaults to 0.0.
        mail (bool optional): Set to True to send mail of the price. Defaults to False.
        receiver (str, optional): The recipient of the mail. Must be a valid gmail ID. Defaults to
    """
    coin_details = get_ticker(coin_1=coin_1, coin_2=coin_2)
    logging.info(coin_details)
    if price != 0.0:
        if float(coin_details["last_price"]) > price:
            message = f"Price of {coin_details['market']} is more than {price} trading at {coin_details['last_price']}"
            if mail:
                send_mail(message=message, receiver=receiver)
                return message
            else:
                return message


def buy_sell_recommendation(
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    market: str = "Binance",
    screener_name: str = "Crypto",
    interval: str = "4h",
):
    """
    Generates a recommendation to buy or sell a cryptocurrency based on its RSI (Relative Strength Index) value.

    Parameters:
        coin_1 (str): The symbol of the first cryptocurrency (default is "BTC").
        coin_2 (str): The symbol of the second cryptocurrency (default is "USDT").
        market (str): The market where the cryptocurrencies are traded (default is "Binance").
        screener_name (str): The name of the screener used to gather indicator data (default is "Crypto").
        interval (str): The time interval for the indicator data (default is "4h").

    Returns:
        dict: A dictionary containing the recommendation code and message.
            - 200: The RSI value of the first cryptocurrency is over 70 and hence is in a strong SELL zone.
            - 200: The RSI value of the first cryptocurrency is less than 30 and hence is in a BUY zone.
    """
    try:
        indicator = get_indicator_data(
            coin_1=coin_1,
            coin_2=coin_2,
            market=market,
            screener_name=screener_name,
            interval=interval,
        )
        if indicator["RSI"] > 70:
            return {
                200: f"The RSI value of {coin_1} is over 70 and hence is in a strong SELL zone."
            }
        elif indicator["RSI"] < 30:
            return {200: f"The RSI value of {coin_1} is less than 30 and hence is in a BUY zone."}

    except Exception:
        pass


def candle_plot(coin_1: str = "BTC", coin_2: str = "USDT", interval: str = "4h", limit: str = 100):
    candle_data = get_candles(coin_1=coin_1, coin_2=coin_2, interval=interval, limit=limit)


def fetch_lend_orders(username: str = CONFIG["Owner"]["main_username"]):
    """
    Fetches the list of lend orders for the user.

    Args:
        username (str): The username of the user. Defaults to "main_username".

    Returns:
        dict: A dictionary containing the list of lend orders.
    """
    fetch_lend_orders_url = constants.URL_DICT["FETCH_LEND_ORDERS_URL"]
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    body = {"timestamp": time_stamp}
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(fetch_lend_orders_url, data=json_body, headers=headers)
    return response.json()


def lend_order(
    username: str = CONFIG["Owner"]["main_username"], coin_name: str = "USDT", amount: float = 0.0
):
    """
    Lends an amount of crypto to the exchange.

    Args:
        coin_name (str): The name of the coin to lend. Defaults to "USDT".
        amount (float): The amount of crypto to lend. Defaults to 0.0.

    Returns:
        None
    """
    lend_url = constants["URL_DICT"]["LEND_ORDERS_URL"]
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    body = {"timestamp": time_stamp}
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(lend_url, data=json_body, headers=headers)
    return response.json()


def settle_orders(username: str = CONFIG["Owner"]["main_username"]):
    """
    Setstle all orders for the user.

    Args:
        username (str): The username of the user. Defaults to "main_username".

    Returns:
        dict: A dictionary containing the list of settle orders.
    """
    settle_orders_url = constants["URL_DICT"]["SETTLE_ORDERS_URL"]
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    body = {"timestamp": time_stamp}
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(username=username)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(settle_orders_url, data=json_body, headers=headers)
    return response.json()


def crypto_price_tracker(save_dataframe: bool = False):
    """
    A function that iterates over all files in the current directory and prints the names of the files that have a '.json' extension and contain today's date in the file name.

    Parameters:
        username (str): The username of the user. Defaults to "vishalnadigofficial".

    Returns:
        None
    """
    get_market_data(save_dataframe=save_dataframe)

    initial_date = "2023-12-20"
    current_date = datetime.now().strftime("%Y-%m-%d")
    market_data_directory = constants.MARKET_DATA_DIRECTORY
    initial_market_data_file = os.path.join(
        market_data_directory, f"{initial_date}_market_data.csv"
    )
    current_market_data_file = os.path.join(market_data_directory, f"{current_date}_market_data.csv")
    if os.path.isfile(current_market_data_file):
        latest_market_data = pd.read_csv(current_market_data_file)
    else:
        get_price_of_coin_on_date(date=current_date, save_dataframe=True, all_coins=True)
        latest_market_data = pd.read_csv(current_market_data_file)
    if os.path.isfile(initial_market_data_file):
        initial_market_data = pd.read_csv(initial_market_data_file)
    else:
        get_price_of_coin_on_date(date=initial_date, save_dataframe=True, all_coins=True)
        initial_market_data = pd.read_csv(initial_market_data_file)

    date_difference = datetime.strptime(current_date, "%Y-%m-%d") - datetime.strptime(
        initial_date, "%Y-%m-%d"
    )
    week_number = date_difference // timedelta(days=7)
    file_name = f"week_{week_number}_change"
    change_df = {}

    for coin in initial_market_data["market"].values:
        contain_values = initial_market_data[initial_market_data["market"].str.contains(coin)]
        initial_price = contain_values["last_price"].values[0]
        current_price = latest_market_data[latest_market_data["market"].str.contains(coin)][
            "last_price"
        ]
        if len(current_price) != 1:
            pass
        else:
            change = round((current_price.values[0] - initial_price) / initial_price * 100, 2)
            change_df[coin] = {
                f"Week {week_number} Price": initial_price,
                f"Week {week_number} Current Price": current_price.values[0],
                f"Week {week_number} Change": f"{change}",
            }

    change_df = pd.DataFrame(change_df).T.join(initial_market_data["market"])
    change_df = change_df.drop("market", axis=1)
    price_change = pd.Series(change_df[f"Week {week_number} Change"])
    initial_market_data = initial_market_data.join(
        price_change, on="market", how="left", rsuffix="change"
    )
    if save_dataframe:
        initial_market_data.to_csv(
            os.path.join(market_data_directory, f"{file_name}.csv"), index=False
        )
        return {200: f"Created {file_name} successfully."}
    else:
        return initial_market_data


def get_price_of_coin_on_date(
    coin_1: str = "",
    coin_2: str = "USDT",
    date: str = "",
    number_of_days: int = 0,
    get_dataframe: bool = False,
    save_dataframe: bool = False,
    all_coins: bool = False,
):
    """
    Get the price of a coin on a specific date.

    Args:
        coin_1 (str): The symbol of the first coin.
        coin_2 (str): The symbol of the second coin.
        date (str): The date in DD-MM-YYYY format for which to retrieve the price.

    Returns:
        dict: A dictionary containing the price of the coin on the specified date.
    """
    print("Getting price of coin on date")
    if date and number_of_days:
        return {404: "Please provide either a date or number of days."}
    elif date or number_of_days:
        if all_coins:
            print("Getting all coins")
            complete_dataframe = pd.DataFrame()
            dataframe = get_market_data()
            date_required = datetime.now() - datetime.strptime(date, "%d-%m-%Y")
            count = 1
            for coins in dataframe["market"].values:
                if "USDT" in coins:
                    coin_1 = coins.split("USDT")[0]
                    coin_2 = "USDT"
                elif "BTC" in coins:
                    coin_1 = coins.split("BTC")[0]
                    coin_2 = "BTC"
                elif "VRA" in coins:
                    coin_1 = coins.split("VRA")[0]
                    coin_2 = coins.split("VRA")[1]
                try:
                    candle_dataframe = get_candles(
                        coin_1=coin_1, coin_2=coin_2, interval="1d", limit=date_required.days
                    )
                    complete_dataframe[count] = {
                        "market": coins,
                        "close": candle_dataframe["close"].values[candle_dataframe["time"] == date][0],
                        "time": candle_dataframe["time"].values[candle_dataframe["time"] == date][0],
                    }
                    count += 1

                except Exception as e:
                    pass
            complete_dataframe.T.to_csv(
                os.path.join(constants.MARKET_DATA_DIRECTORY, f"{date}_market_data.csv"), index=True
            )
        else:
            try:
                date_required = datetime.now() - datetime.strptime(date, "%d-%m-%Y")
                dataframe = get_candles(
                    coin_1=coin_1, coin_2=coin_2, interval="1d", limit=date_required.days
                )
                if save_dataframe:
                    dataframe.to_csv(f"{coin_1}{coin_2}_{date}.csv", index=False)
                if get_dataframe:
                    return dataframe
                return dataframe.loc[dataframe["time"] == date, "close"].values[0]
            except ValueError:
                return {404: "Invalid date format. Please use the format DD-MM-YYYY."}
    else:
        return {404: "Please provide either a date or a number of days."}


def get_market_indicator(
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    market: str = "Binance",
    screener_name: str = "Crypto",
    interval: str = "4h",
    all_coins: bool = False,
    save_dataframe: bool = False,
):
    """
    Retrieves market indicator data for a specified cryptocurrency pair.

    Parameters:
        coin_1 (str): The first cryptocurrency in the pair. Default is "BTC".
        coin_2 (str): The second cryptocurrency in the pair. Default is "USDT".
        market (str): The market where the indicator data will be retrieved from. Default is "Binance".
        screener_name (str): The name of the screener used to filter the indicator data. Default is "Crypto".
        interval (str): The time interval for the indicator data. Default is "4h".

    Returns:
        None
    """
    count = 1
    coins_dictionary = {}
    dataframe = pd.DataFrame()
    if all_coins:
        if os.path.exists(rf"{constants.MARKET_DATA_DIRECTORY}\2023-12-20_market_data.csv"):
            data = pd.read_csv(rf"{constants.MARKET_DATA_DIRECTORY}\2023-12-20_market_data.csv")
        else:
            url = URL_DICT["MARKET_DATA_URL"]
            response = requests.get(url)
            data = response.json()
        coins_dictionary = data["market"].to_dict()
        for coin in coins_dictionary.values():
            if "USDT" in coin:
                coin_1 = coin.split("USDT")[0]
                coin_2 = "USDT"
            elif "BTC" in coin:
                coin_1 = coin.split("BTC")[0]
                coin_2 = "BTC"
            elif "USDC" in coin:
                coin_1 = coin.split("USDC")[0]
                coin_2 = "USDC"
            ticker_data = get_ticker(coin_1=coin_1, coin_2=coin_2)
            candle_data = get_candles(coin_1=coin_1, coin_2=coin_2, interval="1d", limit=1)
            try:
                indicator_data_ = get_indicator_data(
                    coin_1=coin_1,
                    coin_2=coin_2,
                    market=market,
                    screener_name=screener_name,
                    interval=interval,
                )
                supports = [
                    indicator_data_["Pivot.M.Fibonacci.S1"],
                    indicator_data_["Pivot.M.Fibonacci.S2"],
                    indicator_data_["Pivot.M.Fibonacci.S3"],
                ]
                resistances = [
                    indicator_data_["Pivot.M.Fibonacci.R1"],
                    indicator_data_["Pivot.M.Fibonacci.R2"],
                    indicator_data_["Pivot.M.Fibonacci.R3"],
                ]
                dataframe[count] = {
                    "market": coin_1 + coin_2,
                    "RSI": indicator_data_["RSI"],
                    "EMA10": indicator_data_["EMA10"],
                    "EMA50": indicator_data_["EMA50"],
                    "EMA200": indicator_data_["EMA200"],
                    "Stoch.K": indicator_data_["Stoch.K"],
                    "Stoch.D": indicator_data_["Stoch.D"],
                    "MACD.macd": indicator_data_["MACD.macd"],
                    "MACD.signal": indicator_data_["MACD.signal"],
                    "Pivot": indicator_data_["Pivot.M.Fibonacci.Middle"],
                    "Supports": supports,
                    "Resistances": resistances,
                    "open": candle_data["open"],
                    "high": candle_data["high"],
                    "low": candle_data["low"],
                    "close": candle_data["close"],
                    "Current Price": ticker_data["last_price"],
                    "change_24h": ticker_data["change_24_hour"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            except Exception as e:
                pass
            count += 1
        dataframe = dataframe.T
        if save_dataframe:
            dataframe.to_csv(
                rf"{constants.MARKET_DATA_DIRECTORY}\market_indicator_data.csv", index=False
            )
            return dataframe
        return dataframe
    else:
        ticker_data = get_ticker(coin_1=coin_1, coin_2=coin_2)
        candle_data = get_candles(coin_1=coin_1, coin_2=coin_2, interval="1d", limit=1)
        indicator_data_ = get_indicator_data(
            coin_1=coin_1,
            coin_2=coin_2,
            market=market,
            screener_name=screener_name,
            interval=interval,
        )
        supports = [
            indicator_data_["Pivot.M.Fibonacci.S1"],
            indicator_data_["Pivot.M.Fibonacci.S2"],
            indicator_data_["Pivot.M.Fibonacci.S3"],
        ]
        resistances = [
            indicator_data_["Pivot.M.Fibonacci.R1"],
            indicator_data_["Pivot.M.Fibonacci.R2"],
            indicator_data_["Pivot.M.Fibonacci.R3"],
        ]
        dataframe[count] = {
            "market": coin_1 + coin_2,
            "RSI": indicator_data_["RSI"],
            "EMA10": indicator_data_["EMA10"],
            "EMA50": indicator_data_["EMA50"],
            "EMA200": indicator_data_["EMA200"],
            "Stoch.K": indicator_data_["Stoch.K"],
            "Stoch.D": indicator_data_["Stoch.D"],
            "MACD.macd": indicator_data_["MACD.macd"],
            "MACD.signal": indicator_data_["MACD.signal"],
            "Pivot": indicator_data_["Pivot.M.Fibonacci.Middle"],
            "Supports": supports,
            "Resistances": resistances,
            "open": candle_data["open"],
            "high": candle_data["high"],
            "low": candle_data["low"],
            "close": candle_data["close"],
            "Current Price": ticker_data["last_price"],
            "change_24h": ticker_data["change_24_hour"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        if save_dataframe:
            dataframe = pd.DataFrame(dataframe).to_csv(
                rf"{constants.MARKET_DATA_DIRECTORY}\{coin_1}{coin_2}_indicator_data.csv",
                index=False,
            )
            return dataframe
        return dataframe


def get_price_difference(coin: str = ""):
    oct_dataframe = pd.read_csv(rf"{constants.MARKET_DATA_DIRECTORY}\market_data_13-10-2023.csv")

    if coin:
        oct_dataframe = oct_dataframe.loc[oct_dataframe["market"].str.contains(coin + "USDT")]
        current_price = get_ticker(coin_1=coin, coin_2="USDT")

        oct_dataframe["current_price"] = current_price["last_price"].values[0]
        oct_dataframe["price_change"] = (
            float(oct_dataframe["current_price"].values[0])
            - float(oct_dataframe["close"].values[0])
        ) * 100.0
        return oct_dataframe

    return oct_dataframe


def get_buy_suggestions(
    full_dataframe: bool = False, save_dataframe: bool = False, number_of_coins: int = 10
):
    """
    Generates a dataframe of buy suggestions based on the latest market data.

    Parameters:
        full_dataframe (bool): If True, returns the full dataframe of buy suggestions. Defaults to False.
        save_dataframe (bool): If True, saves the buy suggestions dataframe to a CSV file. Defaults to False.
        number_of_coins (int): The number of top coins to include in the buy suggestions dataframe. Defaults to 10.

    Returns:
        DataFrame: The buy suggestions dataframe.
    """
    initial_date = "2023-12-20"
    current_date = datetime.now().strftime("%Y-%m-%d")
    market_data_directory = constants.MARKET_DATA_DIRECTORY
    date_difference = datetime.strptime(current_date, "%Y-%m-%d") - datetime.strptime(
        initial_date, "%Y-%m-%d"
    )
    week_number = date_difference // timedelta(days=7)
    file_name = os.path.join(market_data_directory, f"week_{week_number}_change.csv")

    if not os.path.exists(file_name):
        crypto_price_tracker(save_dataframe=True)

    latest_dataframe = pd.read_csv(file_name)

    buy_dataframe = latest_dataframe.loc[latest_dataframe["Week 1 Change"] < 0].sort_values(
        by="Week 1 Change", ascending=True
    )
    buy_dataframe = buy_dataframe[["market", "Week 1 Change"]]
    buy_dataframe.columns = ["coin", "change"]
    buy_dataframe.reset_index(drop=True, inplace=True)

    if save_dataframe:
        buy_dataframe.to_csv(rf"{constants.MARKET_DATA_DIRECTORY}\buy_suggestions.csv", index=False)
        if full_dataframe:
            return buy_dataframe
        elif number_of_coins > 0:
            return buy_dataframe.head(number_of_coins)
        else:
            return buy_dataframe.head(20)

    return buy_dataframe.head(20)


def get_weekly_portfolio_update(username: str = CONFIG["Owner"]["main_username"]):
    """
    Generates a weekly portfolio update for the user.

    Parameters:
        user (str): The username of the user. Defaults to "vishalnadigofficial".

    Returns:
        None
    """
    account_balance = get_account_balance(username=username)
    send_mail("Your weekly portfolio update is: " + account_balance)


def regular_updates(
    all_coins: bool = False,
    coin_list: list = [],
    save_dataframe: bool = False,
    interval: str = "4h",
):
    """
    Generates regular updates for the user.

    Parameters:
        all_coins (bool): If True, generates updates for all the coins. Defaults to False.
        coin_list (list): A list of coin symbols to generate updates for. Defaults to an empty list.
        save_dataframe (bool): If True, saves the dataframe to a CSV file. Defaults to False.
    """
    pass
    new_df = {}
    if all_coins and len(coin_list) > 0:
        return {404: "Error: all_coins and coin_list cannot be True at the same time."}
    elif all_coins:
        return crypto_price_tracker(save_dataframe=save_dataframe)
    elif len(coin_list) > 0:
        for coin in coin_list:
            pass


def price_follower(username=CONFIG["Owner"]["main_username"]):
    order_history_dataframe = account_trade_history(limit=100)
    order_history_dataframe = order_history_dataframe[order_history_dataframe['side'] == 'buy']
    if os.path.exists(paths.ACCOUNT_BALANCE_FILE):
        account_balance = pd.read_csv(paths.ACCOUNT_BALANCE_FILE)
    else:
        account_balance = get_account_balance(username=username, save_dataframe=True)
    # account_balance.to_json(os.path.join(os.path.expanduser("~"), fr"{paths.MARKET_DATA_DIRECTORY}/account_balance.json"))
    # print(account_balance)
    print(account_balance)


if __name__ == "__main__":
    # price_follower()
    # print(get_account_balance(save_dataframe = True))
    # print(get_keys(username="vishalnadig")[1])
    # print(account_trade_history(limit= 1000))
    # print(get_keys(username="vishalnadig"))
    # account_trade_history(username="vishalnadig")
    # print(initialize())
    # print(get_active_orders(username="vishalnadig"))
    # print(get_market_data()['market'].values)
    # print(get_markets_details(all_coins=True))
    print(get_indicator_data(coin_1="NAKA"))
    # crypto_price_tracker(save_dataframe=True)  # Use this
    # print(get_candles(coin_1="1000SAT", coin_2="USDT", interval="4h", limit=1))
    # print(get_market_indicator(all_coins=True))
    # print(get_indicator_data(coin_1="1000SATS", coin_2="USDT", market="Binance", screener_name="Crypto", interval="4h"))
    # print(get_price_of_coin_on_date(date="13-10-2023", all_coins=True))
    # print(fetch_lend_orders())
    # account_trade_history()
    # print(get_keys(username="vishalnadig"))
    # get_price_difference("NEAR")
    # print(get_buy_suggestions())
    ...
