from fastapi import FastAPI, HTTPException
import pandas as pd
import sqlalchemy
import logging

from bert_model import TopicModeler, DataProcessor,extract_top_keywords,create_wordcloud

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

# Update this with your MySQL RDS credentials
db_username = "goorm"
db_password = "goorm1415"
db_host = "thesis-mysql.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com"
db_name = "mydatabase"
mysql_connection_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}"

# Create a database engine
engine = sqlalchemy.create_engine(mysql_connection_string)

app = FastAPI()

Base = declarative_base()

class CategoryKeywords(Base):
    __tablename__ = 'category_keywords'
    id = Column(Integer, primary_key=True)
    category = Column(String(50))
    keywords = Column(Text)

@app.get("/modeling")
async def modeling():
    try:
        df = pd.read_sql('SELECT * FROM preprocessed_news', engine)
        
        dataprocessor = DataProcessor()
        topic_modeler = TopicModeler(dataprocessor)

        filtered_df = df[df['tokenized_text_mc'].notnull()]

        # Iterate over each category
        for category in filtered_df['category'].unique():
            if category == 'Economy':
                continue
            # Filter the DataFrame for the current category
            category_df = filtered_df[filtered_df['category'] == category]

            # Extract the text data
            texts = category_df['tokenized_text_mc'].tolist()

            # Fit the topic model on the text data
            topic_model = topic_modeler.fit_model(texts)

            # Extract the top keywords for each topic
            top_keywords = extract_top_keywords(topic_model)

            keywords_str = ', '.join(top_keywords)

            # Create a new CategoryKeywords object
            new_keywords_entry = CategoryKeywords(category=category, keywords=keywords_str)

            # Insert the new object into the database
            with engine.begin() as conn:
                conn.add(new_keywords_entry)

            print(f'{category} : {top_keywords}')

            # Create and display a word cloud
            create_wordcloud(top_keywords)

        for category in filtered_df['category'].unique():
            if category == 'Economy':
                continue
            # Filter the DataFrame for the current category
            category_df = filtered_df[filtered_df['category'] == category]

            # Extract the text data
            texts = category_df['document'].tolist()

            # Fit the topic model on the text data
            topic_model = topic_modeler.fit_model(texts)

            # Extract the top keywords for each topic
            top_keywords = extract_top_keywords(topic_model)

            keywords_str = ', '.join(top_keywords)

            # Create a new CategoryKeywords object
            new_keywords_entry = CategoryKeywords(category=category, keywords=keywords_str)

            # Insert the new object into the database
            with engine.begin() as conn:
                conn.add(new_keywords_entry)

            print(f'{category} : {top_keywords}')

            # Create and display a word cloud
            create_wordcloud(top_keywords)

        return {
            "status": "success",
            "message": "Topic modeling completed."
        }
    except Exception as e:
        logging.error(f"An error occurred in the modeling route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def home():
    return "Welcome to the model App!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
