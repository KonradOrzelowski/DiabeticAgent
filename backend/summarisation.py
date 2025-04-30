from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from keybert import KeyBERT
import openai

openai.api_key = "your-api-key"  # Set your OpenAI key

kw_model = KeyBERT()
embeddings = OpenAIEmbeddings()

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You summarize text."},
            {"role": "user", "content": f"Summarize this: {text}"}
        ],
        max_tokens=50
    )
    return response.choices[0].message.content.strip()

chunks = [
    "This chunk is about how neural networks work in computer vision.",
    "Another chunk talks about the history of data analysis techniques.",
]

documents = []
for chunk in chunks:
    keywords = kw_model.extract_keywords(chunk, top_n=5)
    keyword_list = [kw[0] for kw in keywords]
    summary = summarize_text(chunk)

    doc = Document(
        page_content=chunk,
        metadata={
            "keywords": keyword_list,
            "summary": summary
        }
    )
    documents.append(doc)

vectorstore = FAISS.from_documents(documents, embeddings)
