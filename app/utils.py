import os
from signal import SIGINT, SIGTERM, signal
from loguru import logger
import boto3


AWS_PROFILE = os.getenv("AWS_PROFILE")


def setup_boto3(profile_name: str = AWS_PROFILE):
    """Sets up a boto3 session.

    Args:
        profile_name: AWS profile name.

    Returns:
        Nothing.
    """

    logger.info("Setting up boto3 default session.")
    boto3.setup_default_session(profile_name=profile_name)


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
