import psycopg2


class Database(object):
    def __init__(self, config):
        self.db = psycopg2.connect(host=config["host"], port=config["port"],
                              user=config["user"], password=config["password"],
                              database=config["database"])
        self.inserter = self.db.cursor()

    def insert(self, text, date, source_url, article_url):
        self.inserter.execute(
            "INSERT INTO raw_news (content_of_news, publish_date, source_url, article_url) "
            "VALUES (%s, %s, %s, %s);",
            (text, date, source_url, article_url))
        self.db.commit()
