import os
import boto3
from utils import (
    SignalHandler,
    validate_message,
    process_message,
    insert_record_into_db,
)
import logging
import sys


AWS_PROFILE = os.getenv("AWS_PROFILE")
AWS_REGION = os.getenv("AWS_REGION")
ENDPOINT_URL = os.getenv("ENDPOINT_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES"))
WAIT_TIME = int(os.getenv("WAIT_TIME"))


boto3.setup_default_session(profile_name=AWS_PROFILE)
sqs = boto3.resource("sqs", region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)
queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == "__main__":

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
