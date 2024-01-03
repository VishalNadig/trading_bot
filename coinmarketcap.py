import json
import os
from datetime import datetime

import pandas as pd
import requests

import constants
from paths import paths


def coinmarket_cap(coin_name: str = "BTC") -> dict:
    """Get the market capitalization of the coin

    Args:
        coin_name (str, optional): The coin to get the market capitalization of. Defaults to "BTC".

    Returns:
        dict: The dictionary of the coins market capitalization
    """
    url = constants.URL_DICT["COINMARKETCAP_CATEGORY"]["URL"]
    parameters = constants.URL_DICT["COINMARKETCAP_CATEGORY"]["parameters"]
    headers = constants.URL_DICT["COINMARKETCAP_CATEGORY"]["headers"]
    file_name = "GAMBLING_CATEGORY"
    response = requests.get(url, params=parameters, headers=headers)
    print(response.json())
    with open(
        rf"C:\Users\nadig\git\crypto_market_data\{datetime.now().strftime('%Y-%m-%d')}"
        + file_name
        + ".json",
        "w",
    ) as json_file:
        json.dump(response.json(), json_file)
    # json_dataframe = pd.DataFrame(response.json())
    # print(json_dataframe)
    # with open(rf"C:\Users\nadig\git\crypto_market_data\{datetime.now().strftime('%Y-%m-%d')}{file_name}.json") as json_file:
    #     json_dataframe = json.load(json_file)
    # # for keys in json_dataframe['data']:
    # #     print()
    # for coins in json_dataframe['data']['coins']:
    #     print(coins['name'])
    # json_dataframe = pd.read_json(rf"C:\Users\nadig\git\crypto_market_data\cmc_categories.json")
    # print(json_dataframe.keys())

    # pd.DataFrame.to_json(json_dataframe, path_or_buf=rf"C:\Users\nadig\git\crypto_market_data\{datetime.now().strftime('%Y-%m-%d')}{file_name}.json")
    # with open(rf"C:\Users\nadig\git\crypto_market_data\{datetime.now().strftime('%Y-%m-%d')}{file_name}.json") as json_file:
    #     json_dataframe = pd.read_json(json_file)
    # print(json_dataframe.head()['quote'])


def get_all_categoies():
    """
    Reads a JSON file containing a list of categories and returns the data as a Python object.

    Returns:
        list: A list of categories.
    """
    with open(paths.CRYPTO_CATEGORIES_FILE) as json_file:
        json_dataframe = pd.DataFrame(json.load(json_file)["data"])
    return pd.DataFrame(json_dataframe["name"].values)


def get_all_coins_in_category(category: str = ""):
    """
    Reads a JSON file containing a list of coins in a category and returns the data as a Python object.

    Returns:
        list: A list of coins in the category.
    """
    categories = get_all_categoies()
    if category and category in categories[0].values:
        category = category.lower().replace(" ", "_")
        print(rf"C:\Users\nadig\git\crypto_market_data\{category}_category.json")
        if os.path.exists(rf"C:\Users\nadig\git\crypto_market_data\{category}_category.json"):
            print(f"File {category}_category.json exists")
            with open(
                rf"C:\Users\nadig\git\crypto_market_data\{category}_category.json"
            ) as json_file:
                json_dataframe = pd.DataFrame(json.load(json_file)["data"])
            return pd.DataFrame([coin["name"] for coin in json_dataframe["coins"]])
        else:
            return {404: "The category doesn't exist"}
    else:
        return {404: "The category doesn't exist"}


def get_coin_in_category(coin: str = "", category: str = ""):
    if coin and get_all_coins_in_category(category):
        pass


# print(get_all_categoies())
# print(get_all_coins_in_category(category="Real World Assets"))


def get_market_cap(coin: str = "", symbol: str = ""):
    """
    Reads a JSON file containing market capitalization data and returns a pandas DataFrame.

    Returns:
        pandas.DataFrame: The DataFrame containing the market capitalization data.
    """
    if coin or symbol:
        dataframe = pd.read_json(
            rf"C:\Users\nadig\git\crypto_market_data\2023-12-27_market_cap.json"
        )
        return dataframe[
            dataframe["name"].str.contains(coin) | dataframe["symbol"].str.contains(symbol)
        ]["self_reported_market_cap"].values
    else:
        return None


print(get_market_cap(coin="Immutable", symbol="IMX"))
