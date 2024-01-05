import logging
from flask import Flask, jsonify
from news_crawler import start_crawling
from preprocess import DataProcessor
from bertopic_model import TopicModeler
from KCI_Search_API import get_api
import pandas as pd

app = Flask(__name__)

@app.route('/start-crawling', methods=['GET'])
def crawling():
    try:
        start_crawling(20231207, 20231207, max_page=1)
        return jsonify({"status": "success", "message": "News crawling started."})
    except Exception as e:
        logging.error(f"An error occurred in start_crawling: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/preprocessing', methods=['GET'])
def preprocessing():
    try:
        processor = DataProcessor('news_data.db')
        processor.preprocess_data()
        return jsonify({"status": "success", "message": "Data processing completed."})
    except Exception as e:
        logging.error(f"An error occurred in the modeling route: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/modeling', methods=['GET'])
def modeling():
    try:
        df = pd.read_sql('SELECT * FROM preprocessed_news_data', 'sqlite:///news_data.db')
        topic_modeler = TopicModeler(topic_number=10, topn=5, data=df)
        keyword_combinations = topic_modeler.analyze_topics(df)
        get_api(keyword_combinations)
        return jsonify({"status": "success", "message": "Topic modeling completed."})
    except Exception as e:
        logging.error(f"An error occurred in the modeling route: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def home():
    return "Welcome to the News Crawler App!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


