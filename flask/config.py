import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
CSRF_ENABLED = True
SECRET_KEY = 'omelchenko-key'
GOOGLEMAPS_KEY = 'AIzaSyAvUvSdZnWBFxCAXGUuWdPyNlXxpr4y1e8'

ELASTIC_URL = 'http://192.168.1.41:9200/_search'
