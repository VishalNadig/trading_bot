"""A crypto trading bot to place buy and sell orders automatically"""
import argparse
import csv
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from time import sleep
import toml
import pandas as pd
import requests
from tradingview_ta import Interval, TA_Handler
from pprint import pprint
from paths import paths

logging.basicConfig(
    level=logging.INFO,
    filemode="a",
    filename="LOGFILE_PI",
    format="%(asctime)s;%(levelname)s;%(message)s",
)
PARSER = argparse.ArgumentParser()
CONFIG_FILE = paths.CONFIG_FILE
SCREENER_LIST = ["India", "Crypto"]
INITIAL_INVESTMENT = 0.00037751708  # In BTC
LOGFILE = paths.LOGFILE
ORDER_HISTORY_FILE = r"/home/pi/python_programs/trading_bot/order_history.csv"
API_DICTS = {
    "coindcx": "https://api.coindcx.com/exchange/ticker",
    "cryptowatch": "https://api.cryptowat.ch/markets/binance",
}

INTERVAL_DICT = {
    "1m": Interval.INTERVAL_1_MINUTE,
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "30m": Interval.INTERVAL_30_MINUTES,
    "1h": Interval.INTERVAL_1_HOUR,
    "2h": Interval.INTERVAL_2_HOURS,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY,
    "1W": Interval.INTERVAL_1_WEEK,
    "1M": Interval.INTERVAL_1_MONTH,
}
# HISTORY_COLS = ["market", "last_price", "quantity", "type", "side", "timestamp", 'order_id']
# history_file = pd.DataFrame(columns=HISTORY_COLS)
# history_file.to_csv(ORDER_HISTORY_FILE, mode="w")
TODAY = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
CONFIG = toml.load(CONFIG_FILE)
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
COLS = [
    "market",
    "last_price",
    "bid",
    "ask",
    "volume",
    "high",
    "low",
    "timestamp",
]
CANDLE_DICT = {"CANDLES_URL": "https://public.coindcx.com/market_data/candles"}
REMOVE_CURRENCIES = {
    "INR",
    "BTC",
    "BNB",
    "ETH",
    "USDC",
    "BUSD",
    "TUSD",
    "TRX",
    "DAI",
    "XRP",
    "INR_insta",
}


def get_keys(first_name: str = "", last_name: str = "", user: str = "") -> tuple:
    if first_name and last_name != "":
        user = first_name + last_name
    user = user.lower()
    user = user.replace(" ", "")
    key = CONFIG["accounts"]["api_key"]
    secret_key = CONFIG["accounts"]["secret_key"]
    return key[user], secret_key[user]


def add_keys(first_name: str = "", last_name: str = ""):
    user = first_name + last_name
    user = user.lower()
    user = user.replace(" ", "")
    with (CONFIG_FILE, "r") as file:
        config = toml.load(file)
        if user not in config["accounts"]["user"]:
            toml.dump(user, file)


def get_market_data() -> pd.DataFrame:
    """Get the market data and filter it to our needs"""
    data = requests.get(URL_DICT["MARKET_DATA_URL"]).json()
    df = pd.DataFrame.from_dict(data)
    df = df.sort_values("market")
    COLS = df.columns.tolist()
    COLS = [
        "market",
        "last_price",
        "bid",
        "ask",
        "volume",
        "high",
        "low",
        "timestamp",
    ]
    df = df[COLS]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s") + timedelta(
        hours=5, minutes=30
    )
    for currency in REMOVE_CURRENCIES:
        df = df[~df.market.str.endswith(currency)]
    df = df.reset_index(drop=True)
    df = df.sort_index(ascending=True, axis=0)
    # df.to_csv("market_data.csv", mode="w")
    return df


def place_buy_limit_order(user: str, market: str, price: float, total_quantity: float) -> None:
    """Place a buy order by reading the current price and checking if the price is what we want"""
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))
    body = {
        "side": "buy",  # Toggle between 'buy' or 'sell'.
        "order_type": "limit_order",  # Toggle between a 'market_order' or 'limit_order'.
        "market": f"{market}",  # Replace 'SNTBTC' with your desired market pair.
        "price_per_unit": price,  # This parameter is only required for a 'limit_order'
        "total_quantity": f"{total_quantity}",  # Replace this with the quantity you want
        "timestamp": timeStamp,
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
                market,
                total_quantity,
                "market_order",
                "buy",
                TODAY,
            ]
        )
    logging.info("Written to order history file!")
    file.close()


