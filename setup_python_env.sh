#!/bin/bash

sudo apt-get install python3-venv
python3 -m venv ./.venv
source ./.venv/bin/activate

# need at least pip 19.0 to install poetry project
# see: https://github.com/python-poetry/poetry/issues/321#issuecomment-458205972
python -m pip install -U pip

pip install -r requirements.txt

python -m spacy download en_core_web_md
python -m spacy link en_core_web_md en