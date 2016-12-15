from __future__ import print_function

import argparse
import json
import os
import pickle

from common.db import Database
from common.util.config import check_config
from classifier import ArticleClassifier

def create_parser():
    parser = argparse.ArgumentParser('')
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

    db = Database(db_config)
    articles = []
    for geo in db.read_without_category():
        articles.append(geo.content)
        if len(articles) > 400:
            break

    classifier = ArticleClassifier()
    classifier.train(articles)
    with open('kmeans.model', 'wb') as f:
        pickle.dump(classifier, f)

if __name__ == "__main__":
    main()
