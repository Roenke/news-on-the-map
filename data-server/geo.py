# coding=utf-8
import argparse
import json
import os
import re
import pymorphy2
import requests
import string

from common.article import GeoArticle, GeoPoint
from common.db import Database
from common.util.config import check_config

punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~»«"""

bounded_regex = re.compile(u'("|«)(.+)("|»)')
punctuation_set = set(punctuation)

regex = re.compile('[%s]' % re.escape(punctuation))


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


def get_geo(raw_article, street_set, important_words, morph):
    def get_norm_form(w):
        w = regex.sub(' ', w)
        w = morph.parse(w)[0].normal_form
        w = normalize_sentence(w)
        return w

    def get_tag(w):
        w = normalize_sentence(w)
        w = regex.sub(' ', w)
        return morph.parse(w)[0].tag.POS

    def coordinate_gender(word, main_word):
        def change_gen(word, gen):
            res = morph.parse(word)[0].inflect({gen})
            if res is None:
                return word
            else:
                return res.word

        if main_word == u'ул':
            return change_gen(word, 'femn')
        gen = morph.parse(main_word)[0].tag.gender
        if gen is not None:
            return change_gen(word, gen)
        else:
            return word

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

    def get_coord(text):
        for w in text.split():
            w = get_norm_form(w.decode('utf-8'))
            if w in street_set:
                res = geocodeAddress(w)
                if res is not None:
                    print 'For word ', w, ' found coords', res
                    res = res.split()
                    return GeoPoint(float(res[1]), float(res[0]))
        return None

    def get_words(text):
        result = []
        for w in text.split():
            result.append(get_norm_form(w.decode('utf-8')))
        return result

    def get_pairs(text):
        regex.sub(' ', text)
        prev_word_in_set = False
        prev_word = None
        for w in text.split():
            norm = get_norm_form(w.decode('utf-8'))
            tag = morph.parse(w.decode('utf-8'))[0].tag
            if tag.POS != 'PREP' and tag.POS != 'CONJ':
                if prev_word_in_set:
                    if norm in street_set:
                        print 'Pair is ', ' '.join([prev_word, coordinate_gender(norm, prev_word)])
                        yield ' '.join([prev_word, coordinate_gender(norm, prev_word)])
                    prev_word_in_set = False
                if norm in important_words:
                    if prev_word is not None and not prev_word_in_set:
                        if prev_word in street_set:
                            print 'Pair is ', ' '.join([coordinate_gender(prev_word, norm), norm])
                            yield ' '.join([coordinate_gender(prev_word, norm), norm])
                    prev_word_in_set = True
                prev_word = norm

    def get_capitalized(text):
        words = text.split()
        words_len = len(words)
        for i in range(len(words)):
            w = words[i]
            w = w.decode('utf-8')
            if w.istitle():
                norm = get_norm_form(w)
                if i > 0 and words[i - 1][-1] != '.' and norm in street_set:
                    prev_tag = get_tag(words[i - 1].decode('utf-8'))
                    next_tag = None
                    if i < words_len - 1:
                        next_tag = get_tag(words[i + 1].decode('utf-8'))
                    if prev_tag == 'PREP' and (next_tag is None or next_tag != 'NOUN'):
                        if i < words_len - 1:
                            print 'Capitalized is ', words[i - 1], w, words[i + 1], 'with norm', norm
                            yield norm
                        else:
                            print 'Capitalized is ', words[i - 1], w, 'with norm', norm
                            yield norm

    def get_bounded(text):
        for (l, t, r) in re.findall(bounded_regex, text):
            words = t.split()
            if len(words) <= 3:
                yield ' '.join(words)

    count = 0
    for w in get_pairs(raw_article.content):
        res = geocodeAddress(w)
        if res is not None:
            print 'For word ', w, ' found coords', res
            res = res.split()
            yield GeoArticle(raw_article, GeoPoint(float(res[1]), float(res[0])))
        count += 1

    for w in get_capitalized(raw_article.content):
        res = geocodeAddress(w)
        if res is not None:
            print 'For word ', w, ' found coords', res
            res = res.split()
            yield GeoArticle(raw_article, GeoPoint(float(res[1]), float(res[0])))
        count += 1

    if count > 0:
        print 'Count of pairs is ', count


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

        for geo in get_geo(raw_row, create_street_set('streets.txt'), create_street_set('important_words.txt'), create_morph()):
            raw_row.content.replace('\n', ' ')
            preview = raw_row.content[:PREVIEW_LINE_LEN]
            print "id = %d, content = %s..., point = (%f%f)" \
                  % (raw_row.raw_id, preview, geo.geo.lat, geo.geo.lon)
            db.write_with_geo(geo)


if __name__ == "__main__":
    main()
