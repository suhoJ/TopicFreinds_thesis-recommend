import requests
import urllib
import pandas as pd
from bs4 import BeautifulSoup

def get_data_for_keyword(keyword, api_key='18556060', display_count=100):
    search_word_encoded = urllib.parse.quote_plus(keyword)
    url = f'https://open.kci.go.kr/po/openapi/openApiSearch.kci?apiCode=articleSearch&key={api_key}&keyword={search_word_encoded}&displayCount={display_count}'

    response = requests.get(url, verify=False)  # 'verify=False' may raise security warnings
    if response.status_code != 200:
        print(f"Error occurred while fetching data for keyword '{keyword}': {response.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, 'lxml-xml')
    articles = soup.find_all('record')

    data = []
    for article in articles:
        journal_info = article.find('journalInfo')
        article_info = article.find('articleInfo')

        title = article_info.find('article-title').text if article_info.find('article-title') else None
        authors = [author.text for author in article_info.find_all('author')] if article_info.find('author') else []
        publisher = journal_info.find('publisher-name').text if journal_info.find('publisher-name') else None
        issue = journal_info.find('issue').text if journal_info.find('issue') else None
        pub_year = journal_info.find('pub-year').text if journal_info.find('pub-year') else None
        pub_mon = journal_info.find('pub-mon').text if journal_info.find('pub-mon') else None
        issue_date = f"{pub_year}-{pub_mon}" if pub_year and pub_mon else None
        pages = f"{article_info.find('fpage').text}-{article_info.find('lpage').text}" if article_info.find('fpage') and article_info.find('lpage') else None
        abstract = article_info.find('abstract').text if article_info.find('abstract') else None
        link = article_info.find('url').text if article_info.find('url') else None
        # keywords extraction is not shown in the given example. You might need to adjust this part based on the actual XML structure.
        
        data.append({
            'keyword': keyword,
            'title': title,
            'link': link,
            'authors': ", ".join(authors),
            'publisher': publisher,
            'issue': issue,
            'issue_date': issue_date,
            'pages': pages,
            'abstract': abstract,
            # Assuming 'keywords' field to be handled separately as it's not shown in the example
            # 'keywords': keywords
        })

    return pd.DataFrame(data)
