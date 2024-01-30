from bertopic import BERTopic
from sklearn.cluster import DBSCAN
from bertopic.vectorizers import ClassTfidfTransformer
from gensim.models import CoherenceModel
from sklearn.feature_extraction.text import CountVectorizer
from tokenizer import CustomTokenizer

def train_topic_model(df):
    category_bertopic_models = {}
    custom_tokenizer = CustomTokenizer(Mecab())
    df['tokenized_text_mc'] = df['text'].astype(str)
    ctfidf_model = ClassTfidfTransformer()
    vectorizer = CountVectorizer(tokenizer=custom_tokenizer, max_features=3000)

    # 각 카테고리별로 모델 적용
    for category in df['category'].unique():
        category_docs = df[df['category'] == category]['tokenized_text_mc']

    # 파라미터 조정 - 더 일반적인 토픽을 위한 설정
    topic_model_general = BERTopic(embedding_model="sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens",
                                  vectorizer_model=vectorizer,
                                  ctfidf_model=ctfidf_model,
                                  top_n_words=5,
                                  min_topic_size=30,  # 더 큰 토픽
                                  nr_topics="auto",
                                  calculate_probabilities=True,
                                  verbose=True)

    topics_general, _ = topic_model_general.fit_transform(category_docs)
    print(f"Category: {category} - General Topics")
    general_topic_info = topic_model_general.get_topic_info()  # 결과를 변수에 저장
    # print(general_topic_info)
  
    return category_bertopic_models