def place_sell_limit_order(user: str, market: str, price: float, total_quantity: float) -> None:
    """Place a sell order by reading the current price and checking if the price is what we want"""
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))
    # message = (
    #     f"Sell order of {total_quantity} for market {market} placed at {price} price"
    # )
    body = {
        "side": "sell",  # Toggle between 'buy' or 'sell'.
        "order_type": "limit_order",  # Toggle between a 'market_order' or 'limit_order'.
        "market": f"{market}",  # Replace 'SNTBTC' with your desired market pair.
        "price_per_unit": price,  # This parameter is only required for a 'limit_order'
        "total_quantity": f"{total_quantity}",  # Replace this with the quantity you want
        "timestamp": timeStamp,
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
                market,
                total_quantity,
                "market_order",
                "sell",
                TODAY,
            ]
        )
    logging.info("Written to order history file!")
    file.close()


def place_market_buy_order(user: str, market: str, total_quantity: float) -> None:
    """Place buy order at current market price"""
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))

    body = {
        "side": "buy",  # Toggle between 'buy' or 'sell'.
        "order_type": f"market_order",  # Toggle between a 'market_order' or 'limit_order'.
        "market": f"{market}",  # Replace 'SNTBTC' with your desired market pair.
        "total_quantity": total_quantity,  # Replace this with the quantity you want
        "timestamp": timeStamp,
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
                market,
                total_quantity,
                "market_order",
                "buy",
                TODAY,
            ]
        )
    print("Written to file")
    file.close()


def place_market_sell_order(user: str, market: str, total_quantity: float) -> None:
    """Place sell order at current market price"""

    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))

    body = {
        "side": "sell",  # Toggle between 'buy' or 'sell'.
        "order_type": "market_order",  # Toggle between a 'market_order' or 'limit_order'.
        "market": f"{market}",  # Replace 'SNTBTC' with your desired market pair.
        "total_quantity": f"{total_quantity}",  # Replace this with the quantity you want
        "timestamp": timeStamp,
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
                market,
                total_quantity,
                "market_order",
                "sell",
                TODAY,
            ]
        )
    logging.info("Written to order history file!")
    file.close()


def create_multiple_orders(user: str) -> None:
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))
    body = {
        "orders": [
            {
                "side": "buy",  # Toggle between 'buy' or 'sell'.
                "order_type": "limit_order",  # Toggle between a 'market_order' or 'limit_order'.
                "market": "SNTBTC",  # Replace 'SNTBTC' with your desired market pair.
                "price_per_unit": 0.03244,  # This parameter is only required for a 'limit_order'
                "total_quantity": 400,  # Replace this with the quantity you want
                "timestamp": timeStamp,
                "ecode": "I",
            },
            {
                "side": "buy",  # Toggle between 'buy' or 'sell'.
                "order_type": "limit_order",  # Toggle between a 'market_order' or 'limit_order'.
                "market": "SNTBTC",  # Replace 'SNTBTC' with your desired market pair.
                "price_per_unit": 0.03244,  # This parameter is only required for a 'limit_order'
                "total_quantity": 400,  # Replace this with the quantity you want
                "timestamp": timeStamp,
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


def active_orders(user: str) -> pd.DataFrame:
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))
    body = {
        "side": "buy",  # Toggle between a 'buy' or 'sell' order.
        "market": "SNTBTC",  # Replace 'SNTBTC' with your desired market pair.
        "timestamp": timeStamp,
    }
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["ACTIVE_ORDERS_URL"], data=json_body, headers=headers
    )
    data = response.json()
    print(data)


def account_trade_history(user: str) -> pd.DataFrame:
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))

    body = {"from_id": 352622, "limit": 50, "timestamp": timeStamp}

    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["ACCOUNT_TRADE_HISTORY_URL"], data=json_body, headers=headers
    )
    data = response.json()
    print(data)


def cancel_order(user: str, id) -> None:
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")

    timeStamp = int(round(time.time() * 1000))
    body = {"id": f"{id}", "timestamp": timeStamp}  # Enter your Order ID here.
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["CANCEL_ONE_ACTIVE_ORDER_URL"], data=json_body, headers=headers
    )
    data = response.json()
    print(data)


