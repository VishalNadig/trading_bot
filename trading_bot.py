"""A crypto trading bot to place buy and sell orders automatically"""
import argparse
import csv
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta

import pandas as pd
import requests
import yaml
from matplotlib import pyplot
from tradingview_ta import TA_Handler

import constants
from paths import paths

INITIAL_INVESTMENT = constants.INITIAL_INVESTMENT  # In BTC
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

# HISTORY_COLS = ["market", "last_price", "quantity", "type", "side", "timestamp", 'order_id']
# history_file = pd.DataFrame(columns=HISTORY_COLS)
# history_file.to_csv(ORDER_HISTORY_FILE, mode="w")

logging.basicConfig(
    level=logging.INFO,
    filemode="a",
    filename=paths.LOGFILE,
    format="%(asctime)s;%(levelname)s;%(message)s",
)

with open(CONFIG_FILE, "r+", encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)


def get_keys(first_name: str = "", last_name: str = "", user: str = "") -> tuple:
    """Get API key and secret key for the specified user. If user is not mentioned then, first name and last name of the user can be used to retrieve the keys.

    Args:
        first_name (str, optional): First name of the user. Defaults to "".
        last_name (str, optional): Last name of the user. Defaults to "".
        user (str, optional): Username to retrieve the keys. Defaults to "".

    Returns:
        tuple: The API key and the secret key.
    """
    if first_name and last_name != "":
        user = first_name + last_name
    else:
        user = user.lower()
        user = user.replace(" ", "")
    api_key = CONFIG["trading"]["accounts"][user]["api_key"]
    secret_key = CONFIG["trading"]["accounts"][user]["secret_key"]
    return api_key, secret_key


def add_keys(
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
) -> None:
    """Add API key and the secret key for a new user. If the user already exists. Return exception.

    Args:
        first_name (str, optional): First name of the user. Defaults to "".
        last_name (str, optional): Last name of the user. Defaults to "".
        api_key (str, optional): API key of the user.
        secret_key (str, optional): API secret of the user.
    """
    user = first_name + last_name
    user = user.lower()
    user = user.replace(" ", "")
    dict_update = CONFIG
    dict_dump = {
        "username": first_name.title() + last_name.title(),
        "email": email,
        "api_key": api_key,
        "secret_key": secret_key,
        "google_auth_key": google_auth_key,
    }

    if user not in dict_update["trading"]["accounts"]:
        dict_update["trading"]["accounts"][user] = dict_dump
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            yaml.safe_dump(dict_update, file)
        return {200: "User added!"}
    else:
        return {404: "Error user already present!"}


def get_ticker(coin_1: str = "BTC", coin_2: str = "USDT"):
    url = "https://api.coindcx.com/exchange/ticker"
    response = requests.get(url)
    data = response.json()
    for coins in data:
        if coins['market'] == coin_1+coin_2:
            return coins



def get_markets_details(coin_1: str = "BTC", coin_2: str = "USDT") -> dict:
    url = URL_DICT["MARKET_DETAILS_URL"]
    response = requests.get(url)
    data = response.json()
    for coins in data:
        if coins['symbol'] == coin_1+coin_2:
            return coins


def get_market_data(currency: str = "") -> pd.DataFrame:
    """Get market data and information. We can get the market data and the information of all the currencies or only the specified currencies if they are passed as the argument to this function.

    Args:
        user (str, optional): _description_. Defaults to "".
        currency (str, optional): _description_. Defaults to "".

    Returns:
        pd.DataFrame: _description_
    """
    # TODO: Add the currency list to get the info about the specified currencies only.
    data = requests.get(URL_DICT["MARKET_DATA_URL"], timeout=60).json()
    data_frame = pd.DataFrame.from_dict(data)
    data_frame = data_frame.sort_values("market")
    columns = data_frame.columns.tolist()
    columns = [
        "market",
        "last_price",
        "bid",
        "ask",
        "volume",
        "high",
        "low",
        "timestamp",
    ]
    data_frame = data_frame[columns]
    data_frame["timestamp"] = pd.to_datetime(data_frame["timestamp"], unit="s") + timedelta(
        hours=5, minutes=30
    )
    for currencies in REMOVE_CURRENCIES:
        data_frame = data_frame[~data_frame.market.str.endswith(currencies)]
    data_frame = data_frame.reset_index(drop=True)
    data_frame = data_frame.sort_index(ascending=True, axis=0)
    # data_frame.to_csv("market_data.csv", mode="w")
    if currency != "":
        if data_frame["market"].str.contains(currency).any():
            print(data_frame)
    else:
        return data_frame


