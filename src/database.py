"""Simulates a database for key and session storage."""
import logging
import os
import uuid
import tempfile
import re

log = logging.getLogger(__name__)

# Set up temporary folders

_database = os.getenv("DATABASE_PATH", tempfile.TemporaryDirectory().name)

_key_database = os.path.join(_database, "keys")
log.debug("creating key database: " + _key_database)
os.makedirs(_key_database)

_session_database = os.path.join(_database, "sessions")
log.debug("creating session database: " + _session_database)
os.makedirs(_session_database)


# Keys


def list_keys():
    log.debug("Listing public keys in " + _key_database)
    return os.listdir(_key_database)


def add_key(public_key):
    key_id = new_id()
    path = os.path.join(_key_database, key_id)

    with open(path, "w") as public_key_file:
        public_key_file.write(public_key)
    log.debug("Public key saved to " + path)
    log.debug("Saved public key: " + public_key)
    return key_id


def get_key(key_id):
    path = os.path.join(_key_database, key_id)
    if os.path.isfile(path):
        with open(path, "r") as public_key_file:
            log.debug("Reading public key from " + path)
            key = public_key_file.read()
            log.debug("Read public key:  " + key)
            return key


# Sessions


def save_token(jwt):
    # TODO: this should probably set a last-accessed timestamp to give the session a lifetime.
    token_id = new_id()
    path = os.path.join(_session_database, token_id)
    with open(path, "w") as jwt_file:
        jwt_file.write(jwt)
    log.debug("Session saved to " + path)
    return token_id


def get_token(token_id):
    # TODO: this should probably update a last-accessed timestamp to keep the session alive.
    # Disallow . .. \ / and whitespace
    if re.fullmatch('[^\s\.\\/]+', token_id):
        path = os.path.join(_session_database, token_id)
        if os.path.isfile(path):
            with open(path, "r") as jwt_file:
                log.debug("Reading JWT from " + path)
                return jwt_file.read()


def delete_token(token_id):
    # Disallow . .. \ / and whitespace
    if re.fullmatch('[^\s\.\\/]+', token_id):
        path = os.path.join(_session_database, token_id)
        if os.path.isfile(path):
            os.remove(path)


def new_id():
    """Generate a secure random ID:

    https://stackoverflow.com/questions/817882/unique-session-id-in-python/6092448#6092448

    The implementation of uuid.uuid4 uses os.urandom(16) (at the time of writing) so should be good enough.

    See also: https://www.2uo.de/myths-about-urandom/

    """
    return str(uuid.uuid4())
