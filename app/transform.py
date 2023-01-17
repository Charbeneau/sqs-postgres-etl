import base64


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
