import os
import logging
import datetime
from jwt import get_unverified_header
from flask import Flask, request, jsonify, make_response
from json import dumps
from src.token import sign, decode
from src.key import generate_key
from src.session import create_session
from src.database import list_keys, get_key, get_token


# Logging

debug = bool(os.getenv("FLASK_DEBUG"))
logging_level = logging.DEBUG if debug else logging.WARNING
logging.basicConfig(level=logging_level)
log = logging.getLogger(__name__)


# App

app = Flask("auth", static_folder='static')


@app.route('/sign-in', methods=['POST'])
def sign_in():
    """
    User sign-in.
    This method expects fields 'user_id' and 'password', either in a Json message, or in a form.
    :return: If Json was submitted, a Json message with a 'token' field.
        If a form was submitted, a session_id cookie is set.
    """
    # Retrieve the submitted data
    form = False
    data = request.get_json()
    if not data:
        data = request.form
        form = True
        log.debug("Form data received.")
    else:
        log.debug("Json data received.")
    if not data:
        log.debug("Request data not found.")
        return error("Please provide user_id and password values as either a Json message or a form post.", 400)

    user_id = data.get("user_id", None)
    password = data.get("password", None)

    # Validate
    if user_id and password:
        # Authenticate
        log.debug("Authenticating user " + user_id)
        if authenticate(user_id, password):
            roles = authorise(user_id)
            claims = {
                "user_id": user_id,
                "roles": roles
            }
            jwt = sign(claims)
            # Response
            if form:
                session_id = create_session(jwt)
                response = make_response(session_id)
                response.set_cookie('session_id', session_id)
            else:
                response = jsonify({'token': jwt})
            return response
        else:
            return error("Sign-in failed.", 401)
    else:
        return error("Please provide user_id and password values.", 400)


@app.route('/token/<session_id>')
def token(session_id):
    """
    Gets the token associated with the given session ID.
    :param session_id: The session for which to retrieve the JWT.
    :return: A Json message with a 'token' field.
    """
    jwt = get_token(session_id)
    if jwt:
        log.debug("Read token for session ID " + session_id)
        return jsonify({'token': jwt})
    else:
        log.debug("No token found for session ID " + session_id)
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
    """
    Runs through the process of creating and validating a JWT,
    including key rotation to simulate a different instance verifying the token.
    :return: Some Json displaying the results of the test.
    """
    data = {
        'hello': 'world',
        'now': str(datetime.datetime.now())
    }
    log.debug("Data: " + dumps(data))
    jwt = sign(data)
    log.debug("Token: " + jwt)
    log.debug("Generating new key to simulate being a different instance..")
    generate_key()
    log.debug("Now decoding token..")
    decoded = decode(jwt)
    log.debug("Decoded: " + dumps(decoded))
    return jsonify({
        'data': data,
        'jwt': jwt,
        'jwt header': get_unverified_header(jwt),
        'jwt claims': decoded
    })


def authenticate(user_id, password):
    # TODO: dummy for now - eventually we'll use LDAP.
    return password != "wrong"


def authorise(user_id):
    # TODO: dummy for now - eventually we'll use LDAP.
    return ["tom", "dick", "harry"]


def error(message, status_code):
    response = jsonify(message)
    response.status_code = status_code
    return response


if __name__ == "__main__":
    log.info("FLASK_DEBUG is " + str(debug))
    app.run(
        host="0.0.0.0",
        port=os.getenv("PORT", "5000"),
        debug=debug
    )
