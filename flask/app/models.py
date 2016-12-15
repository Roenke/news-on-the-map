from app import db


class Likes(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key = True)
    user_email = db.Column(db.String(256))
    news_id = db.Column(db.Integer)
    category_id = db.Column(db.Integer)

    __table_args__ = (db.UniqueConstraint('user_email', 'news_id', name='uniq'),)

    def __repr__(self):
        return '<like from {} to {} with category {}'.format(self.user_email, self.news_id, self.category_id)
