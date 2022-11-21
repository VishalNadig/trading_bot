# TRADING BOT DOCUMENTATION

# GENERAL INFORMATION
1. You will need to have the config files with you. The megamind_config file is ideal.
2. You will also need to install and setup poetry first.
3. Make sure the keys of the user are in the config file. Else add them.
4. Make sure to install and update all dependencies using poetry install and poetry update.
5. Make sure the path of the config file matches the path given by paths.py in paths folder.

# FUNCTIONS
## get_keys(first_name: str = "", last_name: str = "", user: str = "") -> tuple:
    """Get API key and secret key for the specified user. If user is not mentioned then, first name and last name of the user can be used to retrieve the keys.

    Args:
        first_name (str, optional): First name of the user. Defaults to "".
        last_name (str, optional): Last name of the user. Defaults to "".
        user (str, optional): Username to retrieve the keys. Defaults to "".

    Returns:
        tuple: The API key and the secret key.
    """

## add_keys(first_name: str = "", last_name: str = "", api_key: str = "", secret_key: str = "") -> None:
    """Add API key and the secret key for a new user. If the user already exists. Return exception.

    Args:
        first_name (str, optional): First name of the user. Defaults to "".
        last_name (str, optional): Last name of the user. Defaults to "".

    Returns: None
    """

## get_market_data(user: str = "", currency: list = []) -> pd.DataFrame:
    """Get market data and information. We can get the market data and the information of all the currencies or only the specified currencies if they are passed as the argument to this function.

    Args:
        user (str, optional): _description_. Defaults to "".
        currency (str, optional): _description_. Defaults to "".

    Returns:
        pd.DataFrame: _description_
    """


## place_buy_limit_order(user: str, market: str, price: float, total_quantity: float) -> None:

    Args:
        user (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        price (float): The price at which to buy.
        total_quantity (float): The number of stocks or coins to buy.

    Returns: None.
    """

## place_sell_limit_order(user: str, market: str, price: float, total_quantity: float) -> None:
    """Place a buy limit order on the market pair specified.

    Args:
        user (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        price (float): The price at which to sell.
        total_quantity (float): The number of stocks or coins to sell.

    Returns: None.
    """

## place_market_buy_order(user: str, market: str, total_quantity: float) -> None:
    """Place a buy market order on the market pair specified. The order is placed at the current market price. This order gets executed immediately.

    Args:
        user (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        total_quantity (float): The number of stocks or coins to buy.

    Returns: None.
    """

## place_market_sell_order(user: str, market: str, total_quantity: float) -> None:
    """Place a sell market order on the market pair specified. The order is placed at the current market price. This order gets executed immediately.

    Args:
        user (str): Username of the account to place the order in.
        market (str): The market pair to place the order. Eg: BTCUSDT, TATAINR.
        total_quantity (float): The number of stocks or coins to buy.

    Returns: None.
    """
## create_multiple_orders(user: str, orders: list = []) -> None:
    """Create multiple orders at once.

    Args:
        user (str): The username of the account to place the order in.
    """

## active_orders(user: str) -> dict:
    """Get the current buy or sell active orders for the user.

    Args:
        user (str): The username of the account to get the active orders from.

    Returns:
        dict: List of all the active orders
    """

## account_trade_history(user: str) -> dict:
    """Get the account trade history of the user.

    Args:
        user (str): The username of the account for which the trade history is to be fetched.

    Returns:
        dict: The history of trades made by the user.
    """
## cancel_order(user: str, ids) -> None:
    """Cancel a particular order of the user.

    Args:
        user (str): The username of the account for whom the order needs to be cancelled.
        id (_type_): The order id.
    """


## cancel_all_orders(user: str) -> None:
    """Cancel all the active orders of the user.

    Args:
        user (str): The username of the account for which the order needs to be cancelled.
    """

## cancel_multiple_by_ids(user: str, ids: list) -> None:
    """Cancel multiple orders given by the list of ids for a particular user.

    Args:
        user (str): The username of the account for which the orders need to be cancelled.
        ids (list): The list of order ids to cancel.
    """

## edit_price_of_orders(user: str, ids, price: float) -> None:
    """Edit the buy or sell price of the orders.

    Args:
        user (str): The username of the account for which the price needs to be edited.
        ids (_type_): The order id for which the price needs to be edited
        price (float): _description_
    """
## auto_trader(user: str, symbol: str, market: str, screener_name: str, interval: str) -> None:
    """Execute trades automatically 24/7 based on input parameters

    Args:
        user (str): The username of the account to auto_trade in.
        symbol (str): Ticker Ex: "CIPLA", "TATAMOTORS", "XVGBTC", "BTCUSDT".
        market (str): he name of the exchange ("NSE", "BSE", "Binance").
        screener_name (str): Either "India" or "Crypto".
        interval (str): Interval of chart "1m", "5m", "30m", "1h", "2h", "4h", "1d", "1W", "1M
    """
## get_account_balance(user: str = "VishalNadig") -> dict:
    """Get the account balance of the user.

    Args:
        user (str, optional): The username of the account to get the balance of. Defaults to "VishalNadig".

    Returns:
        dict: The dictionary of the account balances of all the currencies.
    """

## get_candles(market: str, coin1: str, coin2: str, limit: int = 100, interval: str = "4h")-> pd.DataFrame:
    """Get historical candle data of a cryptocurrency for price prediction and analysis.

    Args:
        market (str): B- Binance, I- CoinDCX, HB- HitBTC, H- Huobi, BM- BitMex.
        coin1 (str): Symbol of coin1 (BTC, XRP, SHIB, DOGE, ADA)
        coin2 (str): Symbol of coin2 (BTC, USDT).
        limit (int, optional): maximum 1000 candles.
        interval (str, optional): [1m   5m  15m 30m 1h  2h  4h  6h  8h  1d  3d  1w  1M] m -> minutes, h -> hours, d -> days, w -> weeks, M -> months. Defaults to "4h".

    Returns:
        pd.DataFrame: The historical candle data of the coin market pair.
    """

## indicator_data(symbol, market: str, screener_name: str = "Crypto", interval: str = "4h") -> list:
    """Get complete indicator data from Trading View.

    Args:
        symbol (_type_): Ticker Ex: "CIPLA", "TATAMOTORS", "XVGBTC", "BTCUSDT"
        market (str): Exchange ("NSE", "BSE", "Binance")
        screener_name (str, optional): Either "India" or "Crypto". Defaults to "Crypto".
        interval (str, optional): Interval of chart "1m", "5m", "30m", "1h", "2h", "4h", "1d", "1W", "1M". Defaults to "4h".

    Returns:
        list: The indicator data for the market pair in an exchange.
    """

## parser_activated_bot() -> None:
    """A CLI to spin up an instance of the bot.
    """

## add_keys_cli() -> None:
    """Add keys via the interactive terminal.
    """
