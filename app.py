from flask import Flask, render_template, request, jsonify
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

app = Flask(__name__)

# Load dataset
newsgroups_data = fetch_20newsgroups(subset='all')
documents = newsgroups_data.data

# Preprocess and vectorize dataset
stop_words = stopwords.words('english')
vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=1000)  # Limit features to 1000
X = vectorizer.fit_transform(documents)

# Apply Truncated SVD (LSA)
lsa = TruncatedSVD(n_components=100)  # Reduce to 100 dimensions
X_reduced = lsa.fit_transform(X)

def search_engine(query):
    """
    Function to search for top 5 similar documents given a query
    Input: query (str)
    Output: documents (list), similarities (list), indices (list)
    """
    # Preprocess and vectorize the query
    query_vec = vectorizer.transform([query])
    query_reduced = lsa.transform(query_vec)

    # Calculate cosine similarities
    similarities = cosine_similarity(query_reduced, X_reduced)[0]

    # Get top 5 most similar documents
    top_indices = np.argsort(similarities)[::-1][:5]  # Indices of top 5 similar documents
    top_similarities = similarities[top_indices]
    top_documents = [documents[i] for i in top_indices]

    return top_documents, top_similarities, top_indices

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    documents, similarities, indices = search_engine(query)
    return jsonify({'documents': documents, 'similarities': similarities.tolist(), 'indices': indices.tolist()})

if __name__ == '__main__':
    app.run(debug=True)
