#!/bin/bash
set -e

## if currently running then docker-compose down
docker-compose down --remove-orphans

## Delete pgdata directory if it exists
if [ -d "pgdata" ]; then rm -rf pgdata; fi

pip3 install -r requirements.txt

## start and wait
docker-compose up -d --wait

./load_data.py