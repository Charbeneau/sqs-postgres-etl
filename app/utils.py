import os
import base64
import psycopg2
import json
import jsonschema
from datetime import datetime
import time
from signal import SIGINT, SIGTERM, signal
from loguru import logger
import boto3


AWS_PROFILE = os.getenv("AWS_PROFILE")
AWS_REGION = os.getenv("AWS_REGION")
ENDPOINT_URL = os.getenv("ENDPOINT_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES"))
WAIT_TIME = int(os.getenv("WAIT_TIME"))


SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Behold, our schema!!",
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "app_version": {"type": "string", "pattern": "[0-9].[0-9]+"},
        "device_type": {"type": "string"},
        "ip": {"type": "string"},
        "locale": {"type": ["string", "null"]},
        "device_id": {"type": "string"},
    },
    "required": ["user_id", "app_version", "device_type", "ip", "locale", "device_id"],
}


def setup_boto3(profile_name: str=AWS_PROFILE):
    """Sets up a boto3 session.

    Args:
        profile_name: AWS profile name.

    Returns:
        Nothing.
    """

    logger.info("Setting up boto3 default session.")
    boto3.setup_default_session(profile_name=profile_name)


def encode_string(string: str) -> str:
    """Base64 encodes a string.

    Args:
        string: String to be encoded.  E.g., '123.4.56.789'

    Returns:
        Encoded string.  E.g., 'MTIzLjQuNTYuNzg5'.
    """

    string_bytes = string.encode("ascii")
    base64_bytes = base64.b64encode(string_bytes)

    return base64_bytes.decode("ascii")


def semver_str_to_int(string: str) -> int:
    """Converts a SemVer string to an integer.

    Args:
        string: String to be converted.  E.g., '2.3.0'

    Returns:
        The major version as an integer.  E.g., 2.
    """

    return int(string.split(".")[0])


def validate_message(message) -> None:
    """Validates an SQS message against a schema.

    Args:
        message: An SQS message (i.e., SQS.Message)

    Returns:
        A dictionary representation of the message if it's valid.
    """
    logger.info(f"\nmessage_id: {message.message_id}")

    d = json.loads(message.body)

    logger.info("Validating message format.")
    try:

        jsonschema.validate(d, SCHEMA)

    except jsonschema.exceptions.ValidationError as e:

        logger.error("Invalid message format!")
        logger.error(repr(e))

    return d


def process_message(d: dict) -> dict:
    """Processes an SQS message.

    Args:
        d: A dictionary with keys user_id, app_version,
        device_type, ip, locale, and device_id.

    Returns:
        The same dictionary with allkeys user_id, app_version,
        device_type, ip, masked_ip, device_id, masked_device_id,
        locale, and create_date.
    """

    logger.info("Creating masked_ip.")
    d["masked_ip"] = encode_string(d["ip"])

    logger.info("Creating masked_device_id.")
    d["masked_device_id"] = encode_string(d["device_id"])

    logger.info("Converting app_version to an integer.")
    d["app_version"] = semver_str_to_int(d["app_version"])

    logger.info("Adding create_date.")
    d["create_date"] = datetime.now()

    return d


def insert_record_into_db(record: dict) -> None:
    """Inserts a record into a PostgresDB.

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
        connection = psycopg2.connect(
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
            database=os.getenv("DATABASE"),
        )
        cursor = connection.cursor()

        INSERT_QUERY = """INSERT INTO user_logins (user_id, device_type, 
        masked_ip, masked_device_id, locale, app_version, create_date)
        VALUES (%(user_id)s, %(device_type)s, %(masked_ip)s, %(masked_device_id)s, %(locale)s, %(app_version)s, %(create_date)s);"""
        cursor.execute(INSERT_QUERY, record)

        connection.commit()
        count = cursor.rowcount
        logger.info(f"{count} Record inserted successfully into user_logins table.")

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Failed to insert record into user_logins table! {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection closed.")


class SignalHandler:
    """Detects whether or not a SIGINT or SIGTERM has been sent.

    Attributes:

        signal_received:  A boolean indicating whether or not a signal
        has been received..
    """

    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        logger.info(f"Handling signal {signal}, exiting gracefully.")
        self.received_signal = True

def main():
    """Wraps the functions of the app.

    Args:
        None.

    Returns:
        Nothing.
    """

    setup_boto3()
    sqs = boto3.resource("sqs", region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)
    queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

    signal_handler = SignalHandler()
    while not signal_handler.received_signal:
        messages = queue.receive_messages(
            MaxNumberOfMessages=MAX_MESSAGES, WaitTimeSeconds=WAIT_TIME
        )
        for message in messages:
            try:
                d = validate_message(message)
                record = process_message(d)
                insert_record_into_db(record)
            except Exception as e:

                logger.error(f"Exception while processing message: {repr(e)}!")

                continue

            message.delete()