import argparse
import json
import os
import random

from common.article import Article
from common.db import Database

PREVIEW_LINE_LEN = 100


def create_parser():
    parser = argparse.ArgumentParser('')
    parser.add_argument("--config", required=False, type=str,
                        help="path to geo-coder config file")
    parser.add_argument("--db", required=True, type=str,
                        help="path to database config file")

    return parser


def get_category(geo_article):
    return int(random.uniform(1, 10))


def main():
    args = create_parser().parse_args()

    if not os.path.exists(args.db):
        raise Exception("config doesn't exists")

    with open(args.db, "r") as f:
        db_config = json.load(f)

    if "db_config" not in db_config:
        raise Exception("you should proved db config")

    db = Database(db_config["db_config"])
    for geo in db.read_without_category():
        category = get_category(geo)
        article = Article(category, geo)

        geo.content.replace('\n', ' ')
        preview = geo.content[:PREVIEW_LINE_LEN]
        print "geo_id = %d, content = %s..., category = %d" \
              % (geo.geo_id, preview, article.category)

        db.write_with_category(article)


if __name__ == "__main__":
    main()
