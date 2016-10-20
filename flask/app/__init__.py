from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps


app = Flask(__name__, template_folder='templates')
app.config.from_object('config')
db = SQLAlchemy(app)

GoogleMaps(app)

from app import views, models