def place_buy_limit_order(user: str = "vishalnadigofficial", coin_1: str = "BTC", coin_2: str = "USDT", price: float = 0.023, total_quantity: float = 450) -> None:
    """Place a buy limit order on the market pair specified.

    Args:
        user (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        price (float): The price at which to buy.
        total_quantity (float): The number of stocks or coins to buy.
    """
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
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
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(URL_DICT["NEW_ORDER_URL"], data=json_body, headers=headers)
    data = response.json()
    print(data)
    logging.info(data)
    with open(ORDER_HISTORY_FILE, "a", newline="") as file:
        csvwrite = csv.writer(file, dialect="excel")
        csvwrite.writerow(
            [
                "",
                coin_1+coin_2,
                total_quantity,
                "market_order",
                "buy",
                TODAY,
            ]
        )
    logging.info("Written to order history file!")
    file.close()


def place_sell_limit_order(user: str = "vishalnadigofficial", coin_1: str = "BTC", coin_2: str = "USDT", price: float = 0.25, total_quantity: float = 450.0) -> None:
    """Place a buy limit order on the market pair specified.

    Args:
        user (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        price (float): The price at which to sell.
        total_quantity (float): The number of stocks or coins to sell.
    """
    # TODO: Find a way to make the price argument to be dynamic for the coins
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    # message = (
    #     f"Sell order of {total_quantity} for market {market} placed at {price} price"
    # )
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
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(URL_DICT["NEW_ORDER_URL"], data=json_body, headers=headers)
    data = response.json()
    logging.info(data)
    with open(ORDER_HISTORY_FILE, "a", newline="") as file:
        csvwrite = csv.writer(file, dialect="excel")
        csvwrite.writerow(
            [
                "",
                coin_1+coin_2,
                total_quantity,
                "market_order",
                "sell",
                TODAY,
            ]
        )
    logging.info("Written to order history file!")
    file.close()


def place_market_buy_order(user: str = "VishalNadigOfficial", coin_1: str = "BTC", coin_2: str = "USDT", total_quantity: float = 450) -> None:
    """Place a buy market order on the market pair specified. The order is placed at the current market price. This order gets executed immediately.

    Args:
        user (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        total_quantity (float): The number of stocks or coins to buy.
    """
    # TODO: Find a way to get the total quantity to sell for each coin dynamically.
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
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
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(URL_DICT["NEW_ORDER_URL"], data=json_body, headers=headers)
    data = response.json()
    print(data)
    # logging.info(data)
    with open(ORDER_HISTORY_FILE, "a", newline="") as file:
        csvwrite = csv.writer(file, dialect="excel")
        csvwrite.writerow(
            [
                "",
                coin_1+coin_2,
                total_quantity,
                "market_order",
                "buy",
                TODAY,
            ]
        )
    print("Written to file")
    file.close()