def cancel_all_orders(user: str) -> None:
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")

    timeStamp = int(round(time.time() * 1000))
    body = {
        "side": "buy",  # Toggle between a 'buy' or 'sell' order.
        "market": "SNTBTC",  # Replace 'SNTBTC' with your desired market pair.
        "timestamp": timeStamp,
    }
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }
    response = requests.post(
        URL_DICT["CANCEL_ALL_ACTIVE_ORDERS_URL"], data=json_body, headers=headers
    )
    data = response.json()
    print(data)


def cancel_multiple_by_ids(user:str, ids: list) -> None:
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")

    body = {
        "ids": ids #[
            #"8a2f4284-c895-11e8-9e00-5b2c002a6ff4",
            #"8a1d1e4c-c895-11e8-9dff-df1480546936",
        #]
    }

    json_body = json.dumps(body, separators=(",", ":"))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url = "https://api.coindcx.com/exchange/v1/orders/cancel_by_ids"

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }

    response = requests.post(url, data=json_body, headers=headers)
    data = response.json()
    print(data)


def edit_price_of_orders(user: str, id, price: float) -> None:


    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))
    body = {
        "id": f"{id}",  # Enter your Order ID here.
        "timestamp": timeStamp,
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
        URL_DICT["EDIT_PRICE_URL"], data=json_body, headers=headers
    )
    data = response.json()
    print(data)


def auto_trader(user: str, symbol, market, screener_name, interval) -> None:
    """Execute trades automatically 24/7 based on input parameters
    symbol: Ticker Ex: "CIPLA", "TATAMOTORS", "XVGBTC", "BTCUSDT"
    market: Exchange ("NSE", "BSE", "Binance")
    screener_name: Either "India" or "Crypto"
    interval: Interval of chart "1m", "5m", "30m", "1h", "2h", "4h", "1d", "1W", "1M"""
    no_of_trades = 0
    open_position = False
    min_order_value = 0.0001
    order_size = 0
    count = 0
    print("Bot Started!", datetime.now().strftime("%Y-%m-%d %H:%M:%s"))
    logging.info("Bot Started!")
    indicator_data_ = indicator_data(
        symbol=symbol, market=market, screener_name=screener_name, interval=interval
    )
    rsi = indicator_data_["RSI"]
    buy_price = indicator_data_["Pivot.M.Fibonacci.Middle"]
    sell_price = indicator_data_["Pivot.M.Fibonacci.R1"]
    stop_loss = indicator_data_["Pivot.M.Fibonacci.S1"] - 0.00000001
    logging.info(
        f"""RSI value for {interval} for {symbol} is {rsi}.\nBuy price is {buy_price}.\nTarget is {sell_price}.\nStop loss is set at {stop_loss}.
            \nOrder size is {order_size}."""
    )
    while True and no_of_trades <= 100:
        try:
            sleep(15)
            data = requests.get(URL_DICT["MARKET_DATA_URL"]).json()
            indicator_data_ = indicator_data(
                symbol=symbol,
                market=market,
                screener_name=screener_name,
                interval=interval,
            )
            account_balance = get_account_balance()
        except Exception as exception:
            logging.error(exception)
            sleep(60)
            data = requests.get(URL_DICT["MARKET_DATA_URL"]).json()
            indicator_data_ = indicator_data(
                symbol=symbol,
                market=market,
                screener_name=screener_name,
                interval=interval,
            )
            account_balance = get_account_balance()

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
        df = pd.DataFrame.from_dict(data)
        df = df.sort_values("market")
        # df = df[COLS]
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s") + timedelta(
            hours=5, minutes=30
        )
        for currency in REMOVE_CURRENCIES:
            df = df[~df.market.str.endswith(currency)]
        df = df.reset_index(drop=True)
        df = df.sort_index(ascending=True, axis=0)
        current_price = df.iloc[506]["last_price"]
        # SET BUY PRICE, SELL PRICE AND STOP LOSS CONDITIONS
        if (
            current_price < pivot
            and current_price > supports[0]
            and current_price < close_price
        ):
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
            float(current_price) == buy_price
            and not open_position
            and order_size > min_order_value
        ) or (rsi < 37 and not open_position and order_size > min_order_value):
            place_buy_limit_order(user=user,market="XVGBTC", price=buy_price, total_quantity=order_size)
            logging.info(
                f"Buy Order placed! for {symbol} at price {buy_price}. Stop loss is {stop_loss}"
            )
            open_position = True
        if (  # SELL CONDITIONS
            (float(current_price) == sell_price and open_position)
            or float(current_price) == stop_loss
            or (rsi > 60 and open_position)
        ):
            place_sell_limit_order(user=user,
                market="XVGBTC", price=sell_price, total_quantity=order_size
            )
            logging.info(f"Sold XVG {sell_price}")
            logging.info(f"The current account balance is: {account_balance} BTC")
            open_position = False
            no_of_trades += 1
            profit = ((sell_price - buy_price) / buy_price) * (100)
            logging.info(f"made {profit}% profits!")


