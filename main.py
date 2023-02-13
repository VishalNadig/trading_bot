import trading_bot
import uvicorn
import yaml
from paths import paths
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
config = paths.CONFIG_FILE
with open(config, "r") as file:
    CONFIG = yaml.safe_load(file)

@app.get("/", tags=["Welcome"])
def welcome():
    return "Welcome master Vishal. I am trading bot."


# @app.get("/get_keys", tags=["trading_bot"])
# def get_keys(first_name: str = "", last_name: str = "", user: str = ""):
#     return trading_bot.get_keys(first_name=first_name, last_name=last_name, user=user)

# @app.post("/add_keys", tags=["trading_bot"])
# def add_keys(
#     first_name: str = "",
#     last_name: str = "",
#     api_key: str = "",
#     secret_key: str = "",
#     email: str = "",
#     google_auth_key: str = "",
# ):
#     return trading_bot.add_keys(first_name=first_name, last_name=last_name, api_key=api_key, secret_key=secret_key, email=email, google_auth_key=google_auth_key)


@app.post("/trading_bot/get_ticker", tags=["trading_bot"])
def get_ticker(coin_1: str = "BTC", coin_2: str = "USDT", coins_list: list = []):
    return trading_bot.get_ticker(coin_1=coin_1, coin_2=coin_2, coins_list=coins_list)


# @app.get("/trading_bot/get_markets_details", tags=["trading_bot"])
# def get_markets_details(coin_1: str = "BTC", coin_2: str = "USDT", coins_list: list = []):
#     return trading_bot.get_markets_details(coin_1=coin_1, coin_2=coin_2, coins_list=coins_list)


# @app.get("/trading_bot/place_buy_limit_order", tags=["trading_bot"])
# def place_buy_limit_order(user: str = CONFIG['Owner']['alt_username'], coin_1: str = "BTC", coin_2: str = "USDT", price: float = 0.023, total_quantity: float = 450):
#     return trading_bot.place_buy_limit_order(user=user, coin_1=coin_1, coin_2=coin_2, price=price, total_quantity=total_quantity)


# @app.get("/trading_bot/place_sell_limit_order", tags=["trading_bot"])
# def place_sell_limit_order(user: str = CONFIG['Owner']['alt_username'], coin_1: str = "BTC", coin_2: str = "USDT", price: float = 0.25, total_quantity: float = 450.0):
#     return trading_bot.place_sell_limit_order(user=user, coin_1=coin_1, coin_2=coin_2, price=price, total_quantity=total_quantity)


# @app.get("/trading_bot/place_market_buy_order", tags=["trading_bot"])
# def place_market_buy_order(user: str = CONFIG['Owner']['alt_username'], coin_1: str = "BTC", coin_2: str = "USDT", total_quantity: float = 450):
#     return trading_bot.place_market_buy_order(user=user, coin_1=coin_1, coin_2=coin_2, total_quantity=total_quantity)


# @app.get("/trading_bot/place_market_sell_order", tags=["trading_bot"])
# def place_market_sell_order(user: str = CONFIG['Owner']['alt_username'], coin_1: str = "BTC", coin_2: str = "USDT", total_quantity: float = 450.0):
#     return trading_bot.place_market_sell_order(user=user, coin_1=coin_1, coin_2=coin_2, total_quantity=total_quantity)


# @app.post("/trading_bot/create_multiple_orders", tags=["trading_bot"])
# def create_multiple_orders(user: str = CONFIG['Owner']['alt_username'], orders: list = []):
#     return trading_bot.create_multiple_orders(user=user, orders=orders)


# @app.get("/trading_bot/get_active_orders", tags=["trading_bot"])
# def get_active_orders(user: str = CONFIG['Owner']['alt_username']):
#     return trading_bot.get_active_orders(user=user)


# @app.get("/trading_bot/account_trade_history", tags=["trading_bot"])
# def account_trade_history(user: str = CONFIG['Owner']['alt_username']):
#     return trading_bot.account_trade_history(user=user)


