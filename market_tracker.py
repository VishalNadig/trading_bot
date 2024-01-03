"""A Python script to track market movements of all coins"""
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
from tradingview_ta import TA_Handler

from constants import INTERVAL_DICT, LOGFILE, REMOVE_CURRENCIES, URL_DICT

logging.basicConfig(
    level=logging.INFO,
    filemode="a",
    filename=LOGFILE,
    format="%(asctime)s;%(levelname)s;%(message)s",
)


def get_market_data(
    username: str = "", currency: str = "", remove_currency: list = []
) -> pd.DataFrame:
    """Get market data and information. We can get the market data and the information of all the currencies or only the specified currencies if they are passed as the argument to this function.

    Args:
        username (str, optional): Username from config file. Defaults to "".
        currency (str, optional): The coin we want the data of. Defaults to "".

    Returns:
        pd.DataFrame: _description_
    """
    if len(remove_currency) > 0:
        for coin in remove_currency:
            if coin not in REMOVE_CURRENCIES:
                REMOVE_CURRENCIES.add(coin)
            else:
                pass
    # TODO: Add the currency list to get the info about the specified currencies only.
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
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s") + timedelta(hours=7, minutes=0)
    for currencies in REMOVE_CURRENCIES:
        df = df[~df.market.str.endswith(currencies)]
    df = df.reset_index(drop=True)
    df = df.sort_index(ascending=True, axis=0)
    # df.to_csv("market_data.csv", mode="w")
    # if currency != "":
    #     if df["market"].str.contains(currency).any():
    #         print(df)
    # else:
    return df


def indicator_data(
    symbol: str, market: str, screener_name: str = "Crypto", interval: str = "4h"
) -> list:
    """Get complete indicator data from Trading View.

    Args:
        symbol (str): Ticker Ex: "CIPLA", "TATAMOTORS", "XVGBTC", "BTCUSDT"
        market (str): Exchange ("NSE", "BSE", "Binance")
        screener_name (str, optional): Either "India" or "Crypto". Defaults to "Crypto".
        interval (str, optional): Interval of chart "1m", "5m", "30m", "1h", "2h", "4h", "1d", "1W", "1M". Defaults to "4h".

    Returns:
        list: The indicator data for the market pair in an exchange.
    """

    trading_pair = TA_Handler(
        symbol=f"{symbol}",
        screener=f"{screener_name}",
        exchange=f"{market}",
        interval=INTERVAL_DICT[str(interval)],
    )
    return trading_pair.get_analysis().indicators


def market_tracker(
    coin_1: str = "",
    coin_2: str = "USDT",
    market: str = "Binance",
    interval: str = "4h",
    limit: int = 100,
):
    """
    Retrieves market data for a given coin and performs various analyses based on the data.

    Args:
        coin_1 (str): The first coin to track. Defaults to an empty string.
        coin_2 (str): The second coin to track. Defaults to "USDT".
        market (str): The market to track. Defaults to "Binance".
        interval (str): The time interval for tracking. Defaults to "4h".
        limit (int): The maximum number of data points to retrieve. Defaults to 100.

    Returns:
        None

    Raises:
        None

    Examples:
        >>> market_tracker()
        ...
    """
    if coin_1 == "":
        pass

        for coin in get_market_data(remove_currency=["BTC"])["market"]:
            try:

                indicator_data_ = indicator_data(coin, market=market, interval=interval)
                rsi = indicator_data_["RSI"]
                if rsi < 40:
                    print(coin, rsi)

            except:
                indicator_data_ = indicator_data(coin, market="Huobi", interval=interval)
                rsi = indicator_data_["RSI"]
                print(coin)
                if rsi < 40:
                    print(coin, rsi)
    else:
        indicator_data_ = indicator_data(symbol=coin_1 + coin_2, interval=interval, market=market)
        rsi = indicator_data_["RSI"]
        print(rsi)
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

        print(indicator_data_)

    #     print(coin)


if __name__ == "__main__":

    market_tracker(coin_1="BTC", coin_2="USDT", market="Binance", interval="4h", limit=100)
    # print(get_market_data())
