#!/usr/bin/env bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

export FLASK_APP=app/main.py
export FLASK_ENV=development

flask run
