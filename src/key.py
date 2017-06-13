import uuid
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption


# The key pair for this instance (elliptic curve ED25519)
# TODO: confirm the curve to use. SECP256R1 generates keys as per ssh-keygen -t ecdsa ("ecdsa-sha2-nistp256")
_key = {
    'id': uuid.uuid4(),
    'key_pair': ec.generate_private_key(ec.SECP256R1(), default_backend())
}


def key_id():
    return _key["id"]


def private_key():
    """Renders the private key in PEM format, unencrypted, in PKCS8 format.
    This is used for signing JWT tokens.
    """
    return _key["key_pair"].private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())


def public_key():
    """Renders the public key in PEM format.
    This is used for verifying JWT token signatures.
    """
    return _key["key_pair"].public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)
