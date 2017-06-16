import logging
import datetime
import re
from flask import Flask, request, jsonify, make_response
from json import dumps
from .token import sign, decode
from .key import generate_key
from .session import create_session
from .database import list_keys, get_key, get_token
import jwt

log = logging.getLogger(__name__)
app = Flask("auth", static_folder='static')


@app.route('/sign-in', methods=['POST'])
def sign_in():
    # Retrieve the submitted data
    form = False
    data = request.get_json()
    if not data:
        data = request.form
        form = True
    if not data:
        return error("Please provide user_id and password values as either a Json message or a form post.", 400)

    user_id = data.get("user_id", None)
    password = data.get("password", None)

    # Validate
    if user_id and password:
        # Authenticate
        if authenticate(user_id, password):
            roles = authorise()
            claims = {
                "user_id": user_id,
                "roles": roles
            }
            jwt = sign(claims)
            return create_session(jwt) if form else jsonify({'token': jwt})
        else:
            return error("Sign-in failed.", 401)
    else:
        return error("Please provide user_id and password values.", 400)


@app.route('/token/<session_id>')
def token(session_id):
    jwt = get_token(session_id)
    if jwt:
        return jsonify({'token': jwt})
    else:
        return error("No JWT available for session id " + session_id, 404)


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


def authenticate(user_id, password):
    # TODO: dummy for now - eventually we'll use LDAP.
    return password != "wrong"


def authorise():
    # TODO: dummy for now - eventually we'll use LDAP.
    return ["tom", "dick", "harry"]


def error(message, status_code):
    response = jsonify(message)
    response.status_code = status_code
    return response
