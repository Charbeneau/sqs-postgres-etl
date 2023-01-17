from utils import SignalHandler
from orchestrate import receive_messages


def main():
    """Wraps the SignalHandler and receive_message().

    Args:
        None.

    Returns:
        Nothing.
    """

    signal_handler = SignalHandler()
    while not signal_handler.received_signal:
        receive_messages()


if __name__ == "__main__":

    main()
