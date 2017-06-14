import logging
import datetime
from flask import Flask, jsonify
from json import dumps
from .token import sign, decode
from .key import generate_key
from .database import list_keys, get_key
import jwt

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
app = Flask("auth", static_folder='static')


@app.route('/sign-in', methods=['POST'])
def sign_in():
    token = sign({'user': 'david', 'role': 'dude'})
    return jsonify(token)


@app.route('/keys')
def keys():
    """Returns the public key of this instance.
    The fields in the returned Json match what Github does for public keys.
    e.g. see https://api.github.com/users/davidcarboni/keys
    """
    log.debug("Public keys requested.")
    result = []
    for _id in list_keys():
        result.append({'id': _id, 'key': get_key(_id)})
    return jsonify(result)


@app.route('/')
def home():
    data = {
        'hello': 'world',
        'now': str(datetime.datetime.now())
    }
    log.debug("Data: " + dumps(data))
    token = sign(data)
    log.debug("Token: " + token)
    log.debug("Generating new key to simulate being a different instance..")
    generate_key()
    log.debug("Now decoding token..")
    decoded = decode(token)
    log.debug("Decoded: " + dumps(decoded))
    return jsonify({
        'data': data,
        'jwt': token,
        'jwt header': jwt.get_unverified_header(token),
        'jwt claims': decoded
    })
