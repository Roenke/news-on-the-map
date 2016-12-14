class RawArticle:
    def __init__(self, content, date, source_url, article_url):
        self.content = content
        self.date = date
        self.source_url = source_url
        self.article_url = article_url


class IdentityRawArticle(RawArticle):
    def __init__(self, identity, raw):
        RawArticle.__init__(self, raw.content, raw.date,
                            raw.source_url, raw.article_url)
        self.raw_id = identity


class GeoPoint:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon


class GeoArticle(IdentityRawArticle):
    def __init__(self, raw, geo, geo_words):
        IdentityRawArticle.__init__(self, raw.raw_id, raw)
        self.geo = geo
        self.geo_words = geo_words


class IdentityGeoArticle(GeoArticle):
    def __init__(self, identity, geo_id):
        GeoArticle.__init__(self, geo_id, geo_id.geo)
        self.geo_id = identity


class Article(IdentityGeoArticle):
    def __init__(self, category, geo_id):
        IdentityGeoArticle.__init__(self, geo_id.geo_id, geo_id)
        self.category = category


class IdentityArticle(Article):
    def __init__(self, identity, article):
        Article.__init__(self, article.category, article)
        self.article_id = identity
