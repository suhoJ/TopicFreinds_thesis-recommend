# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def add_crawling(link_url):
    link_url = link_url.strip("<![CDATA[").strip("]]>")
    response = requests.get(link_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        English_title = soup.select_one('div#contents small.eng').get_text(strip=True) if soup.select_one('div#contents small.eng') else None
        keywords = [kw.get_text(strip=True) for kw in soup.select('#keywd')] if soup.select('#keywd') else []
        return {'English_title': English_title, 'keywords': keywords}

def get_text(element, tag, attrs=None):
    if attrs is None:
        attrs = {}
    if element:
        target = element.find(tag, attrs)
        return target.text.strip() if target else ''
    return ''

def get_api(keyword):
    api_key = api_key #api key
    keyword = keyword
    url = f"https://open.kci.go.kr/po/openapi/openApiSearch.kci?apiCode=articleSearch&key={api_key}&title={keyword}"
    response = requests.get(url)
    if response.status_code == 200:
        # data = response.json()
        # total_records = data['response']['total']
        soup = BeautifulSoup(response.content, 'lxml-xml')
        # print(soup.prettify())
        articles = soup.find_all('record')
        link_data = [get_text(article, 'url') for article in articles]
        # print(link_data)

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(add_crawling, link_data)

        final_results = []

        for article in articles:
            title = get_text(article, 'article-title')
            author = [author.text.strip() for author in article.find_all('author')]
            publisher = get_text(article.find('journalInfo'), 'publisher-name')
            # publication = get_text(soup.find('journalinfo'), 'journal-name')
            issue = get_text(article.find('journalInfo'), 'issue')
            issue_date = get_text(article.find('journalInfo'), 'pub-year') + '-' + get_text(soup.find('journalInfo'), 'pub-mon')
            pages = get_text(article, 'fpage')
            link = get_text(article, 'url')
            English_title = add_crawling(link).get('English_title', None)
            abstract = get_text(article.find('abstract-group'), 'abstract', {'lang': 'original'})
            keywords = add_crawling(link).get('keywords', None)

            final_results.append({
                'title': title,
                'author': author,
                'publisher': publisher,
                # 'publication': publication,
                'issue': issue,
                'issue_date': issue_date,
                'pages': pages,
                'link': link,
                'English_title': English_title,
                'abstract': abstract,
                'keywords': keywords
            })

        return final_results
    else:
        print(f"Error 발생: {response.status_code} - {response.text}")  # 예외 전처리
        return []

# print(get_api("딥러닝"))
