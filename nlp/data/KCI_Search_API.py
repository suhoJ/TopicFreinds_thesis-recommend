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
    target = element.find(tag, attrs)
    return target.text if target is not None else ''

def get_api():
    api_key = api_key
    keyword = keyword_combinations[0]  #keyword 조정 필요
    url = f"https://open.kci.go.kr/po/openapi/openApiSearch.kci?apiCode=articleSearch&key={api_key}&title={keyword}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')  
        # print(soup.prettify())
        articles = soup.find_all('articleinfo')
        link_data = [get_text(article, 'url') for article in articles]
        # print(link_data)

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(add_crawling, link_data)

        final_results = []

        for article in articles:
            title = get_text(article, 'article-title')
            author = [get_text(author, 'author') for author in article.find_all('author')]
            publisher = get_text(soup.find('journalinfo'), 'publisher-name')
            publication = get_text(soup.find('journalinfo'), 'journal-name')
            journal_name = get_text(soup.find('journalinfo'), 'journal-name')
            issn = None
            issue = get_text(soup.find('journalinfo'), 'issue')
            issue_date = get_text(soup.find('journalinfo'), 'pub-year') + '-' + get_text(soup.find('journalinfo'), 'pub-mon')
            pages = get_text(article, 'fpage')
            link = get_text(article, 'url')
            English_title = add_crawling(link).get('English_title', None)
            abstract = get_text(article.find('abstract-group'), 'abstract', {'lang': 'original'}) + ' ' + get_text(article.find('abstract-group'), 'abstract', {'lang': 'english'})
            keywords = add_crawling(link).get('keywords', None)

            final_results.append({
                'title': title,
                'author': author,
                'publisher': publisher,
                'publication': publication,
                'journal_name': journal_name,
                'issn': issn,
                'issue': issue,
                'issue_date': issue_date,
                'pages': pages,
                'link': link,
                'English_title': English_title,
                'abstract': abstract,
                'keywords': keywords
            })

        return final_results

print(get_api())