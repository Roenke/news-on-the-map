import psycopg2
from ast import literal_eval as make_tuple

from common.article import RawArticle, IdentityRawArticle, GeoArticle, GeoPoint, IdentityGeoArticle


class Database(object):
    def __init__(self, config):
        self.db = psycopg2.connect(host=config["host"], port=config["port"],
                                   user=config["user"], password=config["password"],
                                   database=config["database"])

    def insert_raw(self, raw):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO raw_news (content_of_news, publish_date, source_url, article_url) "
            "VALUES (%s, %s, %s, %s);",
            (raw.content, raw.date, raw.source_url, raw.article_url))
        self.db.commit()

    def read_raw_without_geo(self):
        """Reads all raw news without geo information"""
        query = """SELECT
                        raw_news.id,
                        raw_news.content_of_news,
                        raw_news.publish_date,
                        raw_news.source_url,
                        raw_news.article_url
                    FROM raw_news
                    LEFT OUTER JOIN geo_news
                    ON raw_news.id = geo_news.raw_news_id
                    WHERE geo_news.id IS NULL"""
        cursor = self.db.cursor()
        cursor.execute(query)
        for row in cursor:
            raw = RawArticle(row[1], row[2], row[3], row[4])
            yield IdentityRawArticle(row[0], raw)

    def read_raw_data(self):
        """Reads all raw news"""
        query = """SELECT
                        raw_news.id,
                        raw_news.content_of_news,
                        raw_news.publish_date,
                        raw_news.source_url,
                        raw_news.article_url
                    FROM raw_news"""
        cursor = self.db.cursor()
        cursor.execute(query)
        for row in cursor:
            raw = RawArticle(row[1], row[2], row[3], row[4])
            yield IdentityRawArticle(row[0], raw)

    def write_with_geo(self, geo_article):
        cursor = self.db.cursor()
        query = "INSERT INTO geo_news (raw_news_id, coord, location_words) " \
                "VALUES (%s, POINT(%s, %s), %s)" % (
                    geo_article.raw_id, geo_article.geo.lat, geo_article.geo.lon, geo_article.geo_words)
        cursor.execute(query)
        self.db.commit()

    def read_without_category(self):
        query = """SELECT
                        raw_news.id,
                        raw_news.content_of_news,
                        raw_news.publish_date,
                        raw_news.source_url,
                        raw_news.article_url,
                        geo_news.id,
                        geo_news.coord,
                        geo_news.location_words
                    FROM geo_news
                    LEFT OUTER JOIN news
                    ON geo_news.id = news.geo_news_id
                    JOIN raw_news
                    ON geo_news.raw_news_id = raw_news.id
                    WHERE news.id IS NULL"""

        cursor = self.db.cursor()
        cursor.execute(query)
        for row in cursor:
            raw = RawArticle(row[1], row[2], row[3], row[4])
            id_raw = IdentityRawArticle(row[0], raw)
            geo = GeoArticle(id_raw, GeoPoint(*make_tuple(row[6])), row[7])
            yield IdentityGeoArticle(row[5], geo)

    def write_with_category(self, article):
        cursor = self.db.cursor()
        query = "INSERT INTO news (geo_news_id, category) " \
                "VALUES (%d, %d)" % (article.geo_id, article.category)
        cursor.execute(query)
        self.db.commit()
