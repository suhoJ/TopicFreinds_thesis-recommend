from bertopic import BERTopic
from sklearn.cluster import DBSCAN
from bertopic.vectorizers import ClassTfidfTransformer
from gensim.models import CoherenceModel
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO
