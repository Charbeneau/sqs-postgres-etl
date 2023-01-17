import os
import psycopg2
from loguru import logger


def create_db_connection():
    """Creates a Postgres DB connection.

    Args:
        None

    Returns:
        A psycopg2 connection https://www.psycopg.org/docs/connection.html#connection.
    """
    connection = psycopg2.connect(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        database=os.getenv("DATABASE"),
    )
    return connection


def create_insert_query_string():
    """Creates a Postgres INSERT query string.

    Args:
        None

    Returns:
        An INSERT query string.
    """

    INSERT_QUERY = """INSERT INTO user_logins (user_id, device_type, 
    masked_ip, masked_device_id, locale, app_version, create_date)
    VALUES (%(user_id)s, %(device_type)s, %(masked_ip)s, %(masked_device_id)s, %(locale)s, %(app_version)s, %(create_date)s);"""
    return INSERT_QUERY


def insert_record_into_db(record: dict) -> None:
    """Inserts a record into a Postgres.

    Args:
        record: A dictionary containing user_id, device_type, masked_ip,
        masked_device_id, locale, app_version, create_date E.g.,
        {'user_id': '66e0635b-ce36-4ec7-aa9e-8a8fca9b83d4', 'app_version': 2,
        'device_type': 'ios', 'locale': None, 'masked_ip': 'MTMwLjExMS4xNjcuNTQ=',
        'masked_device_id': 'MTI3LTQyLTA4NjI=', 'create_date': datetime.now()}

    Returns:
        Nothing.
    """

    try:
        connection = create_db_connection()
        cursor = connection.cursor()

        cursor.execute(create_insert_query_string(), record)

        connection.commit()

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Failed to insert record into user_logins table! {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection closed.")
