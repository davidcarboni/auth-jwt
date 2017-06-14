from .database import add_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

_key = None


def key_id():
    """Returns the id of the current key for this instance."""
    return _key["id"]


def private_key():
    """Renders the private key in PEM format, unencrypted, in PKCS8 format and returns it as a UTF8 string.
    This is used for signing JWTs.
    """
    return _key["private"].private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode("UTF8")


def _public_key(private):
    """Renders the public key in OpenSSH format and returns it as a UTF8 string.
    This is used for verifying JWT token signatures.
    OpenSSH is the same format used by Github, e.g.: https://api.github.com/users/davidcarboni/keys
    """
    return private.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH).decode("UTF8")


def generate_key():
    """Generate a key pair for this instance
    This will replace/rotate an existing key if one is present.
    TODO: confirm the curve to use. SECP256R1 generates keys as per ssh-keygen -t ecdsa ("ecdsa-sha2-nistp256")
    TODO: decide on an initial key-rotation strategy (default behaviour is "instance lifetime") and cleanup of old keys.
    """
    global _key

    private = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public = _public_key(private)
    _id = add_key(public)

    # NB using a dict to store both the key and ID avoids the (small) risk of a race condition
    # if these two values were stored in separate module-level variables.
    _key = {
        'id': _id,
        'private': private
    }


# Generate instance key
generate_key()
