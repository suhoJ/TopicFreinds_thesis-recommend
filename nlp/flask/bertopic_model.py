from bertopic import BERTopic
from gensim.models.coherencemodel import CoherenceModel
from gensim.corpora.dictionary import Dictionary
import ast
import itertools

class TopicModeler:
    def __init__(self, topic_number, topn, data):
        self.category_models = {}
        self.topic_number = topic_number  # number 0 is the most frequent topic
        self.topn = topn   # number of keywords
        self.data = data

    def analyze_topics(self, df):
        grouped = df.groupby('category')
        for category, group in grouped:
            documents = group['tokenized_text_mc'].apply(' '.join).tolist()
            topic_model = BERTopic(language="multilingual", calculate_probabilities=True, verbose=True)
            topics, _ = topic_model.fit_transform(documents)

            self.category_models[category] = topic_model
            self.process_topics(category, group, topic_model, topics)

    def process_topics(self, category, group, topic_model, topics):
        for topic_num in set(topics):
            if topic_num == -1:
                continue
            topic_keywords = topic_model.get_topic(topic_num)
            keywords = ", ".join([word for word, _ in topic_keywords])
            print(f"Category: {category}, Topic: {topic_num}, Keywords: {keywords}")

        top_keywords = topic_model.get_topic(self.topic_number)[:self.topn]
        print(f"Category: {category}, Top {self.topn} Keywords for Topic {self.topic_number}: {top_keywords}")

        for category, topic_model in self.category_models.items():
            coherence_score = self.calculate_coherence_score(group['tokenized_text_mc'].tolist(), topic_model)
            print(f"Category: {category}, Coherence Score: {coherence_score}")

    def calculate_coherence_score(self, texts, topic_model):
        gensim_dictionary = Dictionary(texts)
        topics = topic_model.get_topics()
        top_n_words = [[word for word, _ in topic_model.get_topic(topic)] for topic in topics if topic != -1]
        coherence_model = CoherenceModel(topics=top_n_words, texts=texts, dictionary=gensim_dictionary, coherence='c_v')
        return coherence_model.get_coherence()

    def generate_keyword_combinations(self, top_keywords):
        keyword_combinations = list(itertools.combinations(top_keywords, 2))[:5]
        return [' '.join(combination) for combination in keyword_combinations]


