import os
import logging
import datetime
from jwt import get_unverified_header
from flask import Flask, request, redirect, jsonify, make_response, render_template
from json import dumps
from src.token import sign, decode
from src.key import generate_key
from src.session import create_session
from src.database import list_keys, get_key, get_token, delete_token


# Logging

debug = bool(os.getenv("FLASK_DEBUG"))
logging_level = logging.DEBUG if debug else logging.WARNING
logging.basicConfig(level=logging_level)
log = logging.getLogger(__name__)


# App

app = Flask("auth", static_folder='static', static_url_path='')


@app.route('/')
def default():
    log.info("Helper redirect to /sign-in")
    return redirect("sign-in")


@app.route('/sign-in', methods=['GET'])
def form():
    log.info(request.cookies)
    return render_template('index.html')


@app.route('/sign-in', methods=['POST'])
def sign_in():
    """
    User sign-in.
    This method expects fields 'username' and 'password', either in a Json message, or in a form.
    :return: If Json was submitted, a Json message with a 'token' field.
        If a form was submitted, a session_id cookie is set.
    """

    # Retrieve the submitted data
    form = False
    data = request.get_json()
    if data:
        log.debug("Json data received.")
    else:
        data = request.form
        if data:
            form = True
            log.debug("Form data received.")

    # Validate
    username = data.get("username", None)
    password = data.get("password", None)
    if not (username and password):
        log.debug("Request data not found.")
        print("username=" + str(username))
        print("password=" + str(password))
        print(data)
        return error("Please provide username and password values as either a Json message or a form post.", 400)

    # Authenticate
    log.debug("Authenticating user " + str(username))
    if authenticate(username, password):
        roles = authorise(username)
        claims = {
            "username": username,
            "roles": roles
        }
        jwt = sign(claims)

        # Response
        session_id = create_session(jwt)
        if form:
            if request.cookies.get('service'):
                response = redirect(service_url())
            else:
                response = make_response(session_id)
        else:
            response = jsonify({'token': jwt})

        response.set_cookie('jwt-session', session_id)
        return response
    else:
        return error("Sign-in failed.", 401)


@app.route('/sign-out')
def sign_out():
    """
    User sign-out.
    If a session identifier is passed in the cookie,
    the session will be removed from the database
    and the cookie value will be cleared.
    """

    session_id = request.cookies.get('jwt-session')
    if session_id:
        delete_token(session_id)

    response = redirect("/sign-in")
    response.set_cookie('jwt-session', '', expires=0)
    return response


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


@app.route('/test')
def test():
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


def authenticate(username, password):
    # TODO: dummy for now - eventually we'll use LDAP.
    return password != "wrong"


def authorise(username):
    # TODO: dummy for now - eventually we'll use LDAP.
    return [
        "dev_eforms_users",
        "dev_advance_notices_users",
        "dev_advance_notices_reviewers",
        "ESERVICES_WRAPPER_EDITOR",
        "TAXSERVER_SEARCH",
        "PFSI_ARTL_DISCHARGE_REQUESTER",
        "PFSI_ARTL_DISCHARGE_APPROVER",
        "PFSI_BT_SERVICE_ADMINISTRATOR",
        "PFSI_ROS_AGENCY_ADMINISTRATOR"
    ]


def service_url():
    service = request.cookies.get('service')
    if service == 'discharges':
        return os.getenv("DISCHARGES_URL", "/discharges")
    elif service == 'securities':
        return os.getenv("SECURITIES_URL", "/securities")


def error(message, status_code):
    response = jsonify(message)
    response.status_code = status_code
    return response


if __name__ == "__main__":
    log.info("FLASK_DEBUG is " + str(debug))
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=debug
    )
