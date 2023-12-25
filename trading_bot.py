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
import database_handler
import trading_bot_auth
from paths import paths

# TODO: Encrypt regardless of where the keys are coming from.

PARSER = argparse.ArgumentParser()
CONFIG_FILE = paths.CONFIG_FILE
ORDER_HISTORY_FILE = paths.ORDER_HISTORY_FILE
LOGFILE = paths.LOGFILE
TODAY = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
SCREENER_LIST = constants.SCREENER_LIST
API_DICTS = constants.API_DICTS
INTERVAL_DICT = constants.INTERVAL_DICT
URL_DICT = constants.URL_DICT
REMOVE_CURRENCIES = constants.REMOVE_CURRENCIES


logging.basicConfig(
    level=logging.INFO,
    filemode="a",
    filename=paths.LOGFILE,
    format="%(asctime)s;%(levelname)s;%(message)s",
)


with open(CONFIG_FILE, "r+", encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)


def get_keys(first_name: str = "", last_name: str = "", username: str = "") -> tuple:
    """Get API key and secret key for the specified username. If username is not mentioned then, first name and last name of the username can be used to retrieve the keys.

    Args:
        first_name (str, optional): First name of the username. Defaults to "".
        last_name (str, optional): Last name of the username. Defaults to "".
        username (str, optional): Username to retrieve the keys. Defaults to "".

    Returns:
        tuple: The API key and the secret key.
    """
    # if first_name and last_name != "":
    #     username = first_name + last_name
    # else:
    #     username = username.lower()
    #     username = username.replace(" ", "")
    # api_key = CONFIG["trading"]["accounts"][username]["api_key"]
    # secret_key = CONFIG["trading"]["accounts"][username]["secret_key"]
    # return api_key, secret_key
    return trading_bot_auth.get_credentials_config_file(
        first_name=first_name, last_name=last_name, username=username
    )


