import argparse
import json
import os
import time
from datetime import datetime
import cPickle as pickle


import rss_feed
import vk_feed
from db import Database


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


loaders = {
    "rss": rss_feed.load,
    "vk":  vk_feed.load
}


def load(db, link):
    typ = link["type"]
    link_url = link["url"]
    loaded_count = 0

    max_date = last_loaded_date[link_url] if link_url in last_loaded_date else datetime.fromtimestamp(0)
    for (text, date, url) in loaders[typ](link_url):
        if link_url in last_loaded_date and last_loaded_date[link_url] >= date:
            break

        max_date = max(max_date, date)
        db.insert(text, date, link_url, url)
        loaded_count += 1
        if loaded_count == MAX_FEED_COUNT:
            break

    last_loaded_date[link_url] = max_date
    print "loaded {} feeds for {}".format(loaded_count, link_url)


def main():
    args = create_parser().parse_args()

    if not os.path.exists(args.config):
        raise Exception("config doesn't exists")

    with open(args.config, "r") as f:
        config = json.load(f)

    if "db_config" not in config:
        raise Exception("you should proved db config")

    db = Database(config["db_config"])
    while True:
        for link in config["links"]:
            load(db, link)

        with open(LOADED_DATES_FILE, "wb") as f:
            pickle.dump(last_loaded_date, f)

        time.sleep(config["period"])

if __name__ == "__main__":
    main()
