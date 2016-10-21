from flask import render_template
from flask_googlemaps import Map
from app import app, models


@app.route("/")
@app.route("/index")
def mapview():
    # creating a map in the view
    markers = [{
        'lat': e.lat,
        'lng': e.lng,
        'infobox': "<h3>{}</h3><hr>{}".format(e.title, e.description)
    } for e in models.Events.query.all()]
    mymap = Map(
        identifier="mymap",
        style=(
            "height:90%;"
            "width:100%;"
            "top:10%;"
            "left:0;"
            "position:absolute;"
        ),
        cluster=True,
        lat=60.0092659,
        lng=30.353306,
        zoom=10,
        markers=markers
    )
    return render_template('index.html', mymap=mymap)
