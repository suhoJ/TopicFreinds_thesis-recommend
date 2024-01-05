from bs4 import BeautifulSoup
import requests
import time
import csv
import os
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import sqlite3
import logging
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

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

def create_db():
    dbpath = "news_data.db"
    conn = sqlite3.connect(dbpath)
    conn.execute('PRAGMA journal_mode=WAL;')  # Write-Ahead Logging을 활성화
    conn.execute('PRAGMA synchronous=NORMAL;') # 동기화 설정을 변경
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS news_crawl(                         
      date TEXT,
      category TEXT,
      press TEXT,
      title TEXT,                            -- 제목
      document TEXT,                         --
      link TEXT,                           -- 링크
      uuid TEXT                            -- 링크
    );
    """)
    conn.commit()
    return conn

def insert_article(article, conn):
    cur = conn.cursor()
    article_uuid = str(uuid.uuid4())
    # Check if the article already exists
    cur.execute("SELECT 1 FROM news_crawl WHERE link = ?", (article['link'],))
    if cur.fetchone():
        # Article already exists, skip insertion
        return
    try:
        cur.execute("""
                INSERT INTO news_crawl (date, category, press, title, document, link, uuid)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
        article['date'],
        article['category'],
        article['press'],
        article['title'],
        article['document'],
        article['link'],
        article_uuid))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Exception in insert_article: {e}")

def news_crawler(start_date, end_date, max_page, conn=None):
    all_articles = []
    original_start_date = start_date

    for category_num, subcategories in categories.items():
        category = category_mapping.get(category_num)
        for subcategory in subcategories:
            current_date = original_start_date

            while current_date <= end_date:
                page_num = 1
                is_last_page = False  # 페이지의 끝
                last_title = None  # 마지막으로 크롤링된 기사의 제목
                last_press = None  # 마지막으로 크롤링된 기사의 언론사

                while not is_last_page and page_num <= max_page:
                    response = requests.get(f"https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1={category_num}&sid2={subcategory}&date={current_date}&page={page_num}", headers=headers)
                    soup = BeautifulSoup(response.content, "html.parser")
                    # time.sleep(2)

                    articles = soup.select(".list_body.newsflash_body > ul > li")
                    # 기사가 없으면 중단
                    if not articles:
                        break

                    # 첫 번째 기사의 제목과 언론사
                    first_article = articles[0]
                    first_title = first_article.select_one("dt:not(.photo) > a").text.strip()
                    first_press = first_article.select_one("span.writing").text.strip()

                    # 이전 페이지의 첫 번째 기사와 동일하다면 마지막 페이지로 간주하고 중단
                    if first_title == last_title and first_press == last_press:
                        break

                    # 각 기사의 페이지 링크 추출
                    links = [article.select_one("dt:not(.photo) > a")['href'] for article in articles]
                    print(links)
                    link_data = [(link, category) for link in links]

                    # 각 링크에 대한 데이터 추출(멀티스레딩)
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        results = list(executor.map(extract_article, link_data))
                        all_articles.extend(results)

                        for result in results:
                            print(result)

                    # 페이지 번호 업데이트
                    last_title = first_title  # 이번 페이지의 첫 번째 기사 제목을 저장
                    last_press = first_press  # 이번 페이지의 첫 번째 기사 언론사를 저장
                    page_num += 1
                    # time.sleep(3)

                current_date += 1  # 다음 날짜로 이동

    return all_articles

def extract_article(data):
    link, category = data
    try:
        response = requests.get(link, headers=headers)
        article_soup = BeautifulSoup(response.content, "html.parser")
        # time.sleep(3)
        # 날짜 추출
        date = article_soup.select_one("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")
        date = date.get_text(strip=True)
        # 언론사 추출
        press = article_soup.find("em", class_="media_end_linked_more_point").get_text(strip=True)
        # 제목 추출
        title = article_soup.select_one("#title_area").get_text(strip=True)
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
                'link': link,
                'uuid': str(uuid.uuid4())
            }
            conn = sqlite3.connect('../news_data.db')
            insert_article(article_data, conn)
            return article_data
    except Exception as e:
            return {"link": link, "error": str(e)}
    finally:
          conn.close()

def start_crawling(start_date, end_date, max_page):
    start_time = time.time()
    try:
        conn = create_db()
        articles = news_crawler(20231207, 20231207, max_page=1, conn=conn) #기사 링크 목록 가져오기
        end_time = time.time()  # 크롤링 종료 시간 기록
        print(f"크롤링 완료. 소요 시간: {end_time - start_time}초")
        print(f"{len(articles)} articles saved")
    except Exception as e:
        logging.error(f"An error occurred: {e}")



