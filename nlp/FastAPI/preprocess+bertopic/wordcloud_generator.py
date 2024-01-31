from wordcloud import WordCloud
import io
import base64

def generate_wordcloud(topic_model):
    keyword_freq = {}
    for _, topic in topic_model.get_topics().items():
        for word, weight in topic:
            keyword_freq[word] = keyword_freq.get(word, 0) + weight

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(keyword_freq)
    img = io.BytesIO()
    wordcloud.to_image().save(img, 'PNG')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()
