"""Python script to manage Authentication of users to use the trading bot."""
import argparse
import logging

import yaml

import database_handler
from constants import CONFIG, CONFIG_FILE, LOGFILE

PARSER = argparse.ArgumentParser()
logging.basicConfig(
    level=logging.INFO,
    filemode="a",
    filename=LOGFILE,
    format="%(asctime)s;%(levelname)s;%(message)s",
)


def get_credentials_config_file(
    first_name: str = "", last_name: str = "", username: str = ""
) -> tuple:
    """Get API key and secret key for the specified user. If user is not mentioned then, first name and last name of the user can be used to retrieve the keys.

    Args:
        first_name (str, optional): First name of the user. Defaults to "".
        last_name (str, optional): Last name of the user. Defaults to "".
        user (str, optional): Username to retrieve the keys. Defaults to "".

    Returns:
        tuple: The API key and the secret key.
    """
    try:

        if username:
            user = username.lower().replace(" ", "")
        elif first_name and last_name:
            user = (first_name + last_name).lower().replace(" ", "")
        else:
            raise ValueError("Either username or first_name and last_name must be provided.")
        api_key = CONFIG["trading"]["accounts"][user]["api_key"]
        secret_key = CONFIG["trading"]["accounts"][user]["secret_key"]
        logging.info(f"API key and Secret key retrieved for {user}.")
        return api_key, secret_key
    except KeyError:
        logging.info("Key Error! Check user or first name and last name.")
        return {404: "Key Error! Check user or first name and last name."}


