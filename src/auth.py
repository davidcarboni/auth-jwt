import logging
import datetime
from flask import Flask, jsonify
from json import dumps
from .token import sign, decode
from src import key

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
app = Flask("auth", static_folder='static')


@app.route('/')
def home():
    data = {
        'hello': 'world',
        'now': str(datetime.datetime.now())
    }
    log.debug("Data: " + dumps(data))
    jwt = sign(data)
    log.debug("Token: " + jwt.decode('UTF8'))
    decoded = decode(jwt)
    log.debug("Decoded: " + dumps(decoded))
    return jsonify({
        'data': data,
        'jwt': jwt,
        'decoded': decoded
    })


@app.route('/public-key')
def public_key():
    """Returns the public key of this instance.
    The fields in the returned Json match what Github does for public keys.
    e.g. see https://api.github.com/users/davidcarboni/keys
    """
    log.debug("Public key requested.")
    return jsonify({'id': key.key_id(), 'key': key.public_key().decode("UTF8")})
