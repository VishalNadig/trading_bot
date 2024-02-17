# TRADING BOT DOCUMENTATION
This is still Work in Progress.
# GENERAL INFORMATION
1. You will need to have the config files with you. The megamind_config file is ideal.
2. You will also need to install and setup poetry first.
3. Make sure the keys of the user are in the config file. Else add them.
4. Make sure to install and update all dependencies using poetry install and poetry update.
5. Make sure the path of the config file matches the path given by paths.py in paths folder.


# FUNCTIONS
## def initialize() -> None:


## def get_keys(first_name: str = "", last_name: str = "", username: str = "") -> tuple:
    """Get the API key and secret key for the specified username. If the username is not mentioned then, the first name and last name of the username can be used to retrieve the keys.

    Args:
        first_name (str, optional): First name of the username. Defaults to "".
        last_name (str, optional): Last name of the username. Defaults to "".
        username (str, optional): Username to retrieve the keys. Defaults to "".

    Returns:
        tuple: The API key and the secret key.
    """


## def add_keys(
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


## def update_keys(
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

## def delete_keys(first_name: str, last_name: str, username: str) -> dict:
    """
    Delete the keys for a specific username in the trading bot configuration file.

    Parameters:
        first_name (str): The first name of the username.
        last_name (str): The last name of the username.
        username (str): The username of the username.

    Returns:
        None
    """

## def get_ticker(coin_1: str = "BTC", coin_2: str = "USDT", all_coins: bool = False) -> pd.DataFrame:
    """Get the ticker details of the coin

    Args:
        coin_1 (str, optional): The coin to get the ticker details of. Defaults to "BTC".
        coin_2 (str, optional): The coin against which to get the ticker details of. Defaults to "USDT".
        all_coins (bool, optional): Whether to get the ticker details of all the coins. Defaults to False.

    Returns:
        dict: The dictionary of the coins details
    """

## def get_market_data(save_dataframe: bool = False, skip_btc: bool = False) -> pd.DataFrame:
    """Get the market data of all coins in the market currently.

    Args:
        save_dataframe (bool, optional): Whether to save the dataframe. Defaults to False.

    Returns:
        dict: The dictionary of the coins market data
    """

## def get_markets_details(
    coin_1: str = "",
    coin_2: str = "USDT",
    coins_list: list = [],
    all_coins: bool = False,
    save_dataframe: bool = False,
    show_leverage_long: bool = False,
    show_leverage_short: bool = False,
) -> pd.DataFrame:
    """Get the market details of the coins listed on the exchange. This includes the max leverage of the coin, the market it trades in, the min quantity to place an order, the max quantity to place an order.

    Args:
        coin_1 (str, optional): The coin to check the price for. Defaults to "BTC".
        coin_2 (str, optional): The coin to check the price against. Defaults to "USDT".
        coins_list (list, optional): If you want the details of multiple coins then pass all the coins as a list to this argument. Defaults to [].

    Returns:
        dict: The dictionary of the market details of the coins.
    """

    ## def place_buy_limit_order(
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

## def place_sell_limit_order(
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

## def place_market_buy_order(
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

## def place_market_sell_order(
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

## def create_multiple_orders(
    username: str = CONFIG["Owner"]["main_username"], orders: list = []
) -> None:
    """Create multiple orders at once.

    Args:
        username (str): The username of the account to place the order in.
        orders (str): The different orders that need to be placed for the username.
    """

## def get_active_orders(username: str = CONFIG["Owner"]["main_username"]) -> dict:
    """Get the current buy or sell active orders for the username.

    Args:
        username (str): The username of the account to get the active orders from.

    Returns:
        dict: List of all the active orders
    """

## def account_trade_history(username: str = CONFIG["Owner"]["main_username"], save_dataframe: bool = False, limit: int = 500) -> dict:
    """Get the account trade history of the username.

    Args:
        username (str): The username of the account for which the trade history is to be fetched.

    Returns:
        dict: The history of trades made by the username.
    """

## def cancel_order(username: str = CONFIG["Owner"]["main_username"], ids: str = "") -> None:
    """Cancel a particular order of the username.

    Args:
        username (str): The username of the account for whom the order needs to be cancelled.
        id (_type_): The order id.
    """

## def cancel_all_orders(username: str = CONFIG["Owner"]["main_username"]) -> None:
    """Cancel all the active orders of the username.

    Args:
        username (str): The username of the account for which the order needs to be cancelled.
    """

## def cancel_multiple_by_ids(username: str = CONFIG["Owner"]["main_username"], ids: list = []) -> None:
    """Cancel multiple orders given by the list of ids for a particular username.

    Args:
        username (str): The username of the account for which the orders need to be cancelled.
        ids (list): The list of order ids to cancel.
    """

