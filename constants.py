"""All constants used in the program."""
from datetime import datetime

import yaml
from tradingview_ta import Interval

from paths import paths

TRADING_FEE = 0.011 # 0.1% trading fee + 1% TDS
ORDER_HISTORY_FILE = paths.ORDER_HISTORY_FILE
LOGFILE = paths.LOGFILE
TODAY = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
CONFIG_FILE = paths.CONFIG_FILE
MARKET_DATA_DIRECTORY = paths.MARKET_DATA_DIRECTORY
with open(CONFIG_FILE) as file:
    CONFIG = yaml.safe_load(file)
USER = CONFIG["database_creds"]["CONNECTION_2"]["USER"]
PASSWORD = CONFIG["database_creds"]["CONNECTION_2"]["PASSWORD"]
HOSTNAME = CONFIG["database_creds"]["CONNECTION_2"]["HOSTNAME"]
DATABASE = CONFIG["database_creds"]["DATABASE_1"]["NAME"]
PORT = CONFIG["database_creds"]["CONNECTION_2"]["PORT"]
URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}"
INITIAL_INVESTMENT = 0.024  # BTC
SCREENER_LIST = ["India", "Crypto"]
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

URL_DICT = {
    "ALL_COIN_PAIRS_URL": "https://api.coindcx.com/",
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
    "CANDLES_URL": "https://public.coindcx.com/market_data/candles",
    "MARKET_DETAILS_URL": "https://api.coindcx.com/exchange/v1/markets_details",
    "TICKER_URL": "https://public.coindcx.com/exchange/ticker",
    "USER_INFO": "https://public.coindcx.com/exchange/v1/users/info",
    "LEND_ORDERS_URL": "https://api.coindcx.com/exchange/v1/funding/lend",
    "SETTLE_ORDERS_URL": "https://api.coindcx.com/exchange/v1/funding/settle",
    "FETCH_LEND_ORDERS_URL": "https://api.coindcx.com/exchange/v1/funding/fetch_orders",
    "COINMARKETCAP_URL": {
        "URL": "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",
        "parameters": {
            "start": 1,
            "limit": 5000,
            "convert": "USD",
            "headers": {
                "Accepts": "application/json",
                "X-CMC_PRO_API_KEY": CONFIG["coinmarketcap_api_key"],
            },
        },
    },
    "COINMARKETCAP_CATEGORIES": {
        "URL": "https://pro-api.coinmarketcap.com/v1/cryptocurrency/categories",
        "parameters": {
            "start": 1,
            "limit": 5000,
        },
        "headers": {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": CONFIG["coinmarketcap_api_key"],
        },
    },
    "COINMARKETCAP_CATEGORY": {
        "URL": "https://pro-api.coinmarketcap.com/v1/cryptocurrency/category",
        "parameters": {"start": 1, "limit": 1000, "id": "6051a80866fc1b42617d6da1"},
        "headers": {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": CONFIG["coinmarketcap_api_key"],
        },
    },
}

REMOVE_CURRENCIES = {
    "INR",
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
MARKETS = {
    "B": "Binance",
    "KC": "Kucoin",
    "I": "CoinDCX",
    "H": "Huobi",
    "G": "GateIO",
}

{'KC', 'B', 'H', 'I'}