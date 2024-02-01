import pandas as pd
import re
from konlpy.tag import Mecab
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base #2.0미만 버전
from sqlalchemy.orm import declarative_base  #2.0이상 버전
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
    text = Column(LONGTEXT)

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

def create_table(self):
    Base.metadata.create_all(engine)

def save_preprocessed_data(engine, preprocessed_news_data):
    if preprocessed_news_data is not None:
        data_dict = preprocessed_news_data.to_dict(orient='records')
    
        with engine.begin() as connection:  # Automatically commits or rolls back
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
    df["title"] = df["title"].apply(self.process_text)     # 수정 : self 추가
    df["title"] = df["title"].apply(self.process_title)
    df["document"] = df["document"].apply(self.process_text)
    
    # Combine title and document for tokenization
    df["text"] = df["title"] + " " + df["document"]
    
    # Debugging: Print DataFrame and columns
    print("DataFrame after tokenization:")
    print(df.head())
    print("DataFrame columns:", df.columns)
    
    # Ensure tokenized_text_mc column exists
    if 'text' not in df.columns:
        raise Exception("Column 'text' not found in DataFrame")
    
    preprocessed_news_data = df
    create_table(engine)
    save_preprocessed_data(engine, df)
