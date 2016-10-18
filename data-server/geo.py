import argparse
import json
import os
import random

from common.article import GeoArticle, GeoPoint
from common.db import Database
from common.util.config import check_config

lat_min = 59.775757
lat_max = 60.185233
lon_min = 29.505844
lon_max = 30.780945


def create_parser():
    parser = argparse.ArgumentParser('')
    parser.add_argument("--config", required=False, type=str,
                        help="path to geo-coder config file")
    parser.add_argument("--db", required=True, type=str,
                        help="path to database config file")
    return parser


def get_geo(raw_article):
    # TODO: use geo-coding services for raw_article
    point = GeoPoint(random.uniform(lat_min, lat_max),
                     random.uniform(lon_min, lon_max))
    return GeoArticle(raw_article, point)


PREVIEW_LINE_LEN = 100


def main():
    args = create_parser().parse_args()

    if not os.path.exists(args.db):
        raise Exception("config doesn't exists")

    with open(args.db, "r") as f:
        db_config = json.load(f)

    check_config(db_config, args.db, 'host', 'port', 'user', 'password', 'database')

    db = Database(db_config)
    for raw_row in db.read_raw_without_geo():
        geo = get_geo(raw_row)

        if geo is not None:
            raw_row.content.replace('\n', ' ')
            preview = raw_row.content[:PREVIEW_LINE_LEN]
            print "id = %d, content = %s..., point = (%f%f)" \
                  % (raw_row.raw_id, preview, geo.geo.lat, geo.geo.lon)
            db.write_with_geo(geo)


if __name__ == "__main__":
    main()
