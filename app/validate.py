import json
import jsonschema
from loguru import logger


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
