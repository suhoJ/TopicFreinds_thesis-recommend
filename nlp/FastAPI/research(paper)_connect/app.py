import streamlit as st
from PIL import Image
import requests

# 이미지 불러오기
logo = Image.open('./fastapi/banner_image.png').convert("RGB")  # 파일 위치 수정 필요
logo = logo.resize((130, 80))
def image_to_base64(image):
    import base64
    import io
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return base64.b64encode(buffer.getvalue()).decode()

# HTML을 이용한 이미지 위치 조정
st.markdown(
    """
    <style>
    .reportview-container {
        flex-direction: row;
        justify-content: center;
    }
    .logo {
        position: relative;
        top: 0px;  # 상단 여백 조정
        left: 10px;  # 왼쪽 여백 조정
    }
    .logo img {
        max-width: 100%;
        height: auto;
    }
    .main {
        flex: 1;
        max-width: 800px;
    </style>
    """,
    unsafe_allow_html=True
)

# 이미지 넣기
st.markdown(
    """
    <div class="logo">
        <img src="data:image/jpg;base64,{}">
    </div>
    """.format(image_to_base64(logo)),
    unsafe_allow_html=True
)

# FastAPI 엔드포인트 URL
FASTAPI_ENDPOINT = "http://127.0.0.1:8000/search_papers"  # 각자 주소에 맞게 수정

# 검색창
search_term = st.text_input('논문 검색어를 입력하세요')

# FastAPI 엔드포인트에서 데이터를 가져오는 함수
def get_search_results(search_term):
    response = requests.get(FASTAPI_ENDPOINT, params={"search_term": search_term})
    if response.status_code == 200:
        return response.json()
    else:
        st.error('검색 중 오류가 발생했습니다.')
        return []

st.title('Topic Keywords')


# 사용자가 검색어를 입력하면 결과를 표시
if search_term:
    search_results = get_search_results(search_term)
    st.write('검색 결과:')
    for result in search_results:
        st.write(result)
