#!/bin/bash
curl -v -X POST -H "content-type: application/json" -d '{"user_id": "martin", "password": "zecrets"}' localhost:5000/sign-in

