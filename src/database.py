"""Simulates a database for key and session storage."""
import logging
import os
import uuid
import tempfile
import re
from pymongo import MongoClient

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

mongodb_uri = os.getenv('MONGODB_URI')
if mongodb_uri:
    client = MongoClient(mongodb_uri)
    log.debug(client)
    database = client.get_database()
    log.debug(database)
    keys = database.get_collection("keys")
    log.debug(keys)


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

    for found in keys.find():
        log.debug("Found: " + str(found))

    return os.listdir(_key_database)


def add_key(public_key):
    key_id = new_id()
    path = os.path.join(_key_database, key_id)

    with open(path, "w") as public_key_file:
        public_key_file.write(public_key)
    log.debug("Public key saved to " + path)
    log.debug("Saved public key: " + public_key)

    mongo_id = database.keys.insert_one({'key_id': key_id, 'public_key': public_key}).inserted_id
    log.debug("Inserted ID is " + str(mongo_id))

    return key_id


def get_key(key_id):

    found = keys.find_one({'key_id': key_id})
    log.debug("Found: " + str(found))

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
