#!/bin/bash
SESSION_ID=`curl -d 'user_id=martin&password=zecrets' localhost:5000/sign-in`
echo Session ID: $SESSION_ID
curl -v localhost:5000/token/$SESSION_ID
