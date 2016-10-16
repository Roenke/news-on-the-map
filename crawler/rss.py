import feedparser
from newspaper import Article
from dateutil import parser


MAX_RSS_COUNT = 1024
last_published_date = {}


def load(url):
    count = 0

    entries = feedparser.parse(url).entries
    for entry in entries:
        href = entry.links[0].href
        date = parser.parse(entry.published)
        if url in last_published_date and last_published_date[url] > date:
            break

        article = Article(href, language="ru")
        article.download()
        article.parse()

        yield article.text, date, href

        count += 1
        if count == MAX_RSS_COUNT:
            break

    last_published_date[url] = parser.parse(entries[0].published)
