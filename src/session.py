"""Provides handling for session fallback.
This is useful when a client does not have local storage, or is unable to make rest calls.
It's intended for a small percentage of javascript-disabled and/or older browsers.
"""
from .database import add_session, get_session


def create_session(token):

    """Creates a new session and returns the session ID.
    You can use the session ID to recover the given token.
    NB this looks a little bare for now, but there'll likely be more if we add session lifetime checks.
    :param token: A JWT to be stored on behalf of a client that cannot store it itself.
    :return: A session ID suitable for passing to the client as a cookie value.
    """
    return add_session(token)


def get_token(session_id):
    """ Retrieves the JWT associated with the given session ID (if any)
    NB this looks a little bare for now, but there'll likely be more if we add session lifetime checks.
    :param session_id: The ID of the session.
    :return: The associated JWT, or None
    """
    return get_session(session_id)
