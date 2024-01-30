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
    
    # preprocessed_data = preprocess.preprocess_data(start_date, end_date)  # 전처리 메서드 호출
    preprocessed_data = preprocess.preprocess_data(20231201, 20231201)    # 테스트용
    
    # 전처리된 데이터를 데이터베이스에서 조회
    query = "SELECT * FROM preprocessed_news"
    df = pd.read_sql_query(sql=query, con=engine)
    
    # DataProcessor 인스턴스 생성- db에 저장할 필요없음, DataProcessor와 TopicModeler를 분리하면 안됨.
    data_processor = DataProcessor(tagger=mecab, engine=engine, n=2)  
    # TopicModeler 인스턴스 생성, 이 때 tokenizer로 data_processor를 넘겨줌, bertopic자체에서 토큰화 진행됨. db 저장하려면 모델 다 돌리고 저장해야함.
    topic_modeler = TopicModeler(dataprocessor=data_processor, max_features=3000)

    # 'text' 열의 데이터를 fit_model에 입력
    topic_model = topic_modeler.fit_model(df['text'])
    
    return {"message": "Data preprocessed successfully", "data": preprocessed_data}


@app.get("/")
async def home():
    return "Welcome to the preprocess App!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
