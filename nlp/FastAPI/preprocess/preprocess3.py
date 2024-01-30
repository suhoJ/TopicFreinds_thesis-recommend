import pandas as pd
import re
from konlpy.tag import Mecab
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text
from sqlalchemy.dialects.mysql import LONGTEXT

# SQLAlchemy base class for declarative models
Base = declarative_base()

# Define the schema for the new table
class PreprocessedNews(Base):
    __tablename__ = 'preprocessed_news'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    document = Column(LONGTEXT)
    tokenized_text_mc = Column(LONGTEXT)

# Regex patterns
symbol = re.compile(r"^[^\w\d가-힣]+")
email_pattern = re.compile(r"[\s\Wa-zA-Z0-9]*@")
symbol_mid = re.compile(r"[^가-힣a-zA-Z0-9\s]")
title_pattern = re.compile(r"\[.*?\]\s?")

def process_text(row):
    email_address = email_pattern.search(row)
    processed_text = row[:email_address.start()] if email_address else row
    text = symbol.sub("", processed_text)
    text = symbol_mid.sub("", text)
    text = re.sub("[],,ㆍ·\'\"’‘”“!?\\‘|\<\>`\'[\◇…@▶▲ⓒ]", " ", text)
    return text.strip()

def process_title(title):
    return title_pattern.sub("", title)

class DataProcessor:
    def __init__(self, n=2, engine):
        self.engine = engine
        self.preprocessed_news_data = None
        self.mecab = Mecab() 
        self.n = n
        self.stopwords = ['에게', '통해', '각각', '때문', '무단', '따른', '기자', '는데', '저작', '뉴스', '특파원', '하다', '이번', '이상',
             '전년', '제품', '업체', '기업', '지난해', '대비', '올해', '의원', '내년도', '절반', '당기', '대표', '만나', '분기',
             '국민', '정부', '지역', '현수막', '비중', '포토', 'vs', '파렴치','오전', '오후','정보', '이날', '상품', '세계',
             '시장', '경제', '과학', '사회', '문화', '정치', '처음', '가능', '매출', '소재', '작품', '자신', '위치', 
             '수준', '라이프', '여파', '해석', '고객', '국내', '관련', '내년', 'gb gb', '주요']   # 계속 변동 예정
        self.correction_dict = {'lg' : '엘지', '중신' : '중신용', 'rd': 'R&D', '생활건강': '엘지생활건강', '예술전당': '예술의전당'}
        
   def filter_word(self, sent):
        sent = text[:1000000]     # 텍스트 길이 제한(메모리용량 절약)
        raw_pos_tagged = self.mecab.pos(sent)
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
       
    def create_table(self):
        Base.metadata.create_all(self.engine)

    def save_preprocessed_data(self):
        if self.preprocessed_news_data is not None:
            data_dict = self.preprocessed_news_data.to_dict(orient='records')

            with self.engine.begin() as connection:  # Automatically commits or rolls back
                for record in data_dict:
                    try:
                        connection.execute(PreprocessedNews.__table__.insert(), record)
                    except Exception as e:
                        print(f"Error inserting record: {e}")

    def preprocess_data(self, start_date, end_date):     # 쿼리 추가 - 사용자가 선택하는 날짜에 대해서만 전처리
        query = "SELECT * FROM news_crawl WHERE date >= :start_date AND date <= :end_date"
        df = pd.read_sql_query(sql=query, con=self.engine, params={'start_date': start_date, 'end_date': end_date})
        df = df.drop_duplicates(subset="document")
        df = df.dropna()
        df["title"] = df["title"].apply(process_text)
        df["title"] = df["title"].apply(process_title)
        df["document"] = df["document"].apply(process_text)

        # Combine title and document for tokenization
        df["text"] = df["title"] + " " + df["document"]

        # Apply tokenization and ensure tokenized_text_mc is created
        df["tokenized_text_mc"] = df["text"].apply(self.filter_word)

        # Debugging: Print DataFrame and columns
        print("DataFrame after tokenization:")
        print(df.head())
        print("DataFrame columns:", df.columns)

        # Ensure tokenized_text_mc column exists
        if 'tokenized_text_mc' not in df.columns:
            raise Exception("Column 'tokenized_text_mc' not found in DataFrame")

        # Convert 'tokenized_text_mc' list to string
        df["tokenized_text_mc"] = df["tokenized_text_mc"].apply(lambda x: ' '.join(map(str, x)))

        self.preprocessed_news_data = df
        self.create_table()
        self.save_preprocessed_data()