def get_account_balance(user: str = "VishalNadig") -> pd.DataFrame:
    
    secret_bytes = bytes(get_keys(user=user)[1], encoding="utf-8")
    timeStamp = int(round(time.time() * 1000))
    body = {"timestamp": timeStamp}
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": get_keys(user=user)[0],
        "X-AUTH-SIGNATURE": signature,
    }

    response = requests.post(
        URL_DICT["ACCOUNT_BALANCE_URL"], data=json_body, headers=headers
    )
    data = response.json()
    dataframe = {}
    # dataframe.to_csv("account_balance.csv")
    # account_balance = dataframe["balance"]
    for DATA in data:
        if (
            float(DATA["balance"]) > 0.1
            or float(DATA["locked_balance"]) > 0.1
            or "BTC" in DATA["currency"]
        ):
            dataframe[DATA["currency"]] = {
                "Balance": DATA["balance"],
                "Locked Balance": DATA["locked_balance"],
            }

    return dataframe


def get_candles(
    market: str, coin1: str, coin2: str, limit: int = 100, interval: str = "4h"
) -> pd.DataFrame:
    """
    Get candle data.
    market: B- Binance, I- CoinDCX, HB- HitBTC, H- Huobi, BM- BitMex
    coin1: Symbol of coin1 (BTC, XRP, SHIB, DOGE, ADA)
    coin2: Symbol of coin2 (BTC, USDT)
    limit: maximum 1000 candles
    interval: [1m   5m  15m 30m 1h  2h  4h  6h  8h  1d  3d  1w  1M] m -> minutes, h -> hours, d -> days, w -> weeks, M -> months
    """
    url = (
        CANDLE_DICT["CANDLES_URL"]
        + f"?pair={market}-{coin1}_{coin2}&interval={interval}&limit={limit}"
    )
    response = requests.get(url)
    data = response.json()
    dataframe = pd.DataFrame.from_dict(data)
    dataframe["time"] = pd.to_datetime(dataframe["time"], unit="ms")
    dataframe.to_csv(
        r"/Users/akshathanadig/Downloads/Education/Computer Science/Python/Trading Bot/Analysis_data/candle_data.csv",
        mode="w",
    )
    print(dataframe)
    return dataframe


def indicator_data(
    symbol, market: str, screener_name: str = "Crypto", interval: str = "4h"
) -> list:
    """Get complete indicator data from Trading View.
    symbol: Ticker Ex: "CIPLA", "TATAMOTORS", "XVGBTC", "BTCUSDT"
    market: Exchange ("NSE", "BSE", "Binance")
    screener_name: Either "India" or "Crypto"
    interval: Interval of chart "1m", "5m", "30m", "1h", "2h", "4h", "1d", "1W", "1M"
    """
    trading_pair = TA_Handler(
        symbol=f"{symbol}",
        screener=f"{screener_name}",
        exchange=f"{market}",
        interval=INTERVAL_DICT[str(interval)],
    )
    return trading_pair.get_analysis().indicators


def parser_activated_bot() -> None:
    PARSER.add_argument(
        "-s", "--symbol", help="The symbol of the stock to trade", required=True
    )
    PARSER.add_argument("-m", "--market", help="The market to trade", required=True)
    PARSER.add_argument("-S", "--Screener", help="Name of screener", required=True)
    PARSER.add_argument(
        "-i",
        "--interval",
        help="The chart interval to get the indicator",
        required=True,
    )
    args = PARSER.parse_args()
    auto_trader(
        symbol=args.symbol,
        market=args.market,
        screener_name=args.Screener,
        interval=args.interval,
    )


if __name__ == "__main__":
    # get_market_data()
    # place_sell_limit_order()
    # place_market_buy_order()
    # place_market_sell_order()
    # get_candles("B", "QKC", "BTC", 100, "1d")
    # get_account_balance()
    # pprint(get_account_balance())
    pprint(get_keys(user="VishalNadig"))
    # print(CONFIG["accounts"]["user"])
    # auto_trader("XVGBTC", "Binance", "Crypto", "1d")
    # parser_activated_bot()
    pass
