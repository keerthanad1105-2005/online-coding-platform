from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(code1, code2):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([code1, code2])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])
    return round(float(similarity[0][0]) * 100, 2)