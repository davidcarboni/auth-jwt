from jose import jwt
from jose.constants import ALGORITHMS
from src.key import private_key, public_key, _key_pair

print("Private : " + str(private_key()))
print("Public  : " + str(public_key()))


def sign(data):
    #jwt.encode(data, private_key(), algorithm=ALGORITHMS.RS256)
    return jwt.encode(data, _key_pair, algorithm=ALGORITHMS.RS256)


def decode(token):
    return jwt.decode(token, bytearray(public_key()))
    #return jwt.decode(token, _key_pair.publickey())
