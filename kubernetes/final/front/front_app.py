
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from PIL import Image


# Database connection settings
DATABASE_TYPE = 'mysql'
DBAPI = 'mysqlconnector'
HOST = 'thesis-mysql.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com'
USER = 'goorm'
PASSWORD = 'goorm1415'
DATABASE = 'mydatabase'

# SQLAlchemy engine creation
DATABASE_URI = f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
engine = create_engine(DATABASE_URI)

def fetch_categories():
    query = "SELECT DISTINCT category FROM news"
    with engine.connect() as connection:
        result = pd.read_sql_query(query, connection)
    return result['category'].tolist()

def fetch_keywords():
    query = "SELECT DISTINCT keyword FROM thesis_data"  # Adjust if your keywords are stored elsewhere
    with engine.connect() as connection:
        result = pd.read_sql_query(query, connection)
    return result['keyword'].tolist()


def fetch_news_titles(selected_categories):
    if not selected_categories:
        return pd.DataFrame()  # Return an empty DataFrame if no categories are selected
    category_placeholders = ', '.join(['%s'] * len(selected_categories))
    query = f"""
    SELECT title, link FROM news
    WHERE category IN ({category_placeholders})
    """
    with engine.connect() as connection:
        result = pd.read_sql_query(query, connection, params=tuple(selected_categories))
    return result

def fetch_thesis_titles(selected_keywords):
    if not selected_keywords:
        return pd.DataFrame()  # Return an empty DataFrame if no keywords are selected
    keyword_placeholders = ', '.join(['%s'] * len(selected_keywords))
    query = f"""
    SELECT title, link FROM thesis_data
    WHERE keyword IN ({keyword_placeholders})
    """
    with engine.connect() as connection:
        result = pd.read_sql_query(query, connection, params=tuple(selected_keywords))
    return result

# App UI

# 이미지 불러오기
logo = Image.open('banner_image.png').convert("RGB")  # 파일 위치 수정 필
logo = logo.resize((130, 80))
def image_to_base64(image):
    import base64
    import io
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return base64.b64encode(buffer.getvalue()).decode()

# # HTML을 이용한 이미지 위치 조정
# st.markdown(
#     """
#     <style>
#     .reportview-container {
#         flex-direction: row;
#         justify-content: center;
#     }
#     .logo {
#         position: relative;
#         top: 0px;  # 상단 여백 조정
#         left: 10px;  # 왼쪽 여백 조정
#     }
#     .logo img {
#         max-width: 100%;
#         height: auto;
#     }
#     .main {
#         flex: 1;
#         max-width: 800px;
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# 이미지 넣기
st.markdown(
    """
    <div class="logo">
        <img src="data:image/jpg;base64,{}">
    </div>
    """.format(image_to_base64(logo)),
    unsafe_allow_html=True
)
# 검색창
st.title('Topic Friends')
search_term = st.text_input('논문 검색어를 입력하세요')

st.title('News & Thesis')

# Category selection for news using checkboxes
categories = fetch_categories()
st.write("Select category(ies):")
selected_categories = []
cols = st.columns(3)  # Adjust based on UI needs or the number of categories
for index, category in enumerate(categories):
    col = cols[index % 3]  # This will distribute checkboxes across the columns
    if col.checkbox(category, key=f"category_{category}"):
        selected_categories.append(category)

# Keyword selection for thesis_data
keywords = fetch_keywords()
selected_keywords = st.multiselect('Select keyword(s):', keywords)

# Display titles and links from both tables side by side
if st.button('Show Data'):
    col1, col2 = st.columns(2)  # Create two columns

    # Display news titles in the first column based on selected categories
    if selected_categories:
        news_data = fetch_news_titles(selected_categories)
        with col1:
            st.write("**News Titles:**")
            if not news_data.empty:
                for _, row in news_data.iterrows():
                    st.markdown(f"[{row['title']}]({row['link']})", unsafe_allow_html=True)
            else:
                st.write("No news data found for the selected category(ies).")

    # Display thesis titles in the second column based on selected keywords
    if selected_keywords:
        thesis_data = fetch_thesis_titles(selected_keywords)
        with col2:
            st.write("**Thesis Titles:**")
            if not thesis_data.empty:
                for _, row in thesis_data.iterrows():
                    st.markdown(f"[{row['title']}]({row['link']})", unsafe_allow_html=True)
            else:
                st.write("No thesis data found for the selected keywords.")

