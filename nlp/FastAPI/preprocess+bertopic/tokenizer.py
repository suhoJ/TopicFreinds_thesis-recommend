class DataProcessor:
    def __init__(self, tagger, engine, n=2):
        self.engine = engine
        self.n = n
        self.tagger = tagger
        self.preprocessed_news_data = None
        self.stopwords = ['에게', '통해', '각각', '때문', '무단', '따른', '기자', '는데', '저작', '뉴스', '특파원', '하다', '이번', '이상',
             '전년', '제품', '업체', '기업', '지난해', '대비', '올해', '의원', '내년도', '절반', '당기', '대표', '만나', '분기',
             '국민', '정부', '지역', '현수막', '비중', '포토', 'vs', '파렴치','오전', '오후','정보', '이날', '상품', '세계',
             '시장', '경제', '과학', '사회', '문화', '정치', '처음', '가능', '매출', '소재', '작품', '자신', '위치', 
             '수준', '라이프', '여파', '해석', '고객', '국내', '관련', '내년', '주요']   # 계속 변동 예정
        self.correction_dict = {'lg' : '엘지', '중신' : '중신용', 'rd': 'R&D', '생활건강': '엘지생활건강', '예술전당': '예술의전당', 
                                '엘지생활':'엘지생활건강', 'gbgb' : ''}
        
    def __call__(self, text):
        text = text[:1000000]     # 텍스트 길이 제한(메모리용량 절약)
        raw_pos_tagged = self.tagger.pos(text)
        word_cleaned = [word for word, tag in raw_pos_tagged if tag in ['NNG', "SL"] and len(word) != 1 and word not in self.stopwords]
                                                              # 태그 진행- 명사와 영어 추출, 한단어와 불용 제외시킴
        # n-gram 생성(bigram)
        ngrams = zip(*[word_cleaned[i:] for i in range(self.n)])
        ngram_list = ["".join(ngram) for ngram in ngrams]  # 띄어쓰기 없이 단어를 연결

        # 단어 대체(짤린 단어들 보완)
        corrected_ngram_list = [ngram for ngram in ngram_list if ngram not in self.correction_dict]
        return corrected_ngram_list
