import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
CSRF_ENABLED = True
SECRET_KEY = 'omelchenko-key'
GOOGLEMAPS_KEY = 'AIzaSyDOTA4wHDbiTwaT9T7zo5GCp6w5FbQEXH8'

GOOGLE_CLIENT_ID = '414897681927-4iue7gd05k32oneiicif8pq0n2ofjt7e.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'PiaaUbw4RWuhaIgLevTukwOn'


ELASTIC_URL = 'http://192.168.1.41:9200/_search'
