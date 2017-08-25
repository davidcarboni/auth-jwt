"""Simulates a database for key and session storage."""
import logging
import os
import uuid
import tempfile
from pymongo import MongoClient


# Logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# Database

mongodb_uri = os.getenv('MONGODB_URI')
collection = None
if mongodb_uri:
    # Use Mongo
    client = MongoClient(mongodb_uri)
    database = client.get_database()
    collection = database.get_collection("keys")
else:
    # Fall back to filesystem
    _database = tempfile.TemporaryDirectory().name
    _key_database = os.path.join(_database, "keys")
    log.debug("creating key database: " + _key_database)
    os.makedirs(_key_database)


# Keys

def list_keys():
    log.debug("Listing public keys")

    if collection:
        result = []
        for found in collection.find():
            result.append(found['key_id'])
        log.debug("Found keys: " + str(result))
        return result
    else:
        return os.listdir(_key_database)


def add_key(public_key):
    key_id = new_id()

    if collection:
        mongo_id = collection.insert_one({'key_id': key_id, 'public_key': public_key}).inserted_id
        log.debug("Inserted ID is " + str(mongo_id))
    else:
        path = os.path.join(_key_database, key_id)

        with open(path, "w") as public_key_file:
            public_key_file.write(public_key)
        log.debug("Public key saved to " + path)

    log.debug("Saved public key: " + key_id + " (" + public_key + ")")
    return key_id


def get_key(key_id):

    if collection:
        found = collection.find_one({'key_id': key_id})
        log.debug("Found: " + str(found))
        if found:
            return found['public_key']
    else:
        path = os.path.join(_key_database, key_id)
        if os.path.isfile(path):
            with open(path, "r") as public_key_file:
                log.debug("Reading public key from " + path)
                key = public_key_file.read()
                log.debug("Read public key:  " + key)
                return key


def new_id():
    """Generate a secure random ID:

    https://stackoverflow.com/questions/817882/unique-session-id-in-python/6092448#6092448

    The implementation of uuid.uuid4 uses os.urandom(16) (at the time of writing) so should be good enough.

    See also: https://www.2uo.de/myths-about-urandom/

    """
    return str(uuid.uuid4())
