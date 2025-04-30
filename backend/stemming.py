import spacy
nlp = spacy.load("en_core_web_sm")

def lemmatize_text(text):
    doc = nlp(text)
    lemmatized = [token.lemma_ for token in doc]
    return ' '.join(lemmatized)

from keybert import KeyBERT
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Initialize models
kw_model = KeyBERT()
embeddings = OpenAIEmbeddings()

# Example text chunks
chunks = [
    "The user is running machine learning experiments.",
    "Users have run different data analysis workflows.",
]

# Preprocess and extract keywords
documents = []
for chunk in chunks:
    # Preprocess chunk (choose either stemming or lemmatization)
    processed_chunk = lemmatize_text(chunk)  # or stem_text(chunk)
    
    # Extract keywords from the processed chunk
    keywords = kw_model.extract_keywords(processed_chunk, top_n=5)
    keyword_list = [kw[0] for kw in keywords]
    
    # Store original chunk + keywords from processed version
    doc = Document(page_content=chunk, metadata={"keywords": keyword_list})
    documents.append(doc)

# Create the FAISS vector store
vectorstore = FAISS.from_documents(documents, embeddings)
