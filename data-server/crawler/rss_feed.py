import feedparser
from newspaper import Article
from dateutil import parser
import calendar
from datetime import datetime, timedelta


def convert_date(date):
    utc_dt = parser.parse(date)
    # get integer timestamp to avoid precision lost
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)


def load(url):
    entries = feedparser.parse(url).entries
    for entry in entries:
        href = entry.links[0].href
        date = convert_date(entry.published)

        article = Article(href, language="ru")
        article.download()
        article.parse()

        yield article.text, date, href
