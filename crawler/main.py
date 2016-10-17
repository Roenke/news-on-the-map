import argparse
import json
import os
import time
from datetime import datetime
import cPickle as pickle
import psycopg2

import rss_feed
import vk_feed


MAX_FEED_COUNT = 1024
LOADED_DATES_FILE = ".loaded.pickle"

last_loaded_date = {}
if os.path.exists(LOADED_DATES_FILE):
    with open(LOADED_DATES_FILE, "rb") as f:
        last_loaded_date = pickle.load(f)


def create_parser():
    parser = argparse.ArgumentParser('')
    parser.add_argument("--config", required=True, type=str,
                        help="path to crawler config file")
    return parser


# db = psycopg2.connect(database='raw_news', user='crawler')
# inserter = db.cursor()
# def put_into_db(text, date, source_url, article_url):
    # inserter.execute("INSERT INTO news (text, publish_date, source_url, article_url) VALUES (%s, %s, %s, %s)",
    #                  (text, date, source_url, article_url))


def put_into_db(text, date, site_url, article_url):
    print site_url, ":", article_url, ":", date


loaders = {
    "rss": rss_feed.load,
    "vk":  vk_feed.load
}


def load(link):
    typ = link["type"]
    link_url = link["url"]
    count = 0

    max_date = last_loaded_date[link_url] if link_url in last_loaded_date else datetime.fromtimestamp(0)
    for (text, date, url) in loaders[typ](link_url):
        if link_url in last_loaded_date and last_loaded_date[link_url] >= date:
            break

        max_date = max(max_date, date)
        put_into_db(text, date, link_url, url)
        count += 1
        if count == MAX_FEED_COUNT:
            break

    last_loaded_date[link_url] = max_date
    print "loaded {} feeds for {}".format(count, link_url)


def main():
    args = create_parser().parse_args()

    if not os.path.exists(args.config):
        raise Exception("config doesn't exists")

    with open(args.config, "r") as f:
        config = json.load(f)

    while True:
        for link in config["links"]:
            load(link)

        with open(LOADED_DATES_FILE, "wb") as f:
            pickle.dump(last_loaded_date, f)

        time.sleep(config["period"])

if __name__ == "__main__":
    main()
