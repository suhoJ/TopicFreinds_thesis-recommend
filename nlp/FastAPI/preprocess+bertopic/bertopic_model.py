from bertopic import BERTopic
from sklearn.cluster import DBSCAN
from bertopic.vectorizers import ClassTfidfTransformer
from gensim.models import CoherenceModel
from sklearn.feature_extraction.text import CountVectorizer
from konlpy.tag import Mecab

class DataProcessor:
    def __init__(self, tagger, engine, n=2):
        self.engine = engine
        self.n = n
        self.tagger = tagger
        self.preprocessed_news_data = None
        self.stopwords = ['에게', '통해', '각각', '때문', '무단', '따른', '기자', '는데', '저작', '뉴스', '특파원', '하다', '이번', '이상',
             '전년', '제품', '업체', '기업', '지난해', '대비', '올해', '의원', '내년도', '절반', '당기', '대표', '만나', '분기',
             '국민', '정부', '지역', '현수막', '비중', '포토', 'vs', '파렴치','오전', '오후','정보', '이날', '상품', '세계',
             '시장', '경제', '과학', '사회', '문화', '정치', '처음', '가능', '매출', '소재', '작품', '자신', '위치', 
             '수준', '라이프', '여파', '해석', '고객', '국내', '관련', '내년', 'gb gb', '주요']   # 계속 변동 예정
        self.correction_dict = {'lg' : '엘지', '중신' : '중신용', 'rd': 'R&D', '생활건강': '엘지생활건강', '예술전당': '예술의전당', '엘지생활':'엘지생활건강'}
        
   def __call__(self, text):
        text = text[:1000000]     # 텍스트 길이 제한(메모리용량 절약)
        raw_pos_tagged = self.tagger.pos(text)
        word_cleaned = []
        for word, tag in raw_pos_tagged:
            if tag in ['NNG', "SL"] and (len(word) != 1) and (word not in self.stopwords):
                word_cleaned.append(word)

        # n-gram 생성(bigram)
        ngrams = zip(*[word_cleaned[i:] for i in range(self.n)])
        ngram_list = ["".join(ngram) for ngram in ngrams]  # 띄어쓰기 없이 단어를 연결

        # 단어 대체(짤린 단어들 보완)
        corrected_ngram_list = []
        for ngram in ngram_list:
            for wrong, correct in self.correction_dict.items():
                ngram = ngram.replace(wrong, correct)
            corrected_ngram_list.append(ngram)

        return corrected_ngram_list
       
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
    category_keywords = {}

    for category in df['category'].unique():
        category_docs = df[df['category'] == category]['text'].apply(lambda x: ' '.join(x))
        model = modeler.fit_model(category_docs)
        category_models[category] = model

        # 각 카테고리별 주요 키워드 추출
        topic_info = model.get_topic_info()
        top_topics = topic_info[topic_info['Name'] != '-1']  # -1은 노이즈를 나타내므로 제외
        keywords = [word for word, _ in model.get_topic(top_topics['Topic'][0])]  # 가장 큰 토픽의 키워드
        category_keywords[category] = keywords
    return category_models, category_keywords
