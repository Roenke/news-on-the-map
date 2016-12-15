import argparse
import json
import os

from common.article import Article
from common.db import Database
from common.util.config import check_config
import pickle

PREVIEW_LINE_LEN = 100

def create_parser():
    parser = argparse.ArgumentParser('')
    parser.add_argument("--config", required=False, type=str,
                        help="path to geo-coder config file")
    parser.add_argument("--db", required=True, type=str,
                        help="path to database config file")

    return parser


def main():
    args = create_parser().parse_args()

    if not os.path.exists(args.db):
        raise Exception("config doesn't exists")

    with open(args.db, "r") as f:
        db_config = json.load(f)

    check_config(db_config, args.db, 'host', 'port', 'user', 'password', 'database')

    with open("kmeans.model", "rb") as f:
        classifier = pickle.load(f)

    db = Database(db_config)
    for geo in db.read_without_category():
        category = classifier.get_category(geo.content)
        article = Article(category, geo)

        geo.content.replace('\n', ' ')
        preview = geo.content[:PREVIEW_LINE_LEN]
        print("geo_id = %d, content = %s..., category = %d" \
              % (geo.geo_id, preview, article.category))

        # db.write_with_category(article)


if __name__ == "__main__":
    main()
