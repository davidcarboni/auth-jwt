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
    return os.listdir(_key_database)


def add_key(public_key):
    _id = str(uuid.uuid4())
    path = os.path.join(_key_database, _id)

    with open(path, "w") as public_key_file:
        public_key_file.write(public_key)
    log.debug("Public key saved to " + path)
    return _id


def get_key(_id):
    path = os.path.join(_key_database, _id)
    if os.path.isfile(path):
        with open(path, "r") as public_key_file:
            return public_key_file.read()


# Sessions


def save_token(jwt):
    # TODO: this should probably set a last-accessed timestamp to give the session a lifetime.
    _id = str(uuid.uuid4())
    path = os.path.join(_session_database, _id)
    with open(path, "w") as jwt_file:
        jwt_file.write(jwt)
    log.debug("Session saved to " + path)
    return _id


def get_token(_id):
    # TODO: this should probably update a last-accessed timestamp to keep the session alive.
    # Disallow . .. \ / and whitespace
    if re.fullmatch('[^\s\.\\/]+', _id):
        path = os.path.join(_session_database, _id)
        if os.path.isfile(path):
            with open(path, "r") as jwt_file:
                return jwt_file.read()
