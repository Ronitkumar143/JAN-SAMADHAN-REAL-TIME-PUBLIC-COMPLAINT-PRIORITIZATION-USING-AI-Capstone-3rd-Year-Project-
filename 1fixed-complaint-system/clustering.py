from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def cluster_complaints(complaints):
    """Cluster complaints using KMeans. Requires at least 5 complaints."""
    # Fix: Dynamically set n_clusters to avoid crash when fewer complaints than clusters
    n_clusters = min(5, len(complaints))

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(complaints)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)  # Fix: added n_init to suppress warning
    labels = kmeans.fit_predict(X)

    result = []
    for i, complaint in enumerate(complaints):
        result.append({
            "complaint": complaint,
            "cluster": int(labels[i])
        })

    return result
