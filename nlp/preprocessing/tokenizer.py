class CustomTokenizer:
    def __init__(self, tagger):
        self.tagger = tagger
        self.stopwords = ['에게', '통해', '각각', '때문', '무단', '따른', '기자', '는데', '저작', '뉴스', '특파원', '하다', '이번', '이상',
             '전년', '제품', '업체', '기업', '지난해', '대비', '올해', '의원', '내년도', '절반', '당기', '대표', '만나', '분기',
             '국민', '정부', '지역', '현수막', '비중', '포토', 'vs', '파렴치','오전', '오후','정보', '이날', '상품', '세계',
             '시장', '경제', '과학', '사회', '문화', '정치', '생활', '처음', '가능', '매출', '소재', '작품', '자신', '위치', 'KB',
             '수준', '라이프', '여파', '해석', '고객', '국내', 'RD']

    def __call__(self, sent):
        sent = sent[:1000000]
        raw_pos_tagged = self.tagger.pos(sent)
        result = [word for word, tag in raw_pos_tagged if len(word) > 1 and (word not in self.stopwords) and (tag in ['NNG', "SL"])]
        return result