from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans

from stop_words import get_stop_words


class ArticleClassifier:
    def __init__(self):
        n_features = 1000
        self.tfid = TfidfVectorizer(n_features, stop_words=get_stop_words('ru'), norm=None, binary=False)
        self.vectorizer = make_pipeline(self.tfid, TfidfTransformer())
        self.svd = TruncatedSVD(n_components=15)
        self.normalizer = Normalizer(copy=False)
        self.lsa = make_pipeline(self.svd, self.normalizer)
        self.km = KMeans(init='k-means++', max_iter=400, n_init=1, verbose=False, n_jobs=-1)

    def train(self, articles):
        print("Extracting features from the training dataset using a sparse vectorizer")
        X = self.vectorizer.fit_transform(articles)

        print("Performing dimensionality reduction using LSA")
        X = self.lsa.fit_transform(X)
        explained_variance = self.svd.explained_variance_ratio_.sum()
        print("Explained variance of the SVD step: {}%".format(
            int(explained_variance * 100)))
        self.km.fit(X)

    def get_class(self, article):
        X = self.vectorizer.fit_transform([article])
        X = self.lsa.fit_transform(X)
        return self.km.predict(X)
