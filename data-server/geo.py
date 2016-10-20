# coding=utf-8
import argparse
import json
import os
import random
import pymorphy2
import requests

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


def normalize_sentence(sentence):
    return sentence.lower().replace(u'ё', u'е')


def create_morph():
    return pymorphy2.MorphAnalyzer()


def create_street_set(street_file):
    result = []
    with open(street_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            result.append(normalize_sentence(line.decode('utf-8').rstrip('\n')))
    return set(result)


def get_geo(raw_article, street_set, morph):
    def geocodeAddress(address):
        lat_min = 59.775757
        lat_max = 60.185233
        lon_min = 29.505844
        lon_max = 30.780945
        url = 'https://geocode-maps.yandex.ru/1.x/'
        bbox = format('%f,%f~%f,%f' % (lon_min, lat_min, lon_max, lat_max))
        params = {'geocode': u'Санкт-Петербург, ' + address, 'bbox': bbox, 'rspn': 1, 'format': 'json'}
        try:
            r = requests.get(url, params=params)
            try:
                f = r.json()['response']['GeoObjectCollection']['featureMember']
                if len(f) > 0:
                    return f[0]['GeoObject']['Point']['pos']
                else:
                    return None
            except KeyError:
                print 'Wrong format of response %s' % r.json()
        except Exception as e:
            print 'Exception during geocoding', e
            return None

    def get_coord(text, street_set):
        for w in text.split():
            w = w.decode('utf-8')
            w = morph.parse(w)[0].normal_form
            w = normalize_sentence(w)
            if w in street_set:
                res = geocodeAddress(w)
                if res is not None:
                    print 'For word ', w, ' found coords', res
                    res = res.split()
                    return GeoPoint(float(res[1]), float(res[0]))
        return None

    point = get_coord(raw_article.content, street_set)
    if point is not None:
        return GeoArticle(raw_article, point)
    else:
        return None


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
        geo = get_geo(raw_row, create_street_set('streets.txt'), create_morph())

        if geo is not None:
            raw_row.content.replace('\n', ' ')
            preview = raw_row.content[:PREVIEW_LINE_LEN]
            print "id = %d, content = %s..., point = (%f%f)" \
                  % (raw_row.raw_id, preview, geo.geo.lat, geo.geo.lon)
            db.write_with_geo(geo)


if __name__ == "__main__":
    main()
