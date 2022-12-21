from app.utils import encode_string


def test_encode_string():

    observed = encode_string("123.4.56.789")
    expected = "MTIzLjQuNTYuNzg5"

    assert observed == expected
