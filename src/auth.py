import logging
import datetime
from flask import Flask, request, jsonify, make_response
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
    json = request.get_json()
    if json:
        # We've been sent a json message:
        log.debug("Json request. Woop. Modern age.")
        return _sign_in_json(json)
    else:
        return _sign_in_session(request)


def _sign_in_json(json):
    log.debug("Received json message containing these fields: " + repr(json.keys()))
    if json.get("user_id") and json.get("password"):
        if authenticate(json["user_id"], json["password"]):
            claims = {
                "user_id": json["user_id"],
                "roles": ["tom", "dick", "harry"]
            }
            token = sign(claims)
            return jsonify({'token': token})
        else:
            return error("Sign-in failed.", 403)
    else:
        return error("Please provide user_id and password values.", 400)


def _sign_in_session(request):
    log.debug("Form sign-in")
    return error("Not implemented.", 418)


def authenticate(user_id, password):
    # TODO: dummy for now - eventually we'll use LDAP.
    return True


def error(message, status_code):
    response = jsonify(message)
    response.status_code = status_code
    return response


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