# @app.get("/trading_bot/cancel_order", tags=["trading_bot"])
# def cancel_order(user: str = CONFIG['Owner']['alt_username'], ids: str = ""):
#     return trading_bot.cancel_order(user=user, ids=ids)


# @app.get("/trading_bot/cancel_all_orders", tags=["trading_bot"])
# def cancel_all_orders(user: str = CONFIG['Owner']['alt_username']):
#     return trading_bot.cancel_all_orders(user=user)


# @app.get("/trading_bot/cancel_multiple_by_ids", tags=["trading_bot"])
# def cancel_multiple_by_ids(user: str = CONFIG['Owner']['alt_username'], ids: list = []):
#     return trading_bot.cancel_multiple_by_ids(user=user, ids=ids)


# @app.get("/trading_bot/edit_price_of_orders", tags=["trading_bot"])
# def edit_price_of_orders(user: str = CONFIG['Owner']['alt_username'], ids: list = [], price: float = ""):
#     return trading_bot.edit_price_of_orders(user=user, ids=ids, price=price)


# @app.get("/trading_bot/bot_trader", tags=["trading_bot"])
# def bot_trader(user: str = CONFIG['Owner']['alt_username'], coin_1: str = "BTC", coin_2: str = "USDT", market: str = "Binance", screener_name: str = "Crypto", interval: str = "4h"):
#     return trading_bot.bot_trader(user=user, coin_1=coin_1, coin_2=coin_2, market=market, screener_name=screener_name, interval=interval)


# @app.get("/trading_bot/get_account_balance", tags=["trading_bot"])
# def get_account_balance(user: str = CONFIG['Owner']['alt_username']):
#     return trading_bot.get_account_balance(user=user)


# @app.get("/trading_bot/get_candles", tags=["trading_bot"])
# def get_candles(
#     coin_1: str = "BTC",
#     coin_2: str = "USDT",
#     limit: int = 100,
#     interval: str = "4h",
# ):
#     return trading_bot.get_candles(coin_1=coin_1, coin_2=coin_2, limit=limit, interval=interval)


# @app.get("/trading_bot/get_indicator_data", tags=["trading_bot"])
# def indicator_data(
#     coin_1: str = "BTC", coin_2: str = "USDT", market: str= "Binance", screener_name: str = "Crypto", interval: str = "4h"
# ):
#     return trading_bot.indicator_data(coin_1=coin_1, coin_2=coin_2, market=market, screener_name=screener_name, interval=interval)

# @app.post("/trading_bot/auto_trader", tags=["trading_bot"])
# def auto_trader(user: str = CONFIG['Owner']['alt_username']):
#     return trading_bot.auto_trader(user=user)


# @app.get("/trading_bot/parser_activated_bot", tags=["trading_bot"])
# def parser_activated_bot() -> None:
#     return trading_bot.parser_activated_bot()


# @app.get("/trading_bot/plot_historical_data", tags=["trading_bot"])
# def plot_historical_data(coin_1: str = "BTC", coin_2: str = "USDT", interval: str = "1d", limit: int = 100):
#     return trading_bot.plot_historical_data(coin_1=coin_1, coin_2=coin_2, interval=interval, limit=limit)


# @app.get("/trading_bot/send_mail", tags=["trading_bot"])
# def send_mail(message: str, receiver: str =CONFIG['Owner']['alt_username']) -> None:
#     return trading_bot.send_mail(message=message, receiver=receiver)


# @app.get("/trading_bot/price_tracker", tags=["trading_bot"])
# def price_tracker(coin_1: str = "BTC", coin_2: str = "USDT", price: float = 0.0, mail: bool = False, receiver: str =CONFIG['Owner']['alt_username']) -> str:
#     return trading_bot.price_tracker(coin_1=coin_1, coin_2=coin_2, price=price, mail=mail, receiver=receiver)



if __name__ == "__main__":
    if __name__ == "__main__":
        uvicorn.run(app=app, host="192.168.0.207", port=6969)
