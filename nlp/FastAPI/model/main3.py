from fastapi import FastAPI, HTTPException
# from news_crawler import start_crawling
from preprocess import DataProcessor
from bertopic_model import TopicModeler, apply_category_models
# from KCI_Search_API import get_api
import pandas as pd
import sqlalchemy
import logging

# Update this with your MySQL RDS credentials
db_username = "goorm"
db_password = "goorm1415"
db_host = "thesis-mysql.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com"
db_name = "mydatabase"
mysql_connection_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}"

# Create a database engine
engine = sqlalchemy.create_engine(mysql_connection_string)

class CategoryData(BaseModel):
    text: str
    category: str
    
app = FastAPI()

@app.get("/modeling")
async def modeling():
    try:
        df = pd.read_sql('SELECT * FROM preprocessed_news', engine)
        topic_modeler = TopicModeler(DataProcessor.filter_word)                   # 추가: bertopic으로 키워드 반환되게 수정.

        for category in df['category'].unique():
            category_docs = df[df['category'] == category]['text'].astype(str)
            topic_model = topic_modeler.fit_model(category_docs)
            top_keywords = extract_top_keywords(topic_model)
            wordcloud_img = generate_wordcloud(topic_model)
            results[category] = {
                "top_keywords": top_keywords,
                "wordcloud": wordcloud_img
            }

    return results
        return {"status": "success", "message": "Topic modeling completed."}
    except Exception as e:
        logging.error(f"An error occurred in the modeling route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def home():
    return "Welcome to the modeling App!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
