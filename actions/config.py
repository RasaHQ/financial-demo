# -*- coding: utf-8 -*-
import os

rasa_x_host = os.environ.get("RASA_X_HOST", "localhost:5002")

rasa_x_password = os.environ.get("RASA_X_PASSWORD", "password")

rasa_x_username = os.environ.get("RASA_X_USERNAME", "me")

rasa_x_host_schema = os.environ.get("RASA_X_HOST_SCHEMA", "http")
