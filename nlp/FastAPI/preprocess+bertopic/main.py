from fastapi import FastAPI, HTTPException
from preprocess import DataProcessor
import pandas as pd
import sqlalchemy
import logging
from bertopic_model import 

# Update this with your MySQL RDS credentials
db_username = "goorm"
db_password = "goorm1415"
db_host = "thesis-mysql.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com"
db_name = "mydatabase"
mysql_connection_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}"

# Create a database engine
engine = sqlalchemy.create_engine(mysql_connection_string)

app = FastAPI()

class TextData(BaseModel):
    text: str
    category: str

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
