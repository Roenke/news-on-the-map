from app import app, google, models, db
from urllib.request import Request, urlopen, URLError
from datetime import datetime

import json
from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, DateField, validators
from flask.ext.admin.form.widgets import DatePickerWidget

from flask import render_template, session, request, url_for, redirect, jsonify
from flask_googlemaps import Map
from flask.ext.wtf import Form
from flask.ext.admin.form.widgets import DatePickerWidget

class SearchForm(Form):
    data = TextField('search')
    search = SubmitField(label='search')
    date_from = TextField('From')
    date_to = TextField('To')

def search_events(query_data, user):

    likes = models.Likes.query.filter(models.Likes.user_email == user)

    categories = dict()
    for like in likes:
        categories[like.category_id] = 1 + categories.get(like.category_id, 0)

    fav_category = -1

    for cat in categories:
        if categories.get(fav_category, 0) < categories[cat]:
            fav_category = cat

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
        'infobox': '<h3>{5}{0}</h3><button onClick="like({3}, {4})">Мне нравится!</button><br><b>Подробнее: </b><a target="_blank" href="{1}">{1}</a><br><b>Источник: </b><a target="_blank" href="{2}">{2}</a><br>Keywords: {6}'.format(
            e['_source']['content'][:content_maxlen] + ("" if len(e['_source']['content']) <= content_maxlen else "..."),
            e['_source']['links']['article_url'],
            e['_source']['links']['source_url'],
            e['_source']['id'],
            e['_source']['category'],
            '<font color="red">*</font>' if fav_category == e['_source']['category'] else '',
            e['_source']['location_words'])
    } for e in json.loads(resp.read().decode())['hits']['hits']]
    markers.sort(key=lambda m: m['lat'])
    res = []
    for m in markers:
        if len(res) and res[-1]['lat'] == m['lat'] and res[-1]['lng'] == m['lng']:
            res[-1]['infobox'] += "<hr>" + m['infobox']
        else:
            res.append(m)
    return res


@app.route("/like")
def like():
    id = request.args.get('id', 0, type=int)
    category = request.args.get('category', 0, type=int)
    user = request.args.get('user', '', type=str)

    if(user == ''): return

    like = models.Likes(user_email=user, news_id = id, category_id = category)
    db.session.add(like)
    db.session.commit()
    return jsonify(dummy=0)

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
        user = json.loads(res.read().decode())

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
            epoch = datetime(1970,1,1)
            query_data['from'] = int((datetime.strptime(form.date_from.data,'%d.%m.%Y') - epoch).total_seconds())
            query_data['to'] = int((datetime.strptime(form.date_to.data,'%d.%m.%Y') - epoch).total_seconds())
        if form.data.data:
            query_data['query'] = form.data.data
        markers = search_events(query_data, user['email'] if user is not None else '')

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
    return render_template('index.html', mymap=mymap, form=form, searchRect=session['searchRect'], authorized=(user is not None), user_email = None if user is None else user['email'], user_name = None if user is None else user['name'])
