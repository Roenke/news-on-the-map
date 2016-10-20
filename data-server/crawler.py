import argparse
import cPickle as pickle
import json
import os
import time
from datetime import datetime

from crawler import rss_feed
from crawler import vk_feed
from common.article import RawArticle
from common.db import Database

MAX_FEED_COUNT = 1024
LOADED_DATES_FILE = ".loaded.pickle"

last_loaded_date = {}
if os.path.exists(LOADED_DATES_FILE):
    with open(LOADED_DATES_FILE, "rb") as f:
        last_loaded_date = pickle.load(f)


def create_parser():
    parser = argparse.ArgumentParser('')
    parser.add_argument("--config", required=True, type=str,
                        help="path to crawler_old config file")

    parser.add_argument("--db", required=True, type=str,
                        help="path to database config file")

    return parser


loaders = {
    "rss": rss_feed.load,
    "vk": vk_feed.load
}


def load(db, link):
    typ = link["type"]
    link_url = link["url"]
    from_date = datetime.strptime(link['from_date'], u'%d.%m.%Y')
    loaded_count = 0

    max_date = max(from_date, last_loaded_date[link_url]) if link_url in last_loaded_date else from_date
    for (text, date, url) in loaders[typ](link_url):
        if link_url in last_loaded_date and last_loaded_date[link_url] >= date:
            break

        max_date = max(max_date, date)
        db.insert_raw(RawArticle(text, date, link_url, url))
        loaded_count += 1
        if loaded_count == MAX_FEED_COUNT:
            break

    last_loaded_date[link_url] = max_date
    print "loaded {} feeds for {}".format(loaded_count, link_url)


def main():
    args = create_parser().parse_args()

    if not os.path.exists(args.config):
        raise Exception("config doesn't exists")

    if not os.path.exists(args.db):
        raise Exception("database config doesn't exists")

    with open(args.db, 'r') as db_file:
        db = json.load(db_file)

    with open(args.config, "r") as config_file:
        config = json.load(config_file)

    db = Database(db)
    while True:
        with open(LOADED_DATES_FILE, "wb") as last_article_time:
            pickle.dump(last_loaded_date, last_article_time)

        for link in config["links"]:
            load(db, link)

        time.sleep(config["period"])


if __name__ == "__main__":
    main()
