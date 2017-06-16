#!/bin/bash
echo --- Listing keys:
curl localhost:5000/keys
echo --- Generating a new key:
curl localhost:5000/
echo --- Listing keys again:
curl localhost:5000/keys
echo --- Logging in with Json:
curl -X POST -H "content-type: application/json" -d '{"user_id": "martin", "password": "zecrets"}' localhost:5000/sign-in
echo --- Logging in with form:
SESSION_ID=`curl -d 'user_id=martin&password=zecrets' localhost:5000/sign-in`
echo Session ID: $SESSION_ID
curl localhost:5000/token/$SESSION_ID
