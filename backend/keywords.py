import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sentence_transformers import SentenceTransformer

# Example: List of chunks in the document
chunks = [
    "This is the first chunk of text.",
    "This chunk talks about something else, like machine learning.",
    "The third chunk is about the importance of data science."
]

# 1. TF-IDF Extraction
def extract_tfidf_keywords(chunks, top_n=3):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(chunks)
    df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

    keywords = []
    for index, row in df_tfidf.iterrows():
        top_keywords = row.nlargest(top_n).index.tolist()
        keywords.append(top_keywords)
    
    return keywords

# 2. Topic Modeling (LDA)
def extract_lda_keywords(chunks, num_topics=2, num_words=5):
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(chunks)
    
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=0)
    lda.fit(X)
    
    terms = vectorizer.get_feature_names_out()
    lda_keywords = []
    for topic_idx, topic in enumerate(lda.components_):
        topic_keywords = [terms[i] for i in topic.argsort()[:-num_words - 1:-1]]
        lda_keywords.append(topic_keywords)
    
    return lda_keywords

# 3. Sentence Embeddings with BERT
def extract_bert_keywords(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Get embeddings for the entire document and for each chunk
    doc_embedding = model.encode([" ".join(chunks)])
    chunk_embeddings = model.encode(chunks)
    
    # Calculate similarity between each chunk and the full document
    cosine_similarities = []
    for chunk_emb in chunk_embeddings:
        similarity = np.dot(chunk_emb, doc_embedding.T) / (np.linalg.norm(chunk_emb) * np.linalg.norm(doc_embedding))
        cosine_similarities.append(similarity)
    
    return cosine_similarities

# Combine all methods
def generate_keywords_for_chunks(chunks):
    # TF-IDF Keywords
    tfidf_keywords = extract_tfidf_keywords(chunks)
    
    # LDA Keywords
    lda_keywords = extract_lda_keywords(chunks)
    
    # BERT-based Keyword Relevance
    bert_similarities = extract_bert_keywords(chunks)
    
    # Display the results
    print("Keywords from TF-IDF for each chunk:")
    for i, keywords in enumerate(tfidf_keywords):
        print(f"Chunk {i + 1}: {keywords}")
    
    print("\nKeywords from LDA for each chunk:")
    for i, keywords in enumerate(lda_keywords):
        print(f"Chunk {i + 1}: {keywords}")
    
    print("\nBERT Similarities (chunk relevance to full document):")
    for i, sim in enumerate(bert_similarities):
        print(f"Chunk {i + 1}: Similarity = {sim[0]:.4f}")

# Run the function with the example chunks
generate_keywords_for_chunks(chunks)
