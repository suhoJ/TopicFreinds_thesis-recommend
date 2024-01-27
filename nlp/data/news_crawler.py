from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import time
import re
import logging
import requests
import mysql.connector

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_db():
    db_config = {
        'host': 'host',
        'user': 'user',
        'password': 'pass',
        'database': 'database'
    }
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS news_crawl(
      date TEXT,
      category TEXT,
      press TEXT,
      title TEXT,
      document TEXT,
      link TEXT
    );
    """)
    conn.commit()
    return conn

def insert_article(article, conn):
    cur = conn.cursor()
    try:
        # Use %s instead of ? for MySQL
        cur.execute("SELECT 1 FROM news_crawl WHERE link = %s", (article['link'],))
        if cur.fetchone():
            return  # Article already exists, skip insertion

        # Use %s instead of ? for MySQL
        cur.execute("""
                INSERT INTO news_crawl (date, category, press, title, document, link)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
        article['date'],
        article['category'],
        article['press'],
        article['title'],
        article['document'],
        article['link']))
        conn.commit()
    except mysql.connector.Error as e:  # Handle MySQL exceptions
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Exception in insert_article: {e}")
    finally:
        cur.close()  # Close the cursor

category_mapping = {
    100 : "Politics",
    101 : "Economy",
    102 : "Society",
    103 : "Life-Culture",
    104 : "World",
    105 : "IT-Science"
}

categories = {
    100 : [264, 265, 266, 267, 268, 269],
    101 : [258, 259, 260, 261, 263, 771],
    102 : [249, 250, 251, 252, 254, 255, 256, 257],
    103 : [237, 238, 239, 376, 240, 241, 242, 243, 244, 245, 248],
    104 : [231, 232, 233, 234, 322],
    105 : [226, 227, 228, 229, 230, 731, 732, 283]
}

def news_crawler(start_date, end_date, conn):
    all_articles = []
    original_start_date = start_date

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.page_load_strategy = 'eager'
    options.add_argument("--log-level=3")
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)

    for category_num, subcategories in categories.items():
        category = category_mapping.get(category_num)
        for subcategory in subcategories:
            current_date = original_start_date

            while current_date <= end_date:
                browser.get(f"https://news.naver.com/breakingnews/section/{category_num}/{subcategory}?date={current_date}")
                soup = BeautifulSoup(browser.page_source, "html.parser")
                time.sleep(3)
                # 웹페이지에 들어왔으면, "기사 더보기" 클릭 ("기사 더보기" 버튼이 안보일 때까지)
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
                link_data = [(link, category, conn) for link in links]

                # 각 링크에 대한 데이터 추출(멀티스레딩)
                with ThreadPoolExecutor(max_workers=100) as executor:
                    results = list(executor.map(extract_article, link_data))

                all_articles.extend(results)

                for result in results:
                    print(result)

                current_date += 1  # 다음 날짜로 이동

    browser.quit()
    return all_articles

def extract_article(link_data):
    link, category, conn = link_data
    try:
        response = requests.get(link)
        article_soup = BeautifulSoup(response.content, "html.parser")
        # time.sleep(3)
        # 날짜 추출
        date = article_soup.select_one("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")
        date = date.get_text(strip=True)
        # 언론사 추출
        press = article_soup.find("em", class_="media_end_linked_more_point").get_text(strip=True)
        # 제목 추출
        title = article_soup.select_one("#title_area").get_text(strip=True)
        # 이미지 추출
        # image = article_soup.find('img', id='img1')['src']
        # 본문 추출
        content_raw = article_soup.select_one("article#dic_area") or article_soup.select_one("div#articleBody")
        if content_raw:
            #불필요한 태그 제거
            tags_to_remove = content_raw.select("div[style], em.img_desc, em[style], table.nbd_table, span.end_photo_org, div.vod_player_wrap, span.byline_s")
            for tag in tags_to_remove:
                tag.decompose()
            content = content_raw.get_text(strip=True)
            pattern = r"[\[\(][^)\]]*[\]\)]"
            content = re.sub(pattern, "", content).replace(". ", ".").replace(".", ". ")
            content = content.replace("\n", "")
            content = content.replace("// flash 오류를 우회하기 위한 함수 추가function _flash_removeCallback() {}", "")
            content = content.replace("동영상 뉴스       ", "")
            content = content.replace("동영상 뉴스", "")
            content = content.strip()

            article_data = {
                'date': date,
                'category': category,
                'press': press,
                'title': title,
                'document': content,
                'link': link
            }
            insert_article(article_data, conn)
            return article_data
    except Exception as e:
            return {"link": link, "error": str(e)}
    finally:
           conn.close()

def start_crawling(start_date, end_date):
    start_time = time.time()
    try:
        conn = create_db()
        articles = news_crawler(start_date, end_date, conn) 
        end_time = time.time() 
        print(f"크롤링 완료. 소요 시간: {end_time - start_time}초")
        print(f"{len(articles)} articles saved")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

# if __name__ == "__main__":
#     start_crawling(20231201, 20231201)
