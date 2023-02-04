import argparse
import yaml
from paths import paths

PARSER = argparse.ArgumentParser()
LOGFILE = paths.LOGFILE
CONFIG_FILE = paths.CONFIG_FILE
with open(CONFIG_FILE) as file:
    CONFIG = yaml.safe_load(file)


def add_keys(
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
) -> None:
    """Add API key and the secret key for a new user. If the user already exists. Return exception.

    Args:
        first_name (str, optional): First name of the user. Defaults to "".
        last_name (str, optional): Last name of the user. Defaults to "".
        api_key (str, optional): API key of the user.
        secret_key (str, optional): API secret of the user.
    """
    user = first_name + last_name
    user = user.lower()
    user = user.replace(" ", "")
    dict_update = CONFIG
    dict_dump = {
        "username": first_name.title() + last_name.title(),
        "email": email,
        "api_key": api_key,
        "secret_key": secret_key,
        "google_auth_key": google_auth_key,
    }

    if user not in dict_update["trading"]["accounts"]:
        dict_update["trading"]["accounts"][user] = dict_dump
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            yaml.safe_dump(dict_update, file)
        return {200: "User added!"}
    else:
        return {404: "Error user already present!"}


def add_keys_cli() -> None:
    """Add keys via the interactive terminal."""
    PARSER.add_argument(
        "-f",
        "--first_name",
        required=True,
        type=str,
        help="First name of the user for which the keys are to be added",
    )
    PARSER.add_argument(
        "-l",
        "--last_name",
        required=True,
        type=str,
        help="Last name of the user for which the keys are to be added",
    )
    PARSER.add_argument("-a", "--api_key", required=True, type=str, help="API key of the user")
    PARSER.add_argument(
        "-s", "--secret_key", required=True, type=str, help="API Secret key of the user"
    )
    args = PARSER.parse_args()
    add_keys(
        first_name=args.first_name,
        last_name=args.last_name,
        api_key=args.api_key,
        secret_key=args.secret_key,
    )

def del_keys(username: str = "", first_name: str = "", last_name: str = ""):
    # TODO: Make this work.
    if username != "":
        pass
    elif first_name and last_name != "":
        pass
    else:
        return {404: "User not found"}

def del_keys_cli():
    # TODO: Make this work
    PARSER.add_argument(
        "-f",
        "--first_name",
        required=True,
        type=str,
        help="First name of the user for which the keys are to be added",
    )
    PARSER.add_argument(
        "-l",
        "--last_name",
        required=True,
        type=str,
        help="Last name of the user for which the keys are to be added",
    )
    PARSER.add_argument("-a", "--api_key", required=True, type=str, help="API key of the user")
    PARSER.add_argument(
        "-s", "--secret_key", required=True, type=str, help="API Secret key of the user"
    )
    args = PARSER.parse_args()
    del_keys(username=args.first_name.title()+args.last_name.title(), first_name=args.first_name, last_name=args.last_name)


def update_keys(first_name: str = "",
    last_name: str = "",
    username: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = ""):
    # TODO: Make this work
    pass
add_keys("Anjan", "Nadig", "API_KEY", "SECRET_KEY", "email@email.com", "ASWERFEWQ")