def place_market_sell_order(user: str = "vishalnadigofficial", coin_1: str = "BTC", coin_2: str = "USDT", total_quantity: float = 450.0) -> None:
    """Place a sell market order on the market pair specified. The order is placed at the current market price. This order gets executed immediately.

    Args:
        user (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        total_quantity (float): The number of stocks or coins to buy.
    """
    # TODO: Find a way to get the total quantity to sell for each coin dynamically.

    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
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
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(URL_DICT["NEW_ORDER_URL"], data=json_body, headers=headers)
    data = response.json()
    logging.info(data)
    with open(ORDER_HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        csvwrite = csv.writer(file, dialect="excel")
        csvwrite.writerow(
            [
                "",
                coin_1+coin_2,
                total_quantity,
                "market_order",
                "sell",
                TODAY,
            ]
        )
    logging.info("Written to order history file!")
    file.close()


def create_multiple_orders(user: str = "vishalnadigofficial", orders: list = []) -> None:
    """Create multiple orders at once.

    Args:
        user (str): The username of the account to place the order in.
        orders (str): The different orders that need to be placed for the user.
    """
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
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
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }

    response = requests.post(
        URL_DICT["CREATE_MULTIPLE_ORDERS_URL"], data=json_body, headers=headers
    )
    data = response.json()
    print(data)


def get_active_orders(user: str = "vishalnadigofficial") -> dict:
    """Get the current buy or sell active orders for the user.

    Args:
        user (str): The username of the account to get the active orders from.

    Returns:
        dict: List of all the active orders
    """
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
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
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["ACTIVE_ORDERS_URL"], data=json_body, headers=headers, timeout=60
    )
    data = response.json()
    return data


def account_trade_history(user: str = "vishalnadigofficial") -> dict:
    """Get the account trade history of the user.

    Args:
        user (str): The username of the account for which the trade history is to be fetched.

    Returns:
        dict: The history of trades made by the user.
    """
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))

    body = {"from_id": 352622, "limit": 50, "timestamp": time_stamp}

    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["ACCOUNT_TRADE_HISTORY_URL"], data=json_body, headers=headers, timeout=60
    )
    data = response.json()
    print(data)
    return data


def cancel_order(user: str = "vishalnadigofficial", ids: str = "") -> None:
    """Cancel a particular order of the user.

    Args:
        user (str): The username of the account for whom the order needs to be cancelled.
        id (_type_): The order id.
    """
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")

    time_stamp = int(round(time.time() * 1000))
    body = {"id": f"{ids}", "timestamp": time_stamp}  # Enter your Order ID here.
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["CANCEL_ONE_ACTIVE_ORDER_URL"], data=json_body, headers=headers, timeout=60
    )
    data = response.json()
    print(data)


def cancel_all_orders(user: str = "vishalnadigofficial") -> None:
    """Cancel all the active orders of the user.

    Args:
        user (str): The username of the account for which the order needs to be cancelled.
    """
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
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
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["CANCEL_ALL_ACTIVE_ORDERS_URL"], data=json_body, headers=headers, timeout=60
    )
    data = response.json()
    print(data)


def cancel_multiple_by_ids(user: str = "vishalnadigofficial", ids: list = []) -> None:
    """Cancel multiple orders given by the list of ids for a particular user.

    Args:
        user (str): The username of the account for which the orders need to be cancelled.
        ids (list): The list of order ids to cancel.
    """
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")

    body = {
        "ids": ids
    }

    json_body = json.dumps(body, separators=(",", ":"))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url = "https://api.coindcx.com/exchange/v1/orders/cancel_by_ids"

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }

    response = requests.post(url, data=json_body, headers=headers, timeout=60)
    data = response.json()
    print(data)


def edit_price_of_orders(user: str = "vishalnadigofficial", ids: list = [], price: float = "") -> None:
    """Edit the buy or sell price of the orders.

    Args:
        user (str): The username of the account for which the price needs to be edited.
        ids (_type_): The order id for which the price needs to be edited
        price (float): _description_
    """

    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
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
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["EDIT_PRICE_URL"], data=json_body, headers=headers, timeout=60
    )
    data = response.json()
    print(data)


