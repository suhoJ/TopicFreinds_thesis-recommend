# import requests
# from bs4 import BeautifulSoup
# from concurrent.futures import ThreadPoolExecutor

# def add_crawling(link_url):
#     link_url = link_url.strip("<![CDATA[").strip("]]>")
#     response = requests.get(link_url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         English_title = soup.select_one('div#contents small.eng').get_text(strip=True) if soup.select_one('div#contents small.eng') else None
#         keywords = [kw.get_text(strip=True) for kw in soup.select('#keywd')] if soup.select('#keywd') else []
#         return {'English_title': English_title, 'keywords': keywords}

# def get_text(element, tag, attrs=None):
#     target = element.find(tag, attrs)
#     return target.text if target is not None else ''

# def get_api(keyword_combinations):
#     api_key = "your_api_key"  # Replace with your actual API key
#     final_results = []

#     for keyword in keyword_combinations:
#         url = f"https://open.kci.go.kr/po/openapi/openApiSearch.kci?apiCode=articleSearch&key={api_key}&title={keyword}"
#         response = requests.get(url)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, 'lxml')
#             articles = soup.find_all('articleinfo')

#             link_data = [get_text(article, 'url') for article in articles]
#             with ThreadPoolExecutor(max_workers=20) as executor:
#                 crawled_data = list(executor.map(add_crawling, link_data))

#             for article, crawled in zip(articles, crawled_data):
#                 title = get_text(article, 'article-title')
#                 author = [get_text(author, 'author') for author in article.find_all('author')]
#                 publisher = get_text(article.find('journalinfo'), 'publisher-name')
#                 publication = get_text(article.find('journalinfo'), 'journal-name')
#                 journal_name = get_text(article.find('journalinfo'), 'journal-name')
#                 issn = get_text(article.find('journalinfo'), 'issn')
#                 issue = get_text(article.find('journalinfo'), 'issue')
#                 issue_date = get_text(article.find('journalinfo'), 'pub-year') + '-' + get_text(article.find('journalinfo'), 'pub-mon')
#                 pages = get_text(article, 'fpage') + '-' + get_text(article, 'lpage')
#                 link = get_text(article, 'url')
#                 English_title = crawled.get('English_title')
#                 abstract = get_text(article.find('abstract-group'), 'abstract', {'lang': 'original'}) + ' ' + get_text(article.find('abstract-group'), 'abstract', {'lang': 'english'})
#                 keywords = crawled.get('keywords')

#                 final_results.append({
#                     'title': title,
#                     'author': author,
#                     'publisher': publisher,
#                     'publication': publication,
#                     'journal_name': journal_name,
#                     'issn': issn,
#                     'issue': issue,
#                     'issue_date': issue_date,
#                     'pages': pages,
#                     'link': link,
#                     'English_title': English_title,
#                     'abstract': abstract,
#                     'keywords': keywords
#                 })

#     return final_results

# # Example usage:
# # print(get_api(['example_keyword']))

from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer

class CategoryBERTopicModeler:
    def __init__(self, tokenizer, max_features=3000):
        self.vectorizer = CountVectorizer(tokenizer=tokenizer, max_features=max_features)
        self.ctfidf_model = ClassTfidfTransformer()

    def fit_model(self, docs, embedding_model="sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens"):
        topic_model = BERTopic(embedding_model=embedding_model,
                               vectorizer_model=self.vectorizer,
                               ctfidf_model=self.ctfidf_model,
                               top_n_words=5,
                               min_topic_size=30,
                               nr_topics="auto",
                               verbose=True)
        topics, _ = topic_model.fit_transform(docs)
        return topic_model

def apply_category_models(df, tokenizer):
    modeler = CategoryBERTopicModeler(tokenizer)
    category_models = {}

    for category in df['category'].unique():
        category_docs = df[df['category'] == category]['tokenized_text_mc']
        model = modeler.fit_model(category_docs)
        category_models[category] = model

        # 각 카테고리별 주요 키워드 추출
        topic_info = model.get_topic_info()
        top_topics = topic_info[topic_info['Name'] != '-1']  # -1은 노이즈를 나타내므로 제외
        keywords = ["; ".join(model.get_topic(topic)[0]) for topic in top_topics['Topic']]
        category_keywords[category] = keywords
        
    return category_models, category_keywords
