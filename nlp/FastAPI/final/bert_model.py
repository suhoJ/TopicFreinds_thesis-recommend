# Import necessary libraries
from konlpy.tag import Mecab
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from io import StringIO

# Define the custom tokenizer using Mecab
class DataProcessor:
    def __init__(self):
        self.mecab = Mecab()

    def __call__(self, text):
        if text and isinstance(text, str):
            return self.mecab.morphs(text)
        return self.mecab.morphs(text)

# TopicModeler class
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

# Function to extract the top keyword for each topic
def extract_top_keywords(topic_model):
    top_keywords = []
    for topic_number in sorted(topic_model.get_topics()):
        if topic_number != -1 and topic_number < 10:
            topic_keywords = topic_model.get_topic(topic_number)
            top_keyword, weight = topic_keywords[0] # Select the top keyword by importance
            top_keywords.append((topic_number+1, top_keyword, weight))
    return top_keywords

# Function to create and display a word cloud
def create_wordcloud(keywords):
    word_freq = {word: weight for _, word, weight in keywords}
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path='/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf').generate_from_frequencies(word_freq)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()
