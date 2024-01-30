from fastapi import FastAPI, HTTPException
from preprocess import DataProcessor
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

app = FastAPI()

@app.get("/preprocessing")
async def preprocessing():
    try:
        processor = DataProcessor(engine)  # Pass mecabrc_path here
        # processor.preprocess_data()
        processor.preprocess_data(start_date='2023-12-01', end_date='2023-12-01')
        return {"status": "success", "message": "Data processing completed."}
    except Exception as e:
        logging.error(f"An error occurred in the preprocessing route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def home():
    return "Welcome to the preprocess App!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
