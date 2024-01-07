import os

"""Absolute paths of the files used in the project."""

# LOGFILE = r"/Users/akshathanadig/Downloads/Education/Computer Science/Python/Trading Bot/LOGFILE_MAC.log"
# LOGFILE = r"/home/pi/python_projects/trading_bot/LOGFILE.log"
# CONFIG_FILE = r"/Users/akshathanadig/Downloads/git/megamind_config.yaml"
# ORDER_HISTORY_FILE = r"/home/pi/python_programs/trading_bot/order_history.csv"
if "nadig" in os.path.expanduser("~"):
    LOGFILE = r"C:\Users\nadig\git\trading_bot\trading_bot_LOGFILE.log"
    CONFIG_FILE = r"C:\Users\nadig\megamind_config.yaml"
    ORDER_HISTORY_FILE = r"C:\Users\nadig\git\trading_bot\order_history.csv"
    MARKET_DATA_DIRECTORY = r"C:\Users\nadig\git\crypto_market_data"
    GAMING_JSON_FILE = rf"{MARKET_DATA_DIRECTORY}\.json"
    CRYPTO_CATEGORIES_FILE = rf"{MARKET_DATA_DIRECTORY}\cmc_categories.json"
elif "megamind" in os.path.expanduser("~"):
    LOGFILE = r"/home/megamind/trading_bot_LOGFILE.log"
    CONFIG_FILE = r"/home/megamind/megamind_config.yaml"
    ORDER_HISTORY_FILE = r"/home/megamind/trading_bot_order_history.csv"
    MARKET_DATA_DIRECTORY = r"/home/megamind/crypto_market_data"
    GAMING_JSON_FILE = rf"{MARKET_DATA_DIRECTORY}\.json"
    CRYPTO_CATEGORIES_FILE = rf"{MARKET_DATA_DIRECTORY}\cmc_categories.json"