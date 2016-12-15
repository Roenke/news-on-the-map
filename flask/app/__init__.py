from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps
from flask_bootstrap import Bootstrap
from flask_oauth import OAuth


app = Flask(__name__, template_folder='templates')
app.config.from_object('config')
db = SQLAlchemy(app)

GoogleMaps(app)
Bootstrap(app)

oauth = OAuth()
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=app.config['GOOGLE_CLIENT_ID'],
                          consumer_secret=app.config['GOOGLE_CLIENT_SECRET'])


from app import views, models
