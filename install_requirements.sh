#!/bin/bash

python -m venv ./.venv
source .venv/Scripts/activate
pip install -r requirements.txt

read -p "Instalation of dependences ended, press enter to exit..."