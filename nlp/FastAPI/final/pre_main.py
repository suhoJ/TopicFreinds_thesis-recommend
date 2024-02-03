from fastapi import FastAPI, HTTPException
from preprocess import DataProcessor
import pandas as pd
import sqlalchemy
import logging
from typing import Optional
from datetime import date

# Update this with your MySQL RDS credentials
db_username = "goorm"
db_password = "goorm1415"
db_host = "thesis-mysql.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com"
db_name = "mydatabase"
mysql_connection_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}"

# Create a database engine
engine = sqlalchemy.create_engine(mysql_connection_string)

app = FastAPI()

processor = DataProcessor(engine)

# @app.get("/preprocessing")
# async def preprocessing():
#     try:
#         processor = DataProcessor(engine)  # Pass mecabrc_path here
#         processor.preprocess_data()
#         return {"status": "success", "message": "Data processing completed."}
#     except Exception as e:
#         logging.error(f"An error occurred in the preprocessing route: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def home():
    return "Welcome to the preprocess App!"

@app.get("/process_dates/")
def process_dates(start_date: Optional[date] = None, end_date: Optional[date] = None):
    if start_date is None or end_date is None:
        raise HTTPException(status_code=400, detail="Start date and end date are required.")

    if end_date < start_date:
        raise HTTPException(status_code=400, detail="End date cannot be earlier than start date.")

    # return {"message": "Valid dates received", "start_date": start_date, "end_date": end_date}
    
    try:
        # Call the preprocess_data method with start_date and end_date
        data_processor = DataProcessor(engine)
        data_processor.preprocess_data(start_date, end_date)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Data processing and insertion completed", "start_date": start_date, "end_date": end_date}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
