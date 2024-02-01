import requests
import streamlit as st
from PIL import Image
import base64
import io

# URL of your FastAPI application
preprocess_url = "http://0.0.0.0:8002/preprocess"

# Example of making a POST request to your FastAPI app (modify as needed)
response = requests.post(preprocess_url, json=[{"text": "text", "category": "category"}])  # 이 부분 수정 필요할 수 있음.
if response.status_code == 200:
    data = response.json()
    for category, details in data.items():
        st.header(f"Category: {category}")

        # Display top keywords
        top_keywords = details['top_keywords']
        st.subheader("Top Keywords:")
        for topic_number, keyword, weight in top_keywords:
            st.write(f"Topic {topic_number}: {keyword}")

        # Display word cloud
        wordcloud_img = details['wordcloud']
        image = Image.open(io.BytesIO(base64.b64decode(wordcloud_img)))
        st.image(image, caption=f"Word Cloud for {category}")
else:
    st.error("Failed to fetch data from API")
