from tradingview_ta import Interval

INITIAL_INVESTMENT = 0.00037751708
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
    "TICKER_URL": "https://public.coindcx.com/exchange/ticker"
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
MARKETS = ("Binance", "Huobi", "CoinDCX", )