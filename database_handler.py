"""Python script to manage Authentication of users in a MySQL database."""
import logging

import sqlalchemy
from cryptography.fernet import Fernet
from sqlalchemy import MetaData, create_engine

from constants import CONFIG, DATABASE, HOSTNAME, LOGFILE, PASSWORD, PORT, URL, USER

logging.basicConfig(
    level=logging.INFO,
    filemode="a",
    filename=LOGFILE,
    format="%(asctime)s;%(levelname)s;%(message)s",
)

METADATA = MetaData()
# URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}"


def encrypt_data(
    key: str = CONFIG["database_creds"]["DATABASE_1"]["key"], password: str = ""
) -> dict:
    """Encrypt the sensitive credentials such as API key, SECRET key and Google Auth Key.

    Args:
        key (str, optional): The fernet key generated once at the start. Defaults to CONFIG['database_creds']['DATABASE_1']['key'].
        password (str, optional): The password to encrypt. Defaults to "".

    Returns:
        dict: Encrypted credentials dictionary 200 if successful. 404 If the password is wrong.
    """
    if password:
        fernet = Fernet(key)
        return {"password": fernet.encrypt(password.encode())}
    else:
        return {404: "Error password not found!"}


def decrypt_data(
    key: str = CONFIG["database_creds"]["DATABASE_1"]["key"], password: str = ""
) -> dict:
    """Decrypt the sensitive credentials to use for API call authentication.

    Args:
        key (str, optional): The fernet key generated once at the start. Defaults to CONFIG['database_creds']['DATABASE_1']['key'].
        password (str, optional): The password to decrypt. Defaults to "".

    Returns:
        dict: Decrypted credentials dictionary 200 if successful. 404 If the password is wrong.
    """
    if password:
        fernet = Fernet(key)
        return {"password": fernet.decrypt(bytes(password, "utf-8")).decode()}
    else:
        return {404: "Error password not found!"}


def get_user_credentials(username: str = "", first_name: str = "", last_name: str = "") -> tuple:
    """Fetch the user credentials from the database.

    Args:
        username (str, optional): The username of the user. Defaults to "".
        first_name (str, optional): The first name of the user. Pass this argument in case the username of the user is not known. Defaults to "".
        last_name (str, optional): The last name of the user. Pass this argument in case the username of the user is not known. Defaults to "".

    Returns:
        tuple: Returns the tuple of decrypted API key and secret key of the user for API calls authentication.
        dict: Returns a dictionary with a key of 404 and value of "User Not Found!" in case the user is not found.
    """
    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")

    engine = create_engine(URL)
    connection = engine.connect()

    user_exists = connection.execute(
        "SELECT EXISTS(SELECT 1 FROM trading_bot.users WHERE username = %s)",
        username or (first_name.title() + " " + last_name.title()),
    ).fetchone()[0]

    if user_exists:

        encrypted_api_key, encrypted_secret_key = connection.execute(
            "SELECT api_key, secret_key FROM users WHERE username = %s", user
        ).fetchone()

        api_key = decrypt_data(password=encrypted_api_key)["password"]
        secret_key = decrypt_data(password=encrypted_secret_key)["password"]
        return api_key, secret_key
    else:
        return {404: "User Not Found!"}


def add_user_credentials(
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
) -> dict:
    """Add API key and the secret key for a new user. If the user already exists. Return exception.

    Args:
        username (str, optional): The usename of the user. Defaults to "".
        first_name (str, optional): First name of the user. Defaults to "".
        last_name (str, optional): Last name of the user. Defaults to "".
        api_key (str, optional): API key of the user. Defaults to "".
        secret_key (str, optional): API secret of the user. Defaults to "".
        email (str, optional): Email of the user. Defaults to "".
        google_auth_key (str, optional): The google auth key of the user. Defaults to "".

    Returns:
        dict: Returns the tuple of decrypted API key and secret key of the user for API calls authentication.
        Exception: Returns exception if failure due to unknown reasons.
    """
    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")
    try:
        engine = create_engine(URL)
    except Exception as e:
        return {404: e}
    connection = engine.connect()

    encrypted_api_key = encrypt_data(password=api_key)["password"].decode("utf-8")
    encrypted_secret_key = encrypt_data(password=secret_key)["password"].decode("utf-8")
    encrypted_google_auth_key = encrypt_data(password=google_auth_key)["password"].decode("utf-8")

    try:
        if (
            connection.execute(
                sqlalchemy.text(f""" SELECT username from users where username = '{user}';""")
            ).fetchone()
            is not None
        ):
            if (
                user
                != connection.execute(
                    sqlalchemy.text(f""" SELECT username from users where username = '{user}';""")
                ).fetchone()[0]
            ):
                engine.connect().execute(
                    sqlalchemy.text(
                        f"""
                        INSERT INTO trading_bot.users (username, first_name, last_name, email, api_key, secret_key, google_auth_key)
                        VALUES ('{first_name.lower() + "" + last_name.lower()}', '{first_name}', '{last_name}', '{email}', '{encrypted_api_key}', '{encrypted_secret_key}', '{encrypted_google_auth_key}');
                    """
                    )
                )
                return {200: "User added!"}
            else:
                return {404: "Error user already present!"}
        else:
            engine.connect().execute(
                sqlalchemy.text(
                    f"""
                    INSERT INTO trading_bot.users (username, first_name, last_name, email, api_key, secret_key, google_auth_key)
                        VALUES ('{first_name.lower() + "" + last_name.lower()}', '{first_name}', '{last_name}', '{email}', '{encrypted_api_key}', '{encrypted_secret_key}', '{encrypted_google_auth_key}');
                    """
                )
            )
            return {200: "User added!"}
    except Exception as e:
        print(e)


def update_user_credentials(
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    api_key: str = "",
    secret_key: str = "",
    email: str = "",
    google_auth_key: str = "",
) -> dict:
    """Update the user credentials in the database.

    Args:
        username (str, optional): The username of the user. Defaults to "".
        first_name (str, optional): The first name of the user Pass this argument if the username of the user is not known. Defaults to "".
        last_name (str, optional): The last name of the users. Pass this argument if the username of the user is not known. Defaults to "".
        api_key (str, optional): The API key of the user. Defaults to "".
        secret_key (str, optional): The secret key of the user. Defaults to "".
        email (str, optional): The email ID of the user. Defaults to "".
        google_auth_key (str, optional): The google auth key of the user. Defaults to "".

    Returns:
        dict: 200 if updating the credentials was successful. 404 if the update failed or the user was not found.
    """
    if api_key and secret_key and google_auth_key:
        pass
    else:
        raise ValueError("Google auth key, api_key and secret_key must be provided.")
    if username:
        user = username.lower()
        user = user.replace(" ", "")
    elif first_name and last_name:
        user = first_name + last_name
        user = user.lower()
        user = user.replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")
    engine = create_engine(URL)
    connection = engine.connect()
    encrypted_api_key = encrypt_data(password=api_key)["password"].decode("utf-8")
    encrypted_secret_key = encrypt_data(password=secret_key)["password"].decode("utf-8")
    encrypted_google_auth_key = encrypt_data(password=google_auth_key)["password"].decode("utf-8")
    if (
        user
        == connection.execute(
            f"""SELECT username from users WHERE username = '{user}'"""
        ).fetchone()[0]
    ):
        if encrypted_api_key and encrypted_secret_key and encrypted_google_auth_key and email:
            connection.execute(
                f"""UPDATE users SET api_key = '{encrypted_api_key}', secret_key = '{encrypted_secret_key}', google_auth_key = '{encrypted_google_auth_key}', email = '{email}' WHERE username = '{user}';"""
            )
            return {200: "User Updated"}
        elif (
            encrypted_api_key
            and encrypted_api_key
            != connection.execute(
                f""" SELECT API_KEY FROM users WHERE username = '{user}' """
            ).fetchone()[0]
        ):
            connection.execute(
                f"""UPDATE users SET api_key = '{encrypted_api_key}' WHERE username = '{user}';"""
            )
            return {200: "User api_key Updated!"}
        elif (
            encrypted_secret_key
            and encrypted_secret_key
            != connection.execute(
                f""" SELECT SECRET_KEY FROM users WHERE username = '{user}' """
            ).fetchone()[0]
        ):
            connection.execute(
                f"""UPDATE users SET secret_key = '{encrypted_secret_key}' WHERE username = '{user}';"""
            )
            return {200: "User secret_key Updated!"}
        elif (
            encrypted_google_auth_key
            and encrypted_google_auth_key
            != connection.execute(
                f"""SELECT GOOGLE_AUTH_KEY FROM users WHERE username = '{user}'"""
            ).fetchone()[0]
        ):
            connection.execute(
                f"""UPDATE users SET google_auth_key = '{encrypted_google_auth_key}' WHERE username = '{user}';"""
            )
            return {200: "User google_auth_key Updated!"}
        elif (
            email
            and email
            != connection.execute(
                f"""SELECT EMAIL FROM users WHERE username = {user}"""
            ).fetchone()[0]
        ):
            connection.execute(f"""UPDATE users SET email = '{email}' WHERE username = '{user}';""")
            return {200: "User email Updated!"}
        else:
            return {400: "User Already Present!"}
    else:
        return {404: "User not Found!"}


def delete_user_credentials(username: str = "", first_name: str = "", last_name: str = "") -> dict:
    """Delete a user from the database.

    Args:
        username (str, optional): The username of the user. Defaults to "".
        first_name (str, optional): The first name of the user Pass this argument if the username of the user is not known. Defaults to "".
        last_name (str, optional): The last name of the users. Pass this argument if the username of the user is not known. Defaults to "".

    Returns:
        dict: 200 if deleting the user was successful. 404 if the delete failed or the user was not found.
    """

    if username:
        user = username.lower().replace(" ", "")
    elif first_name and last_name:
        user = (first_name + last_name).lower().replace(" ", "")
    else:
        raise ValueError("Either username or first_name and last_name must be provided.")

    engine = create_engine(URL)
    connection = engine.connect()
    try:
        user_exsists = connection.execute(
            f"SELECT * FROM users WHERE username = '{user}'"
        ).fetchone()
        if user_exsists:
            id = connection.execute(f"SELECT id FROM users WHERE username = '{user}';").fetchone()[
                0
            ]
            connection.execute(f"DELETE FROM users WHERE id = '{id}';")
            max_id = connection.execute("SELECT MAX(Id) FROM users;").fetchone()[0]
            if max_id is not None:
                connection.execute(f"ALTER TABLE users AUTO_INCREMENT={max_id};")
            else:
                connection.execute("ALTER TABLE users AUTO_INCREMENT=1;")
            return {200: "User Deleted"}
        else:
            return {404: "User Not Found"}
    except Exception as e:
        return {404: e}


if __name__ == "__main__":
    print(add_user_credentials(username="vishalnadig", first_name="Vishal", last_name="Nadig", email="stalion.dan@gmail.com", api_key="591c102dfa8c9a46e6c29186aed24795dfdabda1ce77e9e4", secret_key="84f69be6c8a129f16c02e22b71b1e8382fa7c92719b69ea7313b0af9551ebda2", google_auth_key="EVOCSKCMCF7WW6JW"))
    # print(get_user_credentials(username="vishalnadig"))
    # print(
    #     update_user_credentials(
    #         username="vishalnadig",
    #         email="vishal@12",
    #         api_key="1234567890",
    #         secret_key="1234567890",
    #         google_auth_key="1234567890",
    #     )
    # )
    # print(delete_user_credentials(username="vishalnadig"))
    pass
