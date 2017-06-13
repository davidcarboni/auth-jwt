import jwt
from src.key import private_key, public_key


def sign(data):
    """Generates a JWT containing the given data."""
    return jwt.encode(data, private_key(), algorithm='ES256')


def decode(token):
    """Recovers the data from the given JWT."""
    return jwt.decode(token, public_key(), algorithms=['ES256'])