def add_keys(
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
    # username = first_name + last_name
    # username = username.lower()
    # username = username.replace(" ", "")
    # dict_update = CONFIG
    # dict_dump = {
    #     "username": first_name.title() + last_name.title(),
    #     "email": email,
    #     "api_key": api_key,
    #     "secret_key": secret_key,
    #     "google_auth_key": google_auth_key,
    # }

    # if username not in dict_update["trading"]["accounts"]:
    #     dict_update["trading"]["accounts"][username] = dict_dump
    #     with open(CONFIG_FILE, "w", encoding="utf-8") as file:
    #         yaml.safe_dump(dict_update, file)
    #     return {200: "User added!"}
    # else:
    #     return {404: "Error username already present!"}
    return trading_bot_auth.add_keys_config_file(
        first_name=first_name,
        last_name=last_name,
        api_key=api_key,
        secret_key=secret_key,
        email=email,
        google_auth_key=google_auth_key,
    )


def update_keys(
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
):
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
    # username = first_name + last_name
    # username = username.lower()
    # username = username.replace(" ", "")
    # dict_update = CONFIG
    # dict_dump = {
    #     "username": first_name.title() + last_name.title(),
    #     "email": email,
    #     "api_key": api_key,
    #     "secret_key": secret_key,
    #     "google_auth_key": google_auth_key,
    # }
    # if username not in dict_update["trading"]["accounts"]:
    #     return {404: "Error username not present!"}
    # else:
    #     dict_update["trading"]["accounts"][username] = dict_dump
    #     with open(CONFIG_FILE, "w", encoding="utf-8") as file:
    #         yaml.safe_dump(dict_update, file)
    #     return {200: "User updated!"}
    return trading_bot_auth.update_keys_config_file(
        first_name=first_name,
        last_name=last_name,
        api_key=api_key,
        secret_key=secret_key,
        email=email,
        google_auth_key=google_auth_key,
    )


def delete_keys(first_name: str, last_name: str, username: str):
    """
    Delete the keys for a specific username in the trading bot configuration file.

    Parameters:
        first_name (str): The first name of the username.
        last_name (str): The last name of the username.
        username (str): The username of the username.

    Returns:
        None
    """
    return trading_bot_auth.delete_keys_config_file(
        first_name=first_name, last_name=last_name, username=username
    )


def get_ticker(coin_1: str = "BTC", coin_2: str = "USDT") -> dict:
    """Get the ticker details of the coin

    Args:
        coin_1 (str, optional): The coin to get the ticker details of. Defaults to "BTC".
        coin_2 (str, optional): The coin against which to get the ticker details of. Defaults to "USDT".

    Returns:
        dict: The dictionary of the coins details
    """
    url = URL_DICT["TICKER_URL"]
    response = requests.get(url)
    data = response.json()
    coins_dictionary = {}
    for coins in data:
        if coins["market"] == coin_1 + coin_2:
            coins["unix_timestamp"] = coins["timestamp"]
            coins["timestamp"] = datetime.fromtimestamp(coins["timestamp"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            return coins


def get_market_data(currencies_to_include: list = []) -> dict:
    # TODO: Add Currencies to include feature
    """Get the market data of all coins in the market currently.

    Args:
        ticker (str, optional): The coin to get the market data of. Defaults to "BTCUSDT".

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
    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], unit="s") - timedelta(
        hours=7, minutes=0
    )
    dataframe.to_csv(
        rf"C:\Users\nadig\git\crypto_market_data\{datetime.now().strftime('%Y-%m-%d')}_market_data.csv"
    )


def get_markets_details(
    coin_1: str = "", coin_2: str = "", coins_list: list = [], all_coins: bool = False
) -> dict:
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
    coins_dictionary = {}

    if all_coins:
        for coins in data:
            if coin_2 in coins["symbol"]:
                coins_list.append(coins)
        return coins_list
    elif len(coins_list) == 0:
        for coins in data:
            if coins["symbol"] == coin_1 + coin_2:
                return coins
        for coin in coins_list:
            for coins in data:
                if coins["symbol"] == coin + "USDT":
                    coins_dictionary[coins["symbol"]] = coins
        return coins_dictionary


def place_buy_limit_order(
    username: str = CONFIG["Owner"]["alt_username"],
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
    if 401 in response.json().values():
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
    logging.info("Written to order history file!")
    file.close()
    return data


def place_sell_limit_order(
    username: str = CONFIG["Owner"]["alt_username"],
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
    if 401 in response.json().values():
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
    logging.info("Written to order history file!")
    file.close()


def place_market_buy_order(
    username: str = CONFIG["Owner"]["alt_username"],
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
    if 401 in response.json().values():
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
        logging.info("Written to file")
    return data


def place_market_sell_order(
    username: str = CONFIG["Owner"]["alt_username"],
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
    if 401 in response.json().values():
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
    logging.info("Written to order history file!")
    file.close()
    return response.json()


def create_multiple_orders(
    username: str = CONFIG["Owner"]["alt_username"], orders: list = []
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
    if 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    logging.info(response.json())
    return response.json()


def get_active_orders(username: str = CONFIG["Owner"]["alt_username"]) -> dict:
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
    if 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    return response.json()


def account_trade_history(username: str = CONFIG["Owner"]["alt_username"]) -> dict:
    """Get the account trade history of the username.

    Args:
        username (str): The username of the account for which the trade history is to be fetched.

    Returns:
        dict: The history of trades made by the username.
    """
    secret_bytes = bytes(get_keys(username=username)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))

    body = {"from_id": 352622, "limit": 50, "timestamp": time_stamp}

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
    if 401 in response.json().values():
        raise Exception("Unauthorized user credentials")

    with open("order_history.csv", "w") as file:
        response.json().to_csv(file)

    return response.json()


def cancel_order(username: str = CONFIG["Owner"]["alt_username"], ids: str = "") -> None:
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
    if 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    logging.info(response.json())
    return response.json()


def cancel_all_orders(username: str = CONFIG["Owner"]["alt_username"]) -> None:
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
    if 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    return response.json()


def cancel_multiple_by_ids(username: str = CONFIG["Owner"]["alt_username"], ids: list = []) -> None:
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
    if 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    return response.json()


def edit_price_of_orders(
    username: str = CONFIG["Owner"]["alt_username"], ids: list = [], price: float = ""
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
    if 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    return response.json()


def bot_trader(
    username: str = CONFIG["Owner"]["alt_username"],
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
    count = 0
    logging.info(f"""{coin_1}{coin_2} Bot Started for {username} at {datetime.now()}!""")
    indicator_data_ = indicator_data(
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
            indicator_data_ = indicator_data(
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
            indicator_data_ = indicator_data(
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
        data_frame = pd.DataFrame.from_dict(data)
        data_frame = data_frame.sort_values("market")
        # data_frame = data_frame[columns]
        data_frame["timestamp"] = pd.to_datetime(data_frame["timestamp"], unit="s") + timedelta(
            hours=5, minutes=30
        )
        for currency in REMOVE_CURRENCIES:
            data_frame = data_frame[~data_frame.market.str.endswith(currency)]
        data_frame = data_frame.reset_index(drop=True)
        data_frame = data_frame.sort_index(ascending=True, axis=0)
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


def get_account_balance(username: str = CONFIG["Owner"]["alt_username"]) -> dict:
    """Get the account balance of the username.

    Args:
        username (str, optional): The username of the account to get the balance of. Defaults to CONFIG['Owner']['alt_username'].

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
    if 401 in response.json().values():
        raise Exception("Unauthorized user credentials")
    dataframe = pd.DataFrame(response.json())
    price_list = []
    # dataframe.to_csv("account_balance.csv")
    dataframe = dataframe[dataframe["balance"] != "0.0"]
    for coin in dataframe["currency"]:
        if coin == "USDT":
            details = get_ticker(coin_1=coin, coin_2="INR")
            price_list.append(details["last_price"])
        details = get_ticker(coin_1=coin)
        if details != None:
            price_list.append(details["last_price"])
    dataframe["current_price"] = price_list
    dataframe["timestamp"] = datetime.fromtimestamp(time_stamp / 1000)
    return dataframe


def get_candles(
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    limit: int = 100,
    interval: str = "4h",
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
    url = (
        URL_DICT["CANDLES_URL"]
        + f"?pair={get_markets_details(coin_1=coin_1,coin_2=coin_2)['pair']}&interval={interval}&limit={limit}"
    )
    response = requests.get(url, timeout=60)
    data = response.json()
    dataframe = pd.DataFrame.from_dict(data)
    # current_time = datetime.datetime.fromtimestamp(unix_timestamp)
    dataframe["time"] = pd.to_datetime(dataframe["time"], unit="ms")
    return dataframe


def indicator_data(
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    market: str = "Binance",
    screener_name: str = "Crypto",
    interval: str = "4h",
) -> list:
    """Get complete indicator data from Trading View.

    Args:
        symbol (_type_): Ticker Ex: "CIPLA", "TATAMOTORS", "XVGBTC", "BTCUSDT"
        market (str): Exchange ("NSE", "BSE", "Binance", "Huobi", "Kucoin")
        screener_name (str, optional): Either "India" or "Crypto". Defaults to "Crypto".
        interval (str, optional): Interval of chart "1m", "5m", "30m", "1h", "2h", "4h", "1d", "1W", "1M". Defaults to "4h".

    Returns:
        list: The indicator data for the market pair in an exchange.
    """

    trading_pair = TA_Handler(
        symbol=f"{coin_1+coin_2}",
        screener=f"{screener_name}",
        exchange=f"{market}",
        interval=INTERVAL_DICT[str(interval)],
    )
    return trading_pair.get_analysis().indicators


def auto_trader(username: str = CONFIG["Owner"]["alt_username"]):
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
                indi_data = indicator_data(coin_1=coins)
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


def get_rsi_signal(coin_1, coin_2, screener_name, market, interval):
    """
    Generates a signal based on the Relative Strength Index (RSI) indicator.

    Args:
        coin_1 (str): The first coin symbol.
        coin_2 (str): The second coin symbol.
        screener_name (str): The name of the screener.
        market (str): The name of the market.
        interval (str): The interval for calculating the RSI value.

    Returns:
        None
    """
    trading_pair = TA_Handler(
        symbol=f"{coin_1+coin_2}",
        screener=f"{screener_name}",
        exchange=f"{market}",
        interval="4h",
    )
    # Get RSI value for the last 14 periods on the daily timeframe
    rsi = trading_pair.get_analysis().indicators["RSI"]

    # Print BUY if RSI is below 30, SELL if RSI is above 70, otherwise do nothing
    if rsi < 30:
        return "BUY"
    elif rsi > 70:
        return "SELL"


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


def send_mail(message: str, receiver: str = CONFIG["Owner"]["alt_username"]) -> None:
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


def price_tracker(
    coin_1: str = "BTC",
    coin_2: str = "USDT",
    price: float = 0.0,
    mail: bool = False,
    receiver: str = CONFIG["Owner"]["alt_username"],
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
        indicator = indicator_data(
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


def fetch_lend_orders(username: str = CONFIG["Owner"]["alt_username"]):
    """
    Fetches the list of lend orders for the user.

    Args:
        username (str): The username of the user. Defaults to "alt_username".

    Returns:
        dict: A dictionary containing the list of lend orders.
    """
    fetch_lend_orders_url = constants["FETCH_LEND_ORDERS_URL"]
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
    username: str = CONFIG["Owner"]["alt_username"], coin_name: str = "USDT", amount: float = 0.0
):
    """
    Lends an amount of crypto to the exchange.

    Args:
        coin_name (str): The name of the coin to lend. Defaults to "USDT".
        amount (float): The amount of crypto to lend. Defaults to 0.0.

    Returns:
        None
    """
    lend_url = constants["LEND_ORDERS_URL"]
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


def settle_orders(username: str = CONFIG["Owner"]["alt_username"]):
    """
    Setstle all orders for the user.

    Args:
        username (str): The username of the user. Defaults to "alt_username".

    Returns:
        dict: A dictionary containing the list of settle orders.
    """
    settle_orders_url = constants["SETTLE_ORDERS_URL"]
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


def get_market_cap(coin_name: str = "BTC"):
    """
    Retrieves the market capitalization for a given cryptocurrency.

    Args:
        coin_name (str): The name of the cryptocurrency. Defaults to "BTC".

    Returns:
        None
    """
    pass


def price_tracker(username: str = CONFIG["trading"]["accounts"]["vishalnadigofficial"]):
    """
    A function that iterates over all files in the current directory and prints the names of the files that have a '.json' extension and contain today's date in the file name.

    Parameters:
        None

    Returns:
        None
    """
    get_market_data()

    initial_date = "2023-12-20"
    current_date = datetime.now().strftime("%Y-%m-%d")
    base_directory = r"C:\Users\nadig\git\crypto_market_data"
    initial_market_data_file = os.path.join(base_directory, f"{initial_date}_market_data.csv")

    for file in os.listdir(base_directory):
        if file.endswith(".csv") and file.startswith(current_date):
            current_market_data_file = os.path.join(base_directory, file)
            initial_market_data = pd.read_csv(initial_market_data_file)
            latest_market_data = pd.read_csv(current_market_data_file)

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
                f"Week {week_number} Change": f"{change} %",
            }

    change_df = pd.DataFrame(change_df).T.join(initial_market_data["market"])
    change_df = change_df.drop("market", axis=1)
    price_change = pd.Series(change_df[f"Week {week_number} Change"])
    initial_market_data = initial_market_data.join(
        price_change, on="market", how="left", rsuffix="change"
    )
    initial_market_data.to_csv(os.path.join(base_directory, f"{file_name}.csv"), index=False)


if __name__ == "__main__":
    # get_market_data()
    price_tracker()
    # account_trade_history()
    # print(get_keys(username="vishalnadig"))
