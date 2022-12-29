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
    # TODO: Make this work properly
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
        with open(CONFIG_FILE, "w") as file:
            yaml.safe_dump(dict_update, file)
    else:
        return "Error user already present!"


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


add_keys("Anjan", "Nadig", "API_KEY", "SECRET_KEY", "email@email.com", "ASWERFEWQ")
