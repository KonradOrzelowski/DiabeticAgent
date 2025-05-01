import os
import json
import pickle

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document  # Optional, depending on how your chunks are structured

folder_path = 'output/standards-of-care-2025-chunks-formated.json'

with open(folder_path, 'r') as f:  # use 'r' since it's a JSON file, not binary
    formatted_chunks = json.load(f)


all_documents = [Document(page_content=chunk) for chunk in formatted_chunks.values()]

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(all_documents, embeddings)

# Save the FAISS vectorstore using FAISS native method
vectorstore.save_local("faiss_index/")

print("Vectorstore saved to faiss_index/ ✅")
