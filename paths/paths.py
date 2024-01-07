import os

"""Absolute paths of the files used in the project."""
if "nadig" in os.path.expanduser("~"):
    HOME_DIRECTORY = os.path.expanduser("~")
    MARKET_DATA_DIRECTORY = rf"{HOME_DIRECTORY}\git\crypto_market_data"
    LOGFILE = rf"{HOME_DIRECTORY}\git\trading_bot\trading_bot_LOGFILE.log"
    CONFIG_FILE = rf"{HOME_DIRECTORY}\megamind_config.yaml"
    ORDER_HISTORY_FILE = rf"{MARKET_DATA_DIRECTORY}\trading_bot_order_history.csv"
    GAMING_JSON_FILE = rf"{MARKET_DATA_DIRECTORY}\.json"
    CRYPTO_CATEGORIES_FILE = rf"{MARKET_DATA_DIRECTORY}\cmc_categories.json"
elif "megamind" in os.path.expanduser("~"):
    HOME_DIRECTORY = os.path.expanduser("~")
    MARKET_DATA_DIRECTORY = rf"{HOME_DIRECTORY}/crypto_market_data"
    LOGFILE = rf"{HOME_DIRECTORY}/trading_bot_LOGFILE.log"
    CONFIG_FILE = rf"{HOME_DIRECTORY}/megamind_config.yaml"
    ORDER_HISTORY_FILE = rf"{MARKET_DATA_DIRECTORY}/trading_bot_order_history.csv"
    GAMING_JSON_FILE = rf"{MARKET_DATA_DIRECTORY}/.json"
    CRYPTO_CATEGORIES_FILE = rf"{MARKET_DATA_DIRECTORY}/cmc_categories.json"

else:
    raise("The paths of the config file, logfile and the data directories are undefined in paths.py!")