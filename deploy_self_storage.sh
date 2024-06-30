#!/bin/bash
set -e
git pull
/opt/SelfStorage/.venv/bin/pip install -r requirements.txt
/opt/SelfStorage/.venv/bin/python /opt/SelfStorage/selfstorage/manage.py migrate
systemctl restart redis.service
systemctl disable self-storage-celery.service
systemctl stop self-storage-celery.service
systemctl disable self-storage.service
systemctl restart self-storage.service
systemctl enable self-storage.service
systemctl start self-storage-celery.service
systemctl enable self-storage-celery.service