# from bertopic import BERTopic
# from gensim.models.coherencemodel import CoherenceModel
# from gensim.corpora.dictionary import Dictionary
# import pandas as pd
# import ast
# import itertools

# class TopicModeler:
#     def __init__(self, topic_number, topn, data):
#         self.category_models = {}
#         self.topic_number = topic_number
#         self.topn = topn
#         self.data = data

#     def analyze_topics(self, df):
#         grouped = df.groupby('category')
#         keyword_combinations = []
#         for category, group in grouped:
#             documents = group['tokenized_text_mc'].apply(' '.join).tolist()
#             topic_model = BERTopic(language="multilingual", calculate_probabilities=True, verbose=True)
#             topics, _ = topic_model.fit_transform(documents)

#             self.category_models[category] = topic_model
#             keyword_combinations.extend(self.process_topics(category, group, topic_model, topics))

#         return keyword_combinations

#     def process_topics(self, category, group, topic_model, topics):
#         keyword_combinations = []
#         for topic_num in set(topics):
#             if topic_num == -1:
#                 continue
#             topic_keywords = topic_model.get_topic(topic_num)
#             keywords = ", ".join([word for word, _ in topic_keywords])
#             print(f"Category: {category}, Topic: {topic_num}, Keywords: {keywords}")

#         top_keywords = [word for word, _ in topic_model.get_topic(self.topic_number)[:self.topn]]
#         print(f"Category: {category}, Top {self.topn} Keywords for Topic {self.topic_number}: {top_keywords}")

#         keyword_combinations.extend(self.generate_keyword_combinations(top_keywords))

#         coherence_score = self.calculate_coherence_score(group['tokenized_text_mc'].tolist(), topic_model)
#         print(f"Category: {category}, Coherence Score: {coherence_score}")

#         return keyword_combinations

#     def generate_keyword_combinations(self, top_keywords):
#         keyword_combinations = list(itertools.combinations(top_keywords, 2))[:5]
#         return [' '.join(combination) for combination in keyword_combinations]

#     def calculate_coherence_score(self, texts, topic_model):
#         gensim_dictionary = Dictionary([text.split() for text in texts])
#         topics = topic_model.get_topics()
#         top_n_words = [[word for word, _ in topic_model.get_topic(topic)] for topic in topics if topic != -1]
#         coherence_model = CoherenceModel(topics=top_n_words, texts=[text.split() for text in texts], dictionary=gensim_dictionary, coherence='c_v')
#         return coherence_model.get_coherence()

# # Example usage:
# # df = pd.DataFrame({'category': ['category1', 'category2'], 'tokenized_text_mc': [['word1', 'word2'], ['word3', 'word4']]})
# # modeler = TopicModeler(10, 5, df)
# # keyword_combinations = modeler.analyze_topics(df)
# # print(keyword_combinations)

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
    category_keywords = {}

    for category in df['category'].unique():
        category_docs = df[df['category'] == category]['tokenized_text_mc']
        model = modeler.fit_model(category_docs)
        category_models[category] = model

        # 각 카테고리별 주요 키워드 추출
        topic_info = model.get_topic_info()
        top_topics = topic_info[topic_info['Name'] != '-1']  # -1은 노이즈를 나타내므로 제외
        keywords = ["; ".join(model.get_topic(topic)[0]) for topic in top_topics['Topic']]
        category_keywords[category] = keywords
        
    return category_models, category_keywords