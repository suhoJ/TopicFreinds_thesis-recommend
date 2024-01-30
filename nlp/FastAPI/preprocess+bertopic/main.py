from fastapi import FastAPI, HTTPException
import preprocess 
import pandas as pd
import sqlalchemy
import logging
import preprocess
from tokenizer import DataProcessor
from bertopic_model import TopicModeler
from konlpy.tag import Mecab

# Update this with your MySQL RDS credentials
db_username = "goorm"
db_password = "goorm1415"
db_host = "thesis-mysql.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com"
db_name = "mydatabase"
mysql_connection_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}"

# Create a database engine
engine = sqlalchemy.create_engine(mysql_connection_string)

app = FastAPI()
mecab = Mecab()
class TextData(BaseModel):
    text: str
    category: str

@app.post("/preprocess")
def preprocess_data(start_date: str = Query(None), end_date: str = Query(None)):
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Start date and end date must be provided")

    data_processor = DataProcessor(tagger=mecab, engine=engine, n=2)  # DataProcessor 인스턴스 생성
    # preprocessed_data = data_processor.preprocess_data(start_date, end_date)  # 전처리 메서드 호출
    preprocessed_data = data_processor.preprocess_data(20231201, 20231201)    # 테스트용
    return {"message": "Data preprocessed successfully", "data": preprocessed_data}

@app.post("/analyze/")
async def analyze_text(data: TextData):
    # 데이터를 DataFrame으로 변환
    df = pd.DataFrame([data.dict()])

    # 토픽 모델링 수행
    try:
        models = train_topic_model(df)
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def home():
    return "Welcome to the preprocess App!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
