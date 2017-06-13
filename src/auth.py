import logging
import datetime
from flask import Flask
from .token import sign, decode

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
app = Flask("auth", static_folder='static')


@app.route('/')
def hello_world():
    now = str(datetime.datetime.now())
    log.debug(now)
    data = {'hello': 'world'}
    token = sign(data)
    log.debug("Token: " + str(token))
    decoded = decode(token)
    log.debug("Decoded: " + decoded)
    return 'Hello, World: ' + now
