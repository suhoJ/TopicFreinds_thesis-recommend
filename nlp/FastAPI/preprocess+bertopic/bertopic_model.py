from bertopic import BERTopic
from sklearn.cluster import DBSCAN
from bertopic.vectorizers import ClassTfidfTransformer
from gensim.models import CoherenceModel
from sklearn.feature_extraction.text import CountVectorizer
from konlpy.tag import Mecab
from tokenizer import DataProcessor
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class TopicModeler:
    def __init__(self, dataprocessor, max_features=3000):
        self.vectorizer = CountVectorizer(tokenizer=dataprocessor, max_features=max_features)
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
        
    def get_top_keywords(self, topic_model, max_topic=10):
        top_keywords = []
        for topic_number in sorted(topic_model.get_topics()):
            if topic_number != -1 and topic_number <= max_topic: 
                topic_keywords = topic_model.get_topic(topic_number)
                top_keyword = topic_keywords[0][0]  # 가장 중요도가 높은 키워드 선택
                top_keywords.append((topic_number, top_keyword))
        return top_keywords

    def create_wordcloud(self, all_keywords, width=800, height=400)
        font_path='/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'                 
        wordcloud = WordCloud(font_path=font_path, width=width, height=height, background_color='white')
        wordcloud.generate_from_frequencies(all_keywords)

        # 시각화
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()                     
        
def apply_category_models(df, tokenizer):
    modeler = TopicModeler(tokenizer)
    category_models = {}
    category_top_keywords = {}
    category_wordclouds = {}

    for category in df['category'].unique():
        category_docs = df[df['category'] == category]['text'].apply(lambda x: ' '.join(x))
        model = modeler.fit_model(category_docs)
        category_models[category] = model

        # 각 카테고리별 주요 키워드 추출
        top_keywords = modeler.get_top_keywords(model)
        # 각 카테고리별 워드클라우드 생성
        all_keywords = dict([word, freq] for word, freq in model.get_topic(top_keywords[0][0]))
        wordcloud = modeler.create_wordcloud(all_keywords)

        category_top_keywords[category] = top_keywords
        category_wordclouds[category] = wordcloud
    return category_models, category_top_keywords, category_wordclouds