def add_user_credentials_config_file(
    username: str = "",
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
    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")
    config_dictionary = CONFIG
    updated_dictionary = {
        "username": first_name.title() + last_name.title(),
        "email": email,
        "api_key": api_key,
        "secret_key": secret_key,
        "google_auth_key": google_auth_key,
    }

    if user not in config_dictionary["trading"]["accounts"]:
        config_dictionary["trading"]["accounts"][user] = updated_dictionary
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            yaml.safe_dump(config_dictionary, file)
        logging.info(f"{user} added successfully.")
        return {200: "User added!"}
    else:
        logging.info("Error user already present!")
        return {404: "Error user already present!"}


def update_user_credentials_config_file(
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
):
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
    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")
    config_dictionary = CONFIG
    updated_dictionary = {
        "username": first_name.title() + last_name.title(),
        "email": email,
        "api_key": api_key,
        "secret_key": secret_key,
        "google_auth_key": google_auth_key,
    }
    if user not in config_dictionary["trading"]["accounts"]:
        logging.info("Error user not present!")
        return {404: "Error user not present!"}
    else:
        config_dictionary["trading"]["accounts"][user] = updated_dictionary
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            yaml.safe_dump(config_dictionary, file)
        logging.info(f"{user} updated successfully.")
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
    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")

    if user in CONFIG["trading"]["accounts"]:
        del CONFIG["trading"]["accounts"][user]
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            yaml.safe_dump(CONFIG, file)
        logging.info(f"{user} deleted successfully.")
        return {200: "User deleted!"}
    else:
        logging.info("Error user not present!")
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
    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")
    logging.info(f"Retrieving credentials for {user}.")
    return database_handler.get_user_credentials(
        username=user, first_name=first_name, last_name=last_name
    )


def add_user_credentials_database(
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
):
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
    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")
    logging.info(f"Adding credentials for {user}.")
    return database_handler.add_user_credentials(
        username=user,
        first_name=first_name,
        last_name=last_name,
        api_key=api_key,
        secret_key=secret_key,
        email=email,
        google_auth_key=google_auth_key,
    )


def update_user_credentials_database(
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
):
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
    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")
    logging.info(f"Updating credentials for {user}.")
    return database_handler.update_user_credentials(
        username=user,
        first_name=first_name,
        last_name=last_name,
        api_key=api_key,
        secret_key=secret_key,
        email=email,
        google_auth_key=google_auth_key,
    )


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
    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")
    logging.info(f"Deleting credentials for {user}.")
    return database_handler.delete_user_credentials(
        first_name=first_name, last_name=last_name, username=user
    )


def get_user_credentials(first_name: str = "", last_name: str = "", username: str = ""):
    """
    Retrieves the user credentials based on the provided parameters.

    Parameters:
        first_name (str): The first name of the user. Defaults to an empty string.
        last_name (str): The last name of the user. Defaults to an empty string.
        username (str): The username of the user. Defaults to an empty string.

    Returns:
        User credentials (dict): A dictionary containing the user credentials.

    Raises:
        ValueError: If neither the username nor the first_name and last_name are provided.
    """
    if username:
        user = username.lower().replace(" ", "")
        try:
            return get_user_credentials_database(username=user)
        except Exception as e:
            logging.error(e)
            return {404: e}
    elif first_name and last_name:
        try:
            return get_user_credentials_database(first_name=first_name, last_name=last_name)
        except Exception as e:
            logging.error(e)
            try:
                return get_credentials_config_file(first_name=first_name, last_name=last_name)
            except Exception as e:
                logging.error(e)
                return {404: e}
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")


def add_user_credentials(first_name: str = "", last_name: str = "", username: str = ""):
    """
    Adds user credentials to the system.

    Args:
        first_name (str, optional): The first name of the user. Defaults to "".
        last_name (str, optional): The last name of the user. Defaults to "".
        username (str, optional): The username of the user. Defaults to "".

    Returns:
        str: The result of adding user credentials.

    Raises:
        ValueError: If neither the username nor the first_name and last_name are provided.
    """
    if username:
        user = username.lower().replace(" ", "")
        try:
            get_user_credentials_database(username=user)
            get_credentials_config_file(username=username)
        except Exception:
            logging.error(Exception)
            return {404: Exception}
    elif first_name and last_name:
        try:
            get_user_credentials_database(first_name=first_name, last_name=last_name)
            get_credentials_config_file(first_name=first_name, last_name=last_name)
        except Exception:
            logging.error(Exception)
            return {404: Exception}
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")


def update_user_credentials(first_name: str = "", last_name: str = "", username: str = "", api_key="", secret_key="", email="", google_auth_key=""):
    """
    Updates the user's credentials in the system.

    Args:
        first_name (str, optional): The user's first name. Defaults to "".
        last_name (str, optional): The user's last name. Defaults to "".
        username (str, optional): The user's username. Defaults to "".

    Raises:
        Exception: If an error occurs while updating the user's credentials.
        ValueError: If either `username` or `first_name` and `last_name` are not provided.

    Returns:
        None
    """
    if username:
        user = username.lower().replace(" ", "")
        try:
            update_user_credentials_database(username=user, api_key=api_key, secret_key=secret_key, email=email, google_auth_key=google_auth_key)
            update_user_credentials_config_file(username=user, api_key=api_key, secret_key=secret_key, email=email, google_auth_key=google_auth_key)
        except Exception:
            logging.error(Exception)
            return {404: Exception}
    elif first_name and last_name:
        try:
            update_user_credentials_database(first_name=first_name, last_name=last_name, api_key=api_key, secret_key=secret_key, email=email, google_auth_key=google_auth_key)
            update_user_credentials_config_file(first_name=first_name, last_name=last_name, api_key=api_key, secret_key=secret_key, email=email, google_auth_key=google_auth_key)
        except Exception:
            logging.error(Exception)
            return {404: Exception}
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")


def delete_user_credentials(first_name: str = "", last_name: str = "", username: str = ""):
    """
    Deletes user credentials from the config file and the database.

    Args:
        first_name (str): The first name of the user. Defaults to an empty string.
        last_name (str): The last name of the user. Defaults to an empty string.
        username (str): The username of the user. Defaults to an empty string.

    Raises:
        Exception: If an error occurs while deleting the user credentials.
        ValueError: If neither username nor first_name and last_name are provided.
    """
    if username:
        user = username.lower().replace(" ", "")
        try:
            delete_user_credentials_database(username=user)
            delete_user_credentials_config_file(username=username)
        except Exception:
            logging.error(Exception)
            return {404: Exception}
    elif first_name and last_name:
        try:
            delete_user_credentials_database(first_name=first_name, last_name=last_name)
            delete_user_credentials_config_file(first_name=first_name, last_name=last_name)
        except Exception:
            logging.error(Exception)
            return {404: Exception}
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")


if __name__ == "__main__":
    print(get_credentials_config_file(username="vishalnadig"))
