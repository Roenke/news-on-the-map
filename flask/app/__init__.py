from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps
from flask_bootstrap import Bootstrap


app = Flask(__name__, template_folder='templates')
app.config.from_object('config')
db = SQLAlchemy(app)

GoogleMaps(app)
Bootstrap(app)

from app import views, models