def bot_trader(user: str = "VishalNadigOfficial", coin_1: str = "BTC", coin_2: str = "USDT", market: str = "Binance", screener_name: str = "Crypto", interval: str = "4h") -> None:
    """Execute trades automatically 24/7 based on input parameters

    Args:
        user (str): The username of the account to auto_trade in.
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
    print(f"""{coin_1}{coin_2} Bot Started for {user} at {datetime.now()} !""") #datetime.now().strftime('%Y-%m-%d %H:%M:%s')
    logging.info(f"""{coin_1}{coin_2} Bot Started for {user} at {datetime.now()}!""")
    indicator_data_ = indicator_data(
        coin_1 = coin_1,coin_2=coin_2, market=market, screener_name=screener_name, interval=interval
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
                coin_1 = coin_1,
                coin_2=coin_2,
                market=market,
                screener_name=screener_name,
                interval=interval,
            )
            account_balance = get_account_balance(user=user)
        except Exception as exception:
            logging.error(exception)
            time.sleep(60)
            data = get_candles(coin_1=coin_1, coin_2=coin_2)
            indicator_data_ = indicator_data(
                coin_1 = coin_1,
                coin_2=coin_2,
                market=market,
                screener_name=screener_name,
                interval=interval,
            )
            account_balance = get_account_balance(user=user)

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
        # data_frame = pd.DataFrame.from_dict(data)
        # data_frame = data_frame.sort_values("market")
        # # data_frame = data_frame[columns]
        # data_frame["timestamp"] = pd.to_datetime(data_frame["timestamp"], unit="s") + timedelta(
        #     hours=5, minutes=30
        # )
        # for currency in REMOVE_CURRENCIES:
        #     data_frame = data_frame[~data_frame.market.str.endswith(currency)]
        # data_frame = data_frame.reset_index(drop=True)
        # data_frame = data_frame.sort_index(ascending=True, axis=0)
        current_price = data["close"]
        print(current_price)
        # SET BUY PRICE, SELL PRICE AND STOP LOSS CONDITIONS
        # if current_price < pivot and current_price > supports[0] and current_price < close_price:
        #     buy_price = supports[0]
        #     stop_loss = supports[0] - int(0.01 * buy_price)
        #     sell_price = pivot
        # elif (
        #     current_price < supports[0]
        #     and current_price > supports[1]
        #     and current_price < close_price
        # ):
        #     buy_price = supports[1]
        #     stop_loss = supports[1] - int(0.01 * buy_price)
        #     sell_price = supports[0]
        # elif (
        #     current_price < supports[1]
        #     and current_price > supports[2]
        #     and current_price < close_price
        # ):
        #     buy_price = supports[2]
        #     stop_loss = supports[2] - int(0.01 * buy_price)
        #     sell_price = supports[1]
        # elif current_price < supports[2]:
        #     pass
        # order_size = 0.33 * account_balance
        # if (  # BUY CONDITIONS
        #     float(current_price) == buy_price and not open_position and order_size > min_order_value
        # ) or (rsi < 37 and not open_position and order_size > min_order_value):
        #     place_buy_limit_order(
        #         user=user, market=market, price=buy_price, total_quantity=order_size
        #     )
        #     logging.info(
        #         f"Buy Order placed! for {coin_1+coin_2} at price {buy_price}. Stop loss is {stop_loss}"
        #     )
        #     open_position = True
        # if (  # SELL CONDITIONS
        #     (float(current_price) == sell_price and open_position)
        #     or float(current_price) == stop_loss
        #     or (rsi > 60 and open_position)
        # ):
        #     place_sell_limit_order(
        #         user=user, market=market, price=sell_price, total_quantity=order_size
        #     )
        #     logging.info(f"Sold {market} for: {sell_price}")
        #     logging.info(f"The current account balance is: {account_balance} BTC")
        #     open_position = False
        #     no_of_trades += 1
        #     profit = ((sell_price - buy_price) / buy_price) * (100)
        #     logging.info(f"made {profit}% profits!")


def get_account_balance(user: str = "VishalNadigOfficial") -> dict:
    """Get the account balance of the user.

    Args:
        user (str, optional): The username of the account to get the balance of. Defaults to "VishalNadigOfficial".

    Returns:
        dict: The dictionary of the account balances of all the currencies.
    """

    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    time_stamp = int(round(time.time() * 1000))
    body = {"timestamp": time_stamp}
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }

    response = requests.post(
        URL_DICT["ACCOUNT_BALANCE_URL"], data=json_body, headers=headers, timeout=60
    )
    json_data = response.json()
    dataframe = pd.DataFrame(json_data)
    # dataframe.to_csv("account_balance.csv")
    account_balance = dataframe["balance"]
    for data in json_data:
        if (
            float(data["balance"]) > 0.1
            or float(data["locked_balance"]) > 0.1
            or "BTC" in data["currency"]
        ):
            dataframe[data["currency"]] = {
                "Balance": data["balance"],
                "Locked Balance": data["locked_balance"],
            }
    dataframe = dataframe[dataframe['balance'] != 0.0]
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
    dataframe["time"] = pd.to_datetime(dataframe["time"], unit="ms")
    return dataframe


def indicator_data(
    coin_1: str = "BTC", coin_2: str = "USDT", market: str= "Binance", screener_name: str = "Crypto", interval: str = "4h"
) -> list:
    """Get complete indicator data from Trading View.

    Args:
        symbol (_type_): Ticker Ex: "CIPLA", "TATAMOTORS", "XVGBTC", "BTCUSDT"
        market (str): Exchange ("NSE", "BSE", "Binance")
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


