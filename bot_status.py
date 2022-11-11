import configparser
import csv
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from time import sleep

import pandas as pd
import requests
from pandas.core.frame import DataFrame
from tradingview_ta import Exchange, Interval, TA_Handler

CONFIG = configparser.RawConfigParser()
CONFIG.read(
    # r"/Users/akshathanadig/Downloads/Education/Computer Science/Python/Trading Bot/config.ini
    r"/home/pi/python_projects/trading_bot/vn_official_bot/config.ini"
)
KEY = CONFIG["key"]["key"]
SECRET = CONFIG["secret_key"]["secret"]

URL_DICT = {
    "MARKET_DATA_URL": "https://api.coindcx.com/exchange/ticker",
    "NEW_ORDER_URL": "https://api.coindcx.com/exchange/v1/orders/create",
    "CREATE_MULTIPLE_ORDERS_URL": "https://api.coindcx.com/exchange/v1/orders/create_multiple",
    "ORDER_STATUS_URL": "https://api.coindcx.com/exchange/v1/orders/status",
    "MULTIPLE_ORDER_STATUS_URL": "https://api.coindcx.com/exchange/v1/orders/status_multiple",
    "ACTIVE_ORDERS_URL": "https://api.coindcx.com/exchange/v1/orders/active_orders",
    "ACCOUNT_TRADE_HISTORY_URL": "https://api.coindcx.com/exchange/v1/orders/trade_history",
    "ACTIVE_ORDERS_COUNT_URL": "https://api.coindcx.com/exchange/v1/orders/active_orders_count",
    "CANCEL_ALL_ACTIVE_ORDERS_URL": "https://api.coindcx.com/exchange/v1/orders/cancel_all",
    "CANCEL_MULTIPLE_ACTIVE_ORDERS_BY_IDS_URL": "https://api.coindcx.com/exchange/v1/orders/cancel_by_ids",
    "CANCEL_ONE_ACTIVE_ORDER_URL": "https://api.coindcx.com/exchange/v1/orders/cancel",
    "EDIT_PRICE_URL": "https://api.coindcx.com/exchange/v1/orders/edit",
    "ACCOUNT_BALANCE_URL": "https://api.coindcx.com/exchange/v1/users/balances",
}


def account_trade_history():
    key = KEY
    secret = SECRET

    secret_bytes = bytes(secret, encoding="utf-8")

    timeStamp = int(round(time.time() * 1000))

    body = {"from_id": 352622, "limit": 20, "timestamp": timeStamp}

    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": key,
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["ACCOUNT_TRADE_HISTORY_URL"], data=json_body, headers=headers
    )
    data = response.json()
    df = pd.DataFrame.from_dict(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms") + timedelta(
        hours=5, minutes=30
    )
    df = df.sort_values("timestamp", ascending=False)
    return df["symbol"]


def get_active_orders() -> None:
    key = KEY
    secret = SECRET
    trade_history = account_trade_history()
    secret_bytes = bytes(secret, encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))
    #    print(trade_history)
    order_history_list = []
    for symbol in trade_history:
        body = {
            "side": f"sell",  # Toggle between a 'buy' or 'sell' order.
            "market": f"{symbol}",  # Replace 'SNTBTC' with your desired market pair.
            "timestamp": timeStamp,
        }
        json_body = json.dumps(body, separators=(",", ":"))
        signature = hmac.new(
            secret_bytes, json_body.encode(), hashlib.sha256
        ).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": key,
            "X-AUTH-SIGNATURE": signature,
        }
        response = requests.post(
            URL_DICT["ACTIVE_ORDERS_URL"], data=json_body, headers=headers
        )
        data = response.json()
        df_sell = pd.DataFrame.from_dict(data)
        if df_sell.empty:
            pass
        else:
            order_history_list.append(df_sell)
        body = {
            "side": f"buy",  # Toggle between a 'buy' or 'sell' order.
            "market": f"{symbol}",  # Replace 'SNTBTC' with your desired market pair.
            "timestamp": timeStamp,
        }
        json_body = json.dumps(body, separators=(",", ":"))
        signature = hmac.new(
            secret_bytes, json_body.encode(), hashlib.sha256
        ).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": key,
            "X-AUTH-SIGNATURE": signature,
        }
        response = requests.post(
            URL_DICT["ACTIVE_ORDERS_URL"], data=json_body, headers=headers
        )
        data = response.json()
        df_buy = pd.DataFrame(data)
        if df_buy.empty:
            pass
        else:
            order_history_list.append(df_buy)
    if len(order_history_list) == 0:
        print(
            "No active orders, here is the latest trade history of the last five orders"
        )
        print(account_trade_history())
    print("VN Official bot status:\n")
    for order in order_history_list:
        print(
            f"Trade Pair: {order['orders'][0]['market']}",
            f"\tPrice: {order['orders'][0]['price_per_unit']}",
            f"\tStatus: {order['orders'][0]['status']}",
            f"\tSide: {order['orders'][0]['side']}",
            f"\tTotal Quantity: {order['orders'][0]['total_quantity']}",
            f"\tRemaining Quantity: {order['orders'][0]['remaining_quantity']}",
            f"\tCreated At: {order['orders'][0]['created_at']}",
        )


if __name__ == "__main__":
    get_active_orders()
    # account_trade_history()
