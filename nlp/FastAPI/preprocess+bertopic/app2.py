import requests
import streamlit as st
from PIL import Image
import base64
import io
from datetime import date

# URL of your FastAPI application
preprocess_url = "http://0.0.0.0:8002/preprocess"

# 두 개의 열 생성
col1, col2 = st.columns(2)

# 첫 번째 열에 시작 날짜 입력 위젯 배치
with col1:
    start_date = st.date_input('Start date', date.today())

# 두 번째 열에 종료 날짜 입력 위젯 배치
with col2:
    end_date = st.date_input('End date', date.today())

# 날짜 객체를 YYYYMMDD 형식의 문자열로 변환
start_date_str = start_date.strftime("%Y%m%d")
end_date_str = end_date.strftime("%Y%m%d")

# 선택된 날짜 범위 출력
if start_date <= end_date:
    st.success("날짜가 올바르게 입력되었습니다.")
else:
    st.error('Error: End date must fall after start date.')

# Example of making a get request to your FastAPI app (modify as needed)
response = requests.get(preprocess_url, params={"start_date": start_date_str, "end_date": end_date_str})
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