def auto_trader(user: str = "vishalnadigofficial"):
    """Spin up an auto trading bot to trade for a particular user.

    Args:
        user (str): The name of the user to trade for.
    """
    unneccessary_coins = ["NOAH", "XEC", "INR"]
    current_orders = get_active_orders(user=user)["orders"]
    if len(current_orders) == 0:
        coins_currently_held = get_account_balance(user=user)
        for coin in unneccessary_coins:
            if coin in coins_currently_held:
                del coins_currently_held[coin]
        for coins in coins_currently_held.items():
            if (
                float(coins_currently_held[coins]["Locked Balance"]) == 0.0
                and float(coins_currently_held[coins]["Balance"]) > 1.0
            ):
                print(coins)


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
        user=args.user_name,
        symbol=args.symbol,
        market=args.market,
        screener_name=args.Screener,
        interval=args.interval,
    )


def plot_historical_data(
    coin_1: str = "BTC", coin_2: str = "USDT", interval: str = "1d", limit: int = 100
):
    """Plot the historical price of any cryptocurreny to perform technical and fundamental analysis

    Args:
        coin_1 (str, optional): Ticker symbol of the crypto. Defaults to "BTC".
        coin_2 (str, optional): Ticker symbol of the comparison crypto. Defaults to "USDT".
        interval (str, optional): Time interval to get the price of the crypto. Defaults to "1d".
        limit (int, optional): The number of candles to fetch. Max limit = 1000. Defaults to 100.
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


if __name__ == "__main__":
    # pprint(get_market_data(user="vishal nadig"))
    # place_sell_limit_order()
    # place_market_buy_order(user="vishalnadigofficial",coin_1="XTM", coin_2="USDT",total_quantity=425)
    # place_market_sell_order()
    # print(get_account_balance())
    # print(get_keys(user="VishalNadigOfficial"))
    # bot_trader(coin_1="PYR")
    # print(CONFIG["accounts"]["user"])
    # bot_trader("XVGBTC", "Binance", "Crypto", "1d")
    # parser_activated_bot()
    # print(get_keys(user = "Vishal NADIGOFFICIAL"))
    # auto_trader("vishalnadig")
    # place_buy_limit_order(coin_1="XTM")
    # add_keys(first_name="Anjana", last_name="Nadig", api_key="KHSDADASWW", secret_key="ASDASDASDA", email="anjannadig@gmail.com", google_auth_key="KSJAWDASFAS")
    # print(get_account_balance())
    # place_market_sell_order(user="vishalnadig",coin_1="PYR",total_quantity=12.0)
    # print(get_markets_details(coin_1="PYR"))
    print(get_ticker(coin_1="PYR"))
    # print(get_candles(coin_1="PYR",interval="1m"))