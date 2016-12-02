from flask import render_template, session, request
from flask_googlemaps import Map
from app import app
import urllib.request
import json
from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, DateField, validators
from flask.ext.admin.form.widgets import DatePickerWidget

class SearchForm(Form):
    data = TextField('search')
    search = SubmitField(label='search')
    date_from = TextField('From')
    date_to = TextField('To')

def search_events(query_data):
    print("here8")
    url = app.config['ELASTIC_URL']
    content_maxlen = 150
    query_size = 10000
    query = { "query": { "bool": {
            "must": [{
                "wildcard": {"content": query_data['query'].lower()}
            }, {
                "range": {"publish_date": {
                    "gte": query_data['from'],
                    "lt": query_data['to']
                    }}
            }]}},
            "filter": {"geo_bounding_box": { "location": {
                "top_left": {
                    "lat": query_data['bounds']['tl']['lat'],
                    "lon": query_data['bounds']['tl']['lng']
                },
                "bottom_right": {
                    "lat": query_data['bounds']['rb']['lat'],
                    "lon": query_data['bounds']['rb']['lng']
                }
            }}},
        "size": query_size
    }
    print("Query is: ", query)
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


startlat = 60.0092659
startlng = 30.353306

@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
def mapview():
    if 'searchRect' not in session:
        session['searchRect'] = {
            'north': startlat + 0.1,
            'south': startlat - 0.1,
            'east' : startlng + 0.1,
            'west' : startlng - 0.1
        }
    form = SearchForm()
    markers = []
    query_data = {
        "query": "*",
        "from": "now-1000d/d",
        "to": "now/d",
        "bounds": {
            "tl": {
                "lat": startlat + 0.5,
                "lng": startlng - 0.5
            },
            "rb": {
                "lat": startlat - 0.5,
                "lng": startlng + 0.5
            }
        }
    }
    if form.validate_on_submit():
        print("here1")
        if 'rectCheckbox' in request.form and request.form['rectCheckbox'] == "on":
            print("here2")
            r = session['searchRect'] = json.loads(request.form['searchRect'])
            query_data['bounds']['tl']['lat'] = r['north']
            query_data['bounds']['tl']['lng'] = r['west']
            query_data['bounds']['rb']['lat'] = r['south']
            query_data['bounds']['rb']['lng'] = r['east']
        print("here3")
        if form.date_from.data and form.date_to.data:
            print("here4")
            query_data['from'] = form.date_from.data
            query_data['to'] = form.date_to.data
        print("here5")
        if form.data.data:
            print("here6")
            query_data['query'] = form.data.data
        print("here7")
        markers = search_events(query_data)

    mymap = Map(
        identifier="mymap",
        style=(
            "height:85%;"
            "width:100%;"
            "top:15%;"
            "left:0;"
            "position:absolute;"
        ),
        lat=startlat,
        lng=startlng,
        cluster=True,
        zoom=10,
        markers=markers,
    )
    return render_template('index.html', mymap=mymap, form=form, searchRect=session['searchRect'])
