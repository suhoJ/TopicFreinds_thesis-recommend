from bertopic import BERTopic
from sklearn.cluster import DBSCAN
from bertopic.vectorizers import ClassTfidfTransformer
from gensim.models import CoherenceModel
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO
from preprocess import DataProcessor

class TopicModeler:   # 기존 클래스명과 동일하게 이름 수정
    def __init__(self, tokenizer, max_features=3000):
        self.vectorizer = CountVectorizer(tokenizer=DataProcessor.filter_word, max_features=max_features)
        self.ctfidf_model = ClassTfidfTransformer()

    def fit_model(self, docs, embedding_model="sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens"):
        topic_model = BERTopic(embedding_model=embedding_model,
                               vectorizer_model=self.vectorizer,
                               ctfidf_model=self.ctfidf_model,
                               top_n_words=5,
                               min_topic_size=30,
                               nr_topics="auto",
                               verbose=True)
        topics, _ = topic_model.fit_transform(docs)
        return topic_model
