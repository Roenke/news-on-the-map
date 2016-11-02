from flask.ext.wtf import Form
from wtforms import TextField


class SearchForm(Form):
    search = TextField('search')
