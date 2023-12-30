
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def get_text(element, tag):
    target = element.find(tag)
    return target.text if target is not None else None

def add_crawling(link_url):
    if not link_url:
        return {}
    response = requests.get(link_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        English_title = soup.select_one('#thesisEqualTitle').get_text(strip=True) if soup.select_one('#thesisEqualTitle') else None
        summary = soup.select_one('div.abstractTxt').get_text(strip=True) if soup.select_one('div.abstractTxt') else None
        keywords = [kw.get_text(strip=True) for kw in soup.select('div.keywordWrap')] if soup.select('div.keywordWrap') else []
        return {'English_title': English_title, 'summary': summary, 'keywords': keywords}
    return {}

def get_api():
    api_key = api_key  # dbpia의 apikey로 수정할 것
    base_url = "https://api.dbpia.co.kr/v2/search/search.xml"
    keyword = keyword_combinations[0]  #keyword 조정 필요
    #category 구분 검토 필요(?) 일단 2번은 사회과학(&category=2), category를 안 적어도 가능. category를 사용자 선택으로?
    url = base_url + f"?key={api_key}&target=se&searchall={keyword}"
    response = requests.get(url)

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        #print(response.content)
        link_data = [get_text(item, 'link_url') for item in root.findall('.//items/item')]

        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(add_crawling, link_data))

        papers_info = []
        for i, item in enumerate(root.findall('.//items/item')):
            result = {
                'title': get_text(item, 'title'),
                'author': [get_text(author, 'name') for author in item.findall('.//authors/author')],
                'publisher': get_text(item, './/publisher/name'),
                'publication': get_text(item, './/publication/name'),
                'issn': get_text(item, './/publication/issn'),
                'issue': get_text(item, './/issue/name'),
                'issue_date': get_text(item, 'issue/yymm'),
                'pages': get_text(item, 'pages'),
                'link': get_text(item, 'link_url'),
                 ** results[i]
            }

            papers_info.append(result)    # 정확도순의 1페이지 결과만 가져옴.

    return papers_info

papers_data = get_api()
print(papers_data)
