from app import app, google
from urllib.request import Request, urlopen, URLError

import json
from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, DateField, validators
from flask.ext.admin.form.widgets import DatePickerWidget

from flask import render_template, session, request, url_for, redirect
from flask_googlemaps import Map
from flask.ext.wtf import Form
from flask.ext.admin.form.widgets import DatePickerWidget
from wtforms import TextField, SubmitField, DateField, validators

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
    req = Request(url, json.dumps(query).encode('utf8'))
    resp = urlopen(req, json.dumps(query).encode())
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


@app.route("/login")
def login():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route("/authorized")
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')


@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
def index():
    startlat = 60.0092659
    startlng = 30.353306
    user = None
    access_token = session.get('access_token')
    if access_token is not None:
        access_token = access_token[0]
        headers = {'Authorization': 'OAuth ' + access_token}
        req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                      None, headers)
        try:
            res = urlopen(req)
        except URLError as e:
            if e.code == 401:
                # Unauthorized - bad token
                session.pop('access_token', None)
                return redirect(url_for('login'))
        user = json.loads(res.read().decode())['name']

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
        if 'rectCheckbox' in request.form and request.form['rectCheckbox'] == "on":
            r = session['searchRect'] = json.loads(request.form['searchRect'])
            query_data['bounds']['tl']['lat'] = r['north']
            query_data['bounds']['tl']['lng'] = r['west']
            query_data['bounds']['rb']['lat'] = r['south']
            query_data['bounds']['rb']['lng'] = r['east']
        if form.date_from.data and form.date_to.data:
            query_data['from'] = form.date_from.data
            query_data['to'] = form.date_to.data
        if form.data.data:
            query_data['query'] = form.data.data
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
    return render_template('index.html', mymap=mymap, form=form, searchRect=session['searchRect'], user=user)
