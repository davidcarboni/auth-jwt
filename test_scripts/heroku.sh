#!/bin/bash
echo --- Listing keys:
curl rosauth.herokuapp.com/keys
echo --- Generating a new key:
curl rosauth.herokuapp.com/
echo --- Listing keys again:
curl rosauth.herokuapp.com/keys
echo --- Logging in with Json:
curl -X POST -H "content-type: application/json" -d '{"user_id": "martin", "password": "zecrets"}' rosauth.herokuapp.com/sign-in
echo --- Logging in with form:
SESSION_ID=`curl -d 'user_id=martin&password=zecrets' rosauth.herokuapp.com/sign-in`
echo Session ID: $SESSION_ID
curl rosauth.herokuapp.com/token/$SESSION_ID
