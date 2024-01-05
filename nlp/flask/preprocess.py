import pandas as pd
import sqlite3
import re
from konlpy.tag import Mecab

symbol = re.compile(r"^[^\w\d가-힣]+")
email_pattern = re.compile(r"[\s\Wa-zA-Z0-9]*@")
symbol_mid = re.compile(r"[^가-힣a-zA-Z0-9\s]")
title_pattern = re.compile(r"\[.*?\]\s?")

def process_text(row):
    email_address = email_pattern.search(row)
    if email_address:
        processed_text = row[:email_address.start()]
    else:
        processed_text = row

    text = symbol.sub("", processed_text)
    text = symbol_mid.sub("", text)
    text = re.sub("[],,ㆍ·\'\"’‘”“!?\\‘|\<\>`\'[\◇…@▶▲ⓒ]", " ", text)
    text = text.strip()
    return text

def process_title(title):
    processed_title = title_pattern.sub("", title)
    return processed_title

# Stopwords and correction dictionary
stopwords = ['에게', '통해', '각각', '때문','무단','따른','금지','기자','는데','저작','뉴스', '특파원', '하다']
correction_dict = {
    '친환': '친환경',
    '열사': '계열사',
    '제화': '법제화',
}

def filter_word(text):
    '''
    Tokenizes the text, retainging only nouns and foreign words. (NNG:일반 명사, NNP:고유 명사, SL:외국어)
    Single-character words and stopwords are excluded from the tokenization process.
    '''
    mecab = Mecab()
    raw_pos_tagged = mecab.pos(text)
    word_cleaned = []
    for i in range(len(raw_pos_tagged)):
        word, tag = raw_pos_tagged[i]
        corrected_word = correction_dict.get(word, word)
        if tag in ['NNG', 'NNP', "SL"] and (len(corrected_word) != 1) and (corrected_word not in stopwords):
            word_cleaned.append(corrected_word)
    return word_cleaned

class DataProcessor:
    def __init__(self, db_path):
        self.db_path = db_path
        self.preprocessed_news_data = None

    def preprocess_data(self):
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM news_crawl"
            df = pd.read_sql_query(query, conn)

        df = df.drop_duplicates(subset="document")
        df = df.dropna()
        df["title"] = df["title"].apply(process_text)
        df["title"] = df["title"].apply(process_title)
        df["document"] = df["document"].apply(process_text)
        df["text"] = df["title"] + " " + df["document"]
        df["tokenized_text_mc"] = df["text"].apply(filter_word)

        # Saving of preprocessed data
        self.preprocessed_news_data = df

