from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(resumes, job_desc):

    # 🚨 SAFETY CHECK
    if not resumes or not job_desc.strip():
        return []

    vectorizer = TfidfVectorizer()

    try:
        documents = resumes + [job_desc]
        tfidf_matrix = vectorizer.fit_transform(documents)

        scores = cosine_similarity(
            tfidf_matrix[:-1], tfidf_matrix[-1]
        ).flatten()

        return scores

    except Exception as e:
        print("Similarity Error:", e)
        return []
