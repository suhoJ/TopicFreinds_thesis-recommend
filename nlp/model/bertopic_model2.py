from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer

class CategoryBERTopicModeler:
    def __init__(self, tokenizer, max_features=3000):
        self.vectorizer = CountVectorizer(tokenizer=tokenizer, max_features=max_features)
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
    modeler = CategoryBERTopicModeler(tokenizer)
    category_models = {}

    for category in df['category'].unique():
        category_docs = df[df['category'] == category]['text']
        model = modeler.fit_model(category_docs)
        category_models[category] = model

        # 각 카테고리별 주요 키워드 추출
        topic_info = model.get_topic_info()
        top_topics = topic_info[topic_info['Name'] != '-1']  # -1은 노이즈를 나타내므로 제외
        keywords = ["; ".join(model.get_topic(topic)[0]) for topic in top_topics['Topic']]
        category_keywords[category] = keywords
        
    return category_models, category_keywords
