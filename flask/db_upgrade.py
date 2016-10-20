#!/usr/bin/python3

from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
import sys

def usage():
    print("Usage: ./db_downgrade.py up|down")

if(len(sys.argv) < 2):
    usage()
    sys.exit(1)

v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
if(sys.argv[1] == 'up'):
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v + 1)
elif(sys.argv[1] == 'down'):
    api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
else:
    usage()
    sys.exit(1)
print('Current database version: ' + str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))
