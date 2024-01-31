from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import time
import re
import logging
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from concurrent.futures import ThreadPoolExecutor

# MySQL RDS credentials
db_username = "goorm"
db_password = "goorm1415"
db_host = "thesis-mysql.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com"
db_name = "mydatabase"
mysql_connection_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}"

# Create a database engine
engine = create_engine(mysql_connection_string)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# User-Agent for HTTP requests
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

# Category mapping and configuration
category_mapping = {
    # 100 : "Politics",
    # 101 : "Economy",
    # 102 : "Society",
    # 103 : "Life-Culture",
    # 104 : "World",
    105 : "IT-Science"
}
categories = {
    # 100 : [264, 265, 266, 267, 268, 269],
    # 101 : [258, 259, 260, 261, 263, 771],
    # 102 : [249, 250, 251, 252, 254, 255, 256, 257],
    # 103 : [237, 238, 239, 376, 240, 241, 242, 243, 244, 245, 248],
    # 104 : [231, 232, 233, 234, 322],
    # 105 : [226, 227, 228, 229, 230, 731, 732, 283]
    105 : [227]
}

def create_db(engine):
    try:
        with engine.connect() as conn:
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS news_crawl(
                    date TEXT,
                    category TEXT,
                    press TEXT,
                    title TEXT,
                    document TEXT,
                    link VARCHAR(255) PRIMARY KEY
                );
            """)
            conn.execute(create_table_query)
    except SQLAlchemyError as e:
        logging.error(f"Error creating the table: {e}")


# def insert_article(article, engine):
#     with engine.connect() as conn:
#         try:
#             result = conn.execute(text("SELECT 1 FROM news_crawl WHERE link = :link"), {'link': article['link']})
#             if result.fetchone():
#                 logging.info(f"Article already exists: {article['title']}")
#                 return

#             conn.execute(text("""
#                 INSERT INTO news_crawl (date, category, press, title, document, link)
#                 VALUES (:date, :category, :press, :title, :document, :link)
#             """), article)

#             logging.info(f"Article inserted: {article['title']}")
#         except SQLAlchemyError as e:
#             logging.error(f"Error in insert_article: {e}")
def insert_article(article, engine):
    with engine.connect() as conn:
        try:
            # Check if the article with the same link already exists
            result = conn.execute(text("SELECT 1 FROM news_crawl WHERE link = :link"), {'link': article['link']})
            if result.fetchone():
                logging.info(f"Article already exists: {article['title']}")
                return

            # Insert the article data into the database
            conn.execute(text("""
                INSERT INTO news_crawl (date, category, press, title, document, link)
                VALUES (:date, :category, :press, :title, :document, :link)
            """), article)

            # Commit the transaction to ensure data is saved
            conn.commit()

            logging.info(f"Article inserted: {article['title']}")
        except SQLAlchemyError as e:
            # Log the error and roll back the transaction if an exception occurs
            logging.error(f"Error in insert_article: {e}")
            conn.rollback()

def news_crawler(start_date, end_date):
    all_articles = []
    original_start_date = start_date

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.page_load_strategy = 'eager'
    options.add_argument("--log-level=3")
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)

    for category_num, subcategories in categories.items():
        category = category_mapping.get(category_num)
        for subcategory in subcategories:
            current_date = original_start_date

            while current_date <= end_date:
                logging.info(f"Crawling category {category}, subcategory {subcategory}, date {current_date}")
                # URL needs to be defined based on the website structure
                url = f"https://news.naver.com/breakingnews/section/{category_num}/{subcategory}?date={str(current_date)}"
                # url = f"https://example.com/news/{category}/{subcategory}?date={str(current_date)}"
                logging.info(f"URL constructed: {url}")

                browser.get(url)
                soup = BeautifulSoup(browser.page_source, "html.parser")
                time.sleep(3)
                
                while True:
                    try:
                        browser.find_element(By.CSS_SELECTOR, "div.section_more > a").click()
                        time.sleep(0.5)

                        # 업데이트된 페이지 소스를 soup 객체로 파싱
                        soup = BeautifulSoup(browser.page_source, "html.parser")

                    except:  # "기사 더보기" 버튼이 안보이면, 위 문장에서 에러가 나므로,
                        # 페이지 끝까지 스크롤
                        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(0.3)
                        break  # 반복문 탈출

                articles = soup.select("div.sa_text")
                # 기사가 없으면 중단
                if not articles:
                    break


                # 각 기사의 페이지링크 추출
                links = [article.select_one("div.sa_text > a")['href'] for article in articles]
                # print(links)
                link_data = [(link, category) for link in links]

                # 각 링크에 대한 데이터 추출(멀티스레딩)
                with ThreadPoolExecutor(max_workers=100) as executor:
                    results = list(executor.map(extract_article, link_data))

                all_articles.extend(results)

                for result in results:
                    print(result)

                current_date += 1  # 다음 날짜로 이동

    browser.quit()
    return all_articles

