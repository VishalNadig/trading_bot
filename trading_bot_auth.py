import argparse
import yaml
import database_handler
from paths import paths
import sys


PARSER = argparse.ArgumentParser()
LOGFILE = paths.LOGFILE
CONFIG_FILE = paths.CONFIG_FILE
with open(CONFIG_FILE) as file:
    CONFIG = yaml.safe_load(file)

def get_credentials_config_file(first_name: str = "", last_name: str = "", username: str = "") -> tuple:
    """Get API key and secret key for the specified user. If user is not mentioned then, first name and last name of the user can be used to retrieve the keys.

    Args:
        first_name (str, optional): First name of the user. Defaults to "".
        last_name (str, optional): Last name of the user. Defaults to "".
        user (str, optional): Username to retrieve the keys. Defaults to "".

    Returns:
        tuple: The API key and the secret key.
    """
    try:

        if first_name and last_name != "":
            user = first_name + last_name
            user = user.lower()
            user = user.replace(" ", "")
        else:
            user = username.lower()
            user = username.replace(" ", "")
        api_key = CONFIG["trading"]["accounts"][user]["api_key"]
        secret_key = CONFIG["trading"]["accounts"][user]["secret_key"]
        return api_key, secret_key
    except KeyError:
        sys.stdout.write("Key Error! Check user or first name and last name.\n")
        return {404: "Key Error! Check user or first name and last name."}

def add_user_credentials_config_file(
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

def update_user_credentials_config_file(first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",):
    """
    Updates the keys for a user in the trading accounts.

    Args:
        first_name (str): The first name of the user. Defaults to "".
        last_name (str): The last name of the user. Defaults to "".
        api_key (str): The API key for the user. Defaults to "".
        secret_key (str): The secret key for the user. Defaults to "".
        email (str): The email address of the user. Defaults to "".
        google_auth_key (str): The Google authentication key for the user. Defaults to "".

    Returns:
        dict: A dictionary with the HTTP status code and a message.
        If the user is not present, returns {404: "Error user not present!"}.
        If the user is updated successfully, returns {200: "User updated!"}.
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
        return {404: "Error user not present!"}
    else:
        dict_update["trading"]["accounts"][user] = dict_dump
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            yaml.safe_dump(dict_update, file)
        return {200: "User updated!"}


def delete_user_credentials_config_file(first_name: str, last_name: str, username: str):
    """
    Deletes a user from the CONFIG file.

    Args:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        user (str): The username of the user.

    Returns:
        dict: A dictionary containing the HTTP status code and a message indicating the result of the operation.
            - If the user is successfully deleted, the dictionary will contain the key 200 and the value "User deleted!".
            - If the user is not present, the dictionary will contain the key 404 and the value "Error user not present!".
    """
    if first_name is not None and last_name is not None:
        user = first_name + last_name
        user = user.lower()
        user = user.replace(" ", "")
    else:
        user = user.lower()
        user = user.replace(" ", "")

    if user in CONFIG["trading"]["accounts"]:
        del CONFIG["trading"]["accounts"][user]
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            yaml.safe_dump(CONFIG, file)
        return {200: "User deleted!"}
    else:
        return {404: "Error user not present!"}


def get_user_credentials_database(username: str = "", first_name: str = "", last_name: str = ""):
    """
    Retrieve credentials from the database based on the provided username, first name, and last name.

    Parameters:
        username (str): The username of the user whose credentials need to be retrieved. Defaults to an empty string.
        first_name (str): The first name of the user whose credentials need to be retrieved. Defaults to an empty string.
        last_name (str): The last name of the user whose credentials need to be retrieved. Defaults to an empty string.

    Returns:
        dict: A dictionary containing the user's credentials retrieved from the database.
    """
    return database_handler.get_user_credentials(username=username, first_name=first_name, last_name=last_name)


def add_user_credentials_database(first_name: str, last_name: str, api_key: str, secret_key: str, email: str, google_auth_key: str):
    """
    Add credentials to the database.

    Parameters:
        username (str): The username of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        api_key (str): The API key for the user.
        secret_key (str): The secret key for the user.
        email (str): The email address of the user.
        google_auth_key (str): The Google authentication key for the user.

    Returns:
        None
    """
    return database_handler.add_user_credentials(first_name=first_name, last_name=last_name, api_key=api_key, secret_key=secret_key, email=email, google_auth_key=google_auth_key)


def update_user_credentials_database(first_name: str, last_name: str, api_key: str, secret_key: str, email: str, google_auth_key: str):
    """
    Update credentials in the database.

    Parameters:
        username (str): The username of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        api_key (str): The API key for the user.
        secret_key (str): The secret key for the user.
        email (str): The email address of the user.
        google_auth_key (str): The Google authentication key for the user.

    Returns:
        None
    """
    return database_handler.update_user_credentials(first_name=first_name, last_name=last_name, api_key=api_key, secret_key=secret_key, email=email, google_auth_key=google_auth_key)


def delete_user_credentials_database(first_name: str, last_name: str, username: str = ""):
    """
    Delete credentials from the database.

    Parameters:
        username (str): The username of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.

    Returns:
        None
    """
    return database_handler.delete_user_credentials(first_name=first_name, last_name=last_name, username=username)

if __name__ == "__main__":
    print(get_credentials_config_file(username="vishalnadig"))