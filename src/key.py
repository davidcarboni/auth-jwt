import os
from Crypto.PublicKey import RSA

# The key pair for this instance
_key_pair = RSA.generate(int(os.getenv("KEY_SIZE", 4096)))


def private_key():
    """Renders the private key in PEM format, unencrypted, using PKCS1.
    This is useful for signing JWT tokens.
    """
    return _key_pair.exportKey('PEM')


def public_key():
    """Renders the public key in PEM format using PKCS1.
    This is useful for verifying JWT token signatures.
    """
    return _key_pair.publickey().exportKey('PEM')