# def extract_article(data):
#     link, category = data
#     try:
#         response = requests.get(link, headers=headers)
#         article_soup = BeautifulSoup(response.content, "html.parser")
        
#         # Extraction logic based on the website's HTML structure
#         date = article_soup.select_one("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME").get_text(strip=True)
#         press = article_soup.select_one("your_press_selector").get_text(strip=True)
#         title = article_soup.select_one("your_title_selector").get_text(strip=True)
#         content_raw = article_soup.select_one("your_content_selector")

#         if content_raw:
#             # Cleaning and processing the content
#             content = content_raw.get_text(strip=True)

#             article_data = {
#                 'date': date,
#                 'category': category,
#                 'press': press,
#                 'title': title,
#                 'document': content,
#                 'link': link,
#                 'uuid': str(uuid.uuid4())
#             }

#             insert_article(article_data, engine)
#             return article_data

#     except Exception as e:
#         logging.error(f"Error in extract_article: {e}")
#         return {"link": link, "error": str(e)}
def extract_article(link_data):
    link, category = link_data
    try:
        response = requests.get(link)
        article_soup = BeautifulSoup(response.content, "html.parser")

        # Extract date
        date_element = article_soup.select_one("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")
        date = date_element.get_text(strip=True) if date_element else None

        # Extract press
        press_element = article_soup.find("em", class_="media_end_linked_more_point")
        press = press_element.get_text(strip=True) if press_element else None

        # Extract title
        title_element = article_soup.select_one("#title_area")
        title = title_element.get_text(strip=True) if title_element else None

        # Extract content
        content_raw = article_soup.select_one("article#dic_area") or article_soup.select_one("div#articleBody")
        if content_raw:
            # Remove unnecessary tags
            tags_to_remove = content_raw.select("div[style], em.img_desc, em[style], table.nbd_table, span.end_photo_org, div.vod_player_wrap, span.byline_s")
            for tag in tags_to_remove:
                tag.decompose()
            content = content_raw.get_text(strip=True)
            content = re.sub(r"[\[\(][^)\]]*[\]\)]", "", content).replace(". ", ".").replace(".", ". ")
            content = content.replace("\n", "").replace("// flash 오류를 우회하기 위한 함수 추가function _flash_removeCallback() {}", "")
            content = content.replace("동영상 뉴스       ", "").replace("동영상 뉴스", "").strip()

            article_data = {
                'date': date,
                'category': category,
                'press': press,
                'title': title,
                'document': content,
                'link': link
            }
            insert_article(article_data, engine)
            return article_data
        
    except Exception as e:
        return {"link": link, "error": str(e)}



def start_crawling(start_date, end_date):
    logging.info(f"Starting crawling from {start_date} to {end_date}")
    start_time = time.time()
    try:
        create_db(engine)
        articles = news_crawler(start_date, end_date)
        end_time = time.time()
        logging.info(f"Crawling completed. Time taken: {end_time - start_time} seconds")
        logging.info(f"{len(articles)} articles saved")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

# if __name__ == "__main__":
#     start_crawling(20231201, 20231202)  # Example start and end dates
