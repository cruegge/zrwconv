#!/bin/sh
exec gunicorn zrwconv.app:create_app \
    --worker-class aiohttp.GunicornWebWorker \
    --reload \
    --access-logfile - \
    "$@"