## def edit_price_of_orders(
    username: str = CONFIG["Owner"]["main_username"], ids: list = [], price: float = ""
) -> None:
    """Edit the buy or sell price of the orders.

    Args:
        username (str): The username of the account for which the price needs to be edited.
        ids (_type_): The order id for which the price needs to be edited
        price (float): _description_
    """

## def bot_trader(
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

## def get_account_balance(username: str = CONFIG["Owner"]["main_username"], save_dataframe: bool = False) -> dict:
    """Get the account balance of the username.

    Args:
        username (str, optional): The username of the account to get the balance of. Defaults to CONFIG['Owner']['main_username'].

    Returns:
        dict: The dictionary of the account balances of all the currencies.
    """

## def get_account_balance(username: str = CONFIG["Owner"]["main_username"], save_dataframe: bool = False) -> dict:
    """Get the account balance of the username.

    Args:
        username (str, optional): The username of the account to get the balance of. Defaults to CONFIG['Owner']['main_username'].

    Returns:
        dict: The dictionary of the account balances of all the currencies.
    """

## def get_candles(
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

## def get_indicator_data(
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

## def auto_trader(username: str = CONFIG["Owner"]["main_username"]):
    """Spin up an auto trading bot to trade for a particular username.

    Args:
        username (str): The name of the username to trade for.
    """

## def parser_activated_bot() -> None:
    """A CLI to spin up an instance of the bot."""

## def plot_historical_data(
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

## def send_mail(message: str, receiver: str = CONFIG["Owner"]["main_username"]) -> None:
    """Send mail function to send a mail and deliver the message.

    Args:
        message (str): The message to be sent through the mail.
    """

## def price_tracker_mail(
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

## def buy_sell_recommendation(
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

## def fetch_lend_orders(username: str = CONFIG["Owner"]["main_username"]):
    """
    Fetches the list of lend orders for the user.

    Args:
        username (str): The username of the user. Defaults to "main_username".

    Returns:
        dict: A dictionary containing the list of lend orders.
    """

## def lend_order(
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

## def settle_orders(username: str = CONFIG["Owner"]["main_username"]):
    """
    Setstle all orders for the user.

    Args:
        username (str): The username of the user. Defaults to "main_username".

    Returns:
        dict: A dictionary containing the list of settle orders.
    """

## def crypto_price_tracker(save_dataframe: bool = False):
    """
    A function that iterates over all files in the current directory and prints the names of the files that have a '.json' extension and contain today's date in the file name.

    Parameters:
        username (str): The username of the user. Defaults to "vishalnadigofficial".

    Returns:
        None
    """

## def get_price_of_coin_on_date(
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

## def get_market_indicator(
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

## def get_price_difference(coin: str = ""):
    """
    Calculate the price difference for a given coin.
    Args:
        coin (str): The name of the coin. Defaults to empty string.
    Returns:
        pandas.DataFrame: DataFrame containing the price difference information.
    """

## def get_buy_suggestions(
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

## def get_weekly_portfolio_update(username: str = CONFIG["Owner"]["main_username"]):
    """
    Generates a weekly portfolio update for the user.

    Parameters:
        user (str): The username of the user. Defaults to "vishalnadigofficial".

    Returns:
        None
    """

## def regular_updates(
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

## def long_recommendations(coin_1: str = "BTC", coin_2: str = "USDT", all_coins: bool = False, save_dataframe: bool = False, interval: str = "5m", balance_only: bool= False, max_leverage: int = 2):
    """
    Generates long recommendations based on certain criteria.

    Args:
        coin_1 (str, optional): The first coin to consider. Defaults to "BTC".
        coin_2 (str, optional): The second coin to consider. Defaults to "USDT".
        all_coins (bool, optional): Whether to consider all coins. Defaults to False.
        save_dataframe (bool, optional): Whether to save the resulting dataframe. Defaults to False.
        interval (str, optional): The interval to use for calculations. Defaults to "4h".

    Returns:
        pandas.DataFrame: The resulting dataframe containing long recommendations.
    """

## def short_recommendations(coin_1: str = "BTC", coin_2: str = "USDT", all_coins: bool = False, save_dataframe: bool = False, interval: str = "4h"):
    """
    A function to generate short recommendations for trading pairs based on market data and indicators.
    Parameters:
        coin_1 (str): The first coin in the trading pair (default is "BTC").
        coin_2 (str): The second coin in the trading pair (default is "USDT").
        all_coins (bool): Flag to indicate whether to consider all available coins (default is False).
        save_dataframe (bool): Flag to indicate whether to save the resulting dataframe to a CSV file (default is False).
        interval (str): The time interval for market data and indicator analysis (default is "4h").
    Returns:
        pandas.DataFrame: A dataframe containing short recommendations for trading pairs.
    """
