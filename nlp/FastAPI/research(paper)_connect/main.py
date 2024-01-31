from fastapi import FastAPI, HTTPException, Query
from typing import List
# from news_crawler import start_crawling
from preprocess import DataProcessor
from bertopic_model import TopicModeler, apply_category_models
from KCI_Search_API import get_api
import pandas as pd
import sqlalchemy
import logging

# # Update this with your MySQL RDS credentials
# db_username = "goorm"
# db_password = "goorm1415"
# db_host = "thesis-mysql.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com"
# db_name = "mydatabase"
# mysql_connection_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}"

# # Create a database engine
# engine = sqlalchemy.create_engine(mysql_connection_string)

app = FastAPI()

def search_papers(search_term: str) -> List[str]:
    results = get_api(search_term)  # 실제 검색 API를 호출하고 결과를 저장
    return results  # 실제 검색 결과를 반환

@app.get("/search_papers")
async def get_search_results(search_term: str = Query(...)):
    return search_papers(search_term)

@app.get("/")
async def home():
    return "Welcome to the modeling App!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
