from app import db


class Events(db.Model):

    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, index=True)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
