from flask import render_template
from flask_googlemaps import Map
from app import app
from .forms import SearchForm
import urllib.request
import json


def search_events(string):
    url = app.config['ELASTIC_URL']
    content_maxlen = 150
    query_size = 10000
    string = string if string else "*"
    query = {
        "query": {
            "wildcard": {"content": string.lower()}
        },
        "size": query_size
    }
    req = urllib.request.Request(url, json.dumps(query).encode('utf8'))
    resp = urllib.request.urlopen(req, json.dumps(query).encode())
    markers = [{
        'lat': e['_source']['location']['lat'],
        'lng': e['_source']['location']['lon'],
        'infobox': '<h3>{0}</h3><b>Подробнее: </b><a target="_blank" href="{1}">{1}</a><br><b>Источник: </b><a target="_blank" href="{2}">{2}</a>'.format(
            e['_source']['content'][:content_maxlen] + ("" if len(e['_source']['content']) <= content_maxlen else "..."),
            e['_source']['links']['article_url'],
            e['_source']['links']['source_url'])
    } for e in json.loads(resp.read().decode())['hits']['hits']]
    markers.sort(key=lambda m: m['lat'])
    res = []
    for m in markers:
        if len(res) and res[-1]['lat'] == m['lat'] and res[-1]['lng'] == m['lng']:
            res[-1]['infobox'] += "<hr>" + m['infobox']
        else:
            res.append(m)
    return res


@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
def mapview():
    # creating a map in the view
    form = SearchForm()
    markers = []
    if form.validate_on_submit():
        markers = search_events(form.search.data)
    """markers = [{
        'lat': e.lat,
        'lng': e.lng,
        'infobox': "<h3>{}</h3><hr>{}".format(e.title, e.description)
    } for e in models.Events.query.all()]"""
    mymap = Map(
        identifier="mymap",
        style=(
            "height:85%;"
            "width:100%;"
            "top:15%;"
            "left:0;"
            "position:absolute;"
        ),
        cluster=True,
        lat=60.0092659,
        lng=30.353306,
        zoom=10,
        markers=markers
    )
    return render_template('index.html', mymap=mymap, form=form)
