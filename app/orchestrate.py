import os
from utils import setup_boto3
from datetime import datetime
from transform import encode_string, semver_str_to_int
from models import create_user_login_model
from validate import validate_message
from db import add_user_login_to_db
import boto3
from loguru import logger


AWS_REGION = os.getenv("AWS_REGION")
ENDPOINT_URL = os.getenv("ENDPOINT_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES"))
WAIT_TIME = int(os.getenv("WAIT_TIME"))


def process_message(d: dict) -> dict:
    """Processes an SQS message.

    Args:
        d: A dictionary with keys user_id, app_version,
        device_type, ip, locale, and device_id.

    Returns:
        A dictionary with keys user_id, app_version,
        device_type, masked_ip, locale, masked_device_id,
        and create_date.
    """

    logger.info("Creating masked_ip.")
    d["masked_ip"] = encode_string(d["ip"])
    del d["ip"]

    logger.info("Creating masked_device_id.")
    d["masked_device_id"] = encode_string(d["device_id"])
    del d["device_id"]

    logger.info("Converting app_version to an integer.")
    d["app_version"] = semver_str_to_int(d["app_version"])

    logger.info("Adding create_date.")
    d["create_date"] = datetime.now()

    return d


def handle_message(message) -> None:
    """Handles an SQS message's validation,
    processing, and insertion into Postgres.

    Args:
        message: An SQS message (i.e., SQS.Message)

    Returns:
        Nothing.
    """

    validated = validate_message(message)
    processed = process_message(validated)
    user_login = create_user_login_model(processed)
    add_user_login_to_db(user_login)


def receive_messages() -> None:
    """Receives SQS messages,
    and runs handle_message() on them.

    Args:
        None.

    Returns:
        Nothing.
    """

    setup_boto3()
    sqs = boto3.resource("sqs", region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)
    queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

    messages = queue.receive_messages(
        MaxNumberOfMessages=MAX_MESSAGES, WaitTimeSeconds=WAIT_TIME
    )
    for message in messages:
        try:
            handle_message(message)
        except Exception as e:

            logger.error(f"Exception while processing message: {repr(e)}!")

            continue

        message.delete()
