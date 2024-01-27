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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_db():
    db_config = {
        'host': "localhost",
        'user': "root",
        'password': "password",
        'database': "news_db"
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

def insert_article(article):
    db_config = {
        'host': "localhost",
        'user': "root",
        'password': "password",
        'database': "news_db"
    }
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()

    try:
        cur.execute("SELECT 1 FROM news_crawl WHERE link = %s", (article['link'],))
        if cur.fetchone():
            return  # Article already exists, skip insertion

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
        conn.close()

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
                # If on the webpage, click the "Read More" button until it's no longer visible
                while True:
                    try:
                        browser.find_element(By.CSS_SELECTOR, "div.section_more > a").click()
                        time.sleep(0.5)

                        # Parse the updated page source into a BeautifulSoup object
                        soup = BeautifulSoup(browser.page_source, "html.parser")

                    except:  # If the "Read More" button is not visible, an error will be thrown,
                        # Scroll to the bottom of the page
                        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(0.3)
                        break  

                articles = soup.select("div.sa_text")
                # Stop if there are no articles
                if not articles:
                    break

                # Extract links for each article
                links = [article.select_one("div.sa_text > a")['href'] for article in articles]
                # print(links)
                link_data = [(link, category, conn) for link in links]

                # Extract data for each link (multithreading)
                with ThreadPoolExecutor(max_workers=100) as executor:
                    results = list(executor.map(extract_article, link_data))

                all_articles.extend(results)

                for result in results:
                    print(result)

                current_date += 1  # Move to the next date

    browser.quit()
    return all_articles

def extract_article(link_data):
    link, category, conn = link_data
    try:
        response = requests.get(link)
        article_soup = BeautifulSoup(response.content, "html.parser")
        # time.sleep(3)
        # Extract date
        date = article_soup.select_one("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")
        date = date.get_text(strip=True)
        # Extract press
        press = article_soup.find("em", class_="media_end_linked_more_point").get_text(strip=True)
        # Extract title
        title = article_soup.select_one("#title_area").get_text(strip=True)
        # Extract content
        content_raw = article_soup.select_one("article#dic_area") or article_soup.select_one("div#articleBody")
        if content_raw:
            # Remove unnecessary tags
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
            insert_article(article_data)
            return article_data
    except Exception as e:
            return {"link": link, "error": str(e)}

def start_crawling(start_date, end_date):
    start_time = time.time()
    try:
        conn = create_db()
        articles = news_crawler(start_date, end_date, conn) 
        end_time = time.time()  
        print(f"Finish crawling : {end_time - start_time}초")
        print(f"{len(articles)} articles saved")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

# if __name__ == "__main__":
#     start_crawling(20231201, 20231201)
