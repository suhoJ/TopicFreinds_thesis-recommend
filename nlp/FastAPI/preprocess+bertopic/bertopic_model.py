from bertopic import BERTopic
from sklearn.cluster import DBSCAN
from bertopic.vectorizers import ClassTfidfTransformer
from gensim.models import CoherenceModel
from sklearn.feature_extraction.text import CountVectorizer
from konlpy.tag import Mecab

class TopicModeler:
    def __init__(self, tokenizer, max_features=3000):
        self.vectorizer = CountVectorizer(tokenizer=custom_tokenizer, max_features=max_features)
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

def apply_category_models(df, tokenizer):
    modeler = TopicModeler(tokenizer)
    category_models = {}
    category_keywords = {}

    for category in df['category'].unique():
        category_docs = df[df['category'] == category]['tokenized_text_mc'].apply(lambda x: ' '.join(x))
        model = modeler.fit_model(category_docs)
        category_models[category] = model

        # 각 카테고리별 주요 키워드 추출
        topic_info = model.get_topic_info()
        top_topics = topic_info[topic_info['Name'] != '-1']  # -1은 노이즈를 나타내므로 제외
        keywords = [word for word, _ in model.get_topic(top_topics['Topic'][0])]  # 가장 큰 토픽의 키워드
        category_keywords[category] = keywords
    return category_models, category_keywords
