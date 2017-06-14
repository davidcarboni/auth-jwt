import jwt
from .key import private_key, key_id
from .database import get_key


def sign(data):

    """Generates a JWT containing the given data and returns it as a UTF8 string.
    The ID of this instance's key is added to the headers so that when the token is presented,
    the receiving instance can determine which key to use for signature validation.
    :param data: The set of claims to be included in the JWT.
    :return: A signed JWT as a UTF8 string. Two headers are added:
        * iss (issuer) which will be "auth"
        * kid (key ID) identifies the key that signed the token
    TODO: decide how long-lived we'd like tokens to be (exp header).
    """
    headers = {
        'iss': 'auth',
        'kid': key_id()
    }
    return jwt.encode(data, private_key(), algorithm='ES256', headers=headers).decode("UTF8")


def decode(token):
    """Recovers the data from the given JWT.
    The public key is requested from the database because the token may not have been signed by this instance.
    """
    header = jwt.get_unverified_header(token)
    public_key = get_key(header.get("kid"))
    return jwt.decode(token, public_key, algorithms=['ES256'])
