import logging
import b3
import sleuth
import os

from flask import Flask, request, redirect, jsonify, render_template

from src.token import sign
from src.database import list_keys, get_key


# Config

debug = bool(os.getenv("FLASK_DEBUG")) or True
COOKIE_DOMAIN = os.getenv('COOKIE_DOMAIN', None)


# Logging

logging.getLogger().setLevel(logging.DEBUG if debug else logging.WARNING)
log = logging.getLogger(__name__)


# App

app = Flask("auth", static_folder='static', static_url_path='')
app.before_request(b3.start_span)
app.after_request(b3.end_span)


@app.route('/')
def default():
    log.info("Helper redirect to /sign-in")
    return redirect("sign-in")


@app.route('/sign-in', methods=['GET'])
def form():
    log.debug("Current JWT: " + str(request.cookies.get("jwt")))
    log.debug("Service to redirect to after login: " + str(request.cookies.get("service")))
    log.debug("Cookie domain is: " + str(COOKIE_DOMAIN))
    return render_template('index.html',
                           sign_in_url=service_url('sign-in'),
                           sign_out_url=service_url('sign-out'),
                           discharges_url=service_url('discharges'),
                           securities_url=service_url('securities'),
                           dispositions_url=service_url('dispositions'),
                           cookie_domain=COOKIE_DOMAIN)


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
        log.debug("Json data received (API call?).")
    else:
        data = request.form
        if data:
            form = True
            log.debug("Form data received (Login form submitted?).")

    # Validate
    username = data.get("username", None)
    password = data.get("password", None)
    if not (username and password):
        log.debug("Request data not found.")
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
        log.debug("JWT is: {jwt}".format(jwt=jwt))

        # Response
        if form and request.cookies.get('service'):
            service = request.cookies.get('service')
            url = service_url(service)
            response = redirect(url)
        else:
            response = jsonify({'jwt': jwt})
        response.set_cookie('jwt', jwt, domain=".ros.9ov.uk")
        return response
    else:
        return error("Sign-in failed.", 401)


@app.route('/sign-out')
def sign_out():
    """
    User sign-out.
    It's the client's responsibility to dispose of a JWT if it's being stored anywhere other than via the cookie.
    This will clear the cookie and redirect to sign-in.
    """
    response = redirect(service_url('sign-in'))
    response.set_cookie('jwt', '', expires=0)
    return response


@app.route('/keys')
def keys():
    """Returns the public key of this and any other instances.
    The fields in the returned Json match what Github does for public keys.
    e.g. see https://api.github.com/users/davidcarboni/keys
    """
    log.debug("Public keys requested.")
    result = []
    for _id in list_keys():
        result.append({'id': _id, 'key': get_key(_id)})
    return jsonify(result)


def authenticate(username, password):
    # TODO: dummy for now - eventually we'll use LDAP.
    return username and password != "wrong"


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


def service_url(service):
    if service == 'sign-in':
        return os.getenv('SIGN_IN_URL', "/sign-in")
    elif service == 'sign-out':
        return os.getenv('SIGN_OUT_URL', "/sign-out")
    elif service == 'discharges':
        return os.getenv('DISCHARGES_URL', "/discharges")
    elif service == 'securities':
        return os.getenv('SECURITIES_URL', "/securities")
    elif service == 'dispositions':
        return os.getenv('DISPOSITIONS_URL', "/dispositions")
    else:
        return "/"


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
