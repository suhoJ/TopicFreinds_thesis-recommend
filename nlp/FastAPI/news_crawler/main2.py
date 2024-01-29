from fastapi import FastAPI, HTTPException
from news_crawler import start_crawling
# from preprocess import DataProcessor
# from bertopic_model import TopicModeler
# from KCI_Search_API import get_api
import pandas as pd
import sqlalchemy
import logging
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Update this with your MySQL RDS credentials
db_username = "goorm"
db_password = "goorm1415"
db_host = "thesis-mysql.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com"
db_name = "mydatabase"
mysql_connection_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}"

# Create a database engine
engine = sqlalchemy.create_engine(mysql_connection_string)

app = FastAPI()

@app.get("/start-crawling")
async def crawling():
    try:
        # start_crawling(20231207, 20231207)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        date_str = yesterday.strftime("%Y%m%d")
        await start_crawling(date_str, date_str)
        return {"status": "success", "message": "News crawling started."}
    except Exception as e:
        logging.error(f"An error occurred in start_crawling: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def home():
    return "Welcome to the News Crawler App!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
    # 스케줄러 설정
    scheduler = BackgroundScheduler()
    scheduler.add_job(crawling, 'cron', hour=0)  # 매일 자정에 실행
    scheduler.start()           #'interval', hours=1 로 변경시 매 1시간마다 크롤링
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
