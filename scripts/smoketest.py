"""Performs Rasa Enterprise smoke tests

Rasa X HTTP API: https://rasa.com/docs/rasa-x/pages/http-api

Rasa   HTTP API: https://rasa.com/docs/rasa/pages/http-api
                 (Use BASE_URL/core/... to reach rasa-production server directly)
"""
from typing import Any
import os
import pprint

from requests import request

BASE_URL = os.environ.get("BASE_URL")
USERNAME = os.environ.get("RASAX_INITIALUSER_USERNAME")
PASSWORD = os.environ.get("RASAX_INITIALUSER_PASSWORD")
VERBOSE = int(os.environ.get("VERBOSE", 1))


def my_print(msg: Any, status_code: int = None) -> None:
    """Pretty print msg"""
    if VERBOSE > 0:
        if status_code:
            print(f"status_code: {status_code}")

        if isinstance(msg, (list, dict)):
            pprint.pprint(msg)
        else:
            print(msg)


quit = False
if not BASE_URL:
    my_print("Please set environment variable: BASE_URL")
    quit = True
if not USERNAME:
    my_print("Please set environment variable: RASAX_INITIALUSER_USERNAME")
    quit = True
if not PASSWORD:
    my_print("Please set environment variable: RASAX_INITIALUSER_PASSWORD")
    quit = True
if quit:
    exit(1)

###################################
my_print("--\nBASE_URL")
my_print(BASE_URL)

###################################
my_print("--\nRasa X Health check")

url = f"{BASE_URL}/api/health"
r = request("GET", url)
if r.status_code != 200:
    my_print(r.json(), r.status_code)
    exit(1)

status_rasa_production = r.json().get("production", {}).get("status")
status_rasa_worker = r.json().get("worker", {}).get("status")

my_print(r.json(), r.status_code)

if status_rasa_production != 200:
    my_print(f'rasa-production not OK!\nstatus = {status_rasa_production}')
    exit(1)

if status_rasa_worker != 200:
    my_print(f'rasa-worker not OK!\nstatus = {status_rasa_worker}')
    exit(1)


###################################
my_print("--\nGet access_token")

url = f"{BASE_URL}/api/auth"
payload = {"username": USERNAME, "password": PASSWORD}
headers = {"Content-Type": "application/json"}
r = request("POST", url, json=payload, headers=headers)
if r.status_code != 200:
    my_print(r.json(), r.status_code)
    exit(1)

access_token = r.json().get("access_token")

if not access_token:
    my_print("access_token is empty???")
    exit(1)

###################################
my_print("--\nCheck tagged production model")

url = f"{BASE_URL}/api/projects/default/models"
payload = {}
headers = {"Authorization": f"Bearer {access_token}"}
params = {'tag': 'production'}
r = request("GET", url, json=payload, headers=headers, params=params)
if r.status_code != 200:
    my_print(r.json(), r.status_code)
    exit(1)

production_model = r.json()[0].get("model")
my_print(f"Found production model: {production_model}")

###################################
my_print("--\nSay hi")

url = f"{BASE_URL}/api/chat"
payload = {"message": "hi"}
headers = {"Authorization": f"Bearer {access_token}"}
params = {}
r = request("POST", url, json=payload, headers=headers, params=params)
if r.status_code != 200 or r.json() == []:
    my_print(r.json(), r.status_code)
    if r.status_code == 200 and r.json() == []:
        print(
            "Bot responded, but the response is empty.\n"
            "Probably the model is not loaded yet by rasa-prod container.\n"
            "Confirm by running `make rasa-enterprise-smoketest locally`.\n"
            "If so, increase sleep time in pipeline after tagging of production model."
        )
    exit(1)

my_print(r.json(), r.status_code)

###################################
my_print("--\nSmoke tests passed")
exit(0)
