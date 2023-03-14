#!/bin/sh
exec gunicorn --reload "$@"
