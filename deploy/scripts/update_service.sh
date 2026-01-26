#!/bin/bash
set -e

SERVICE_NAME="xml-import"
SERVICE_DIR="/opt/xml_data_importer"

systemctl stop $SERVICE_NAME

cp -r $SERVICE_DIR $SERVICE_DIR.backup.$(date +%Y%m%d_%H%M%S)

cd $SERVICE_DIR

git stash
git pull origin master
git stash pop

source .venv/bin/activate
uv sync
deactivate

systemctl start $SERVICE_NAME
