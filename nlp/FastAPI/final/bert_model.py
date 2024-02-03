# Import necessary libraries
from konlpy.tag import Mecab
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
    def __init__(self):
        # self.vectorizer = CountVectorizer(tokenizer=tokenizer, max_features=max_features)
        # self.ctfidf_model = ClassTfidfTransformer()
        self.umap_model = UMAP(n_neighbors=15, min_dist=0.1, n_components=5, random_state=42, metric='cosine')
        self.hdbscan_model = hdbscan.HDBSCAN(min_cluster_size=10, metric='euclidean', cluster_selection_method='eom', prediction_data=True)

    def fit_model(self, docs, embedding_model="sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens"):
        topic_model = BERTopic(embedding_model="sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens", \
                 vectorizer_model=vectorizer,
                 top_n_words=15,
                 min_topic_size=10,
                 umap_model=umap_model,hdbscan_model=hdbscan_model,
                 verbose=True)
        topics, probs = model.fit_transform(documents)
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
