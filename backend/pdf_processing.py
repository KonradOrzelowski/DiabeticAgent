from langchain_unstructured import UnstructuredLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import pickle

# Set up the splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

pdf_folder_path = "documents/"
if not os.path.exists(pdf_folder_path):
    raise FileNotFoundError(f"The folder {pdf_folder_path} does not exist.")
    
pdf_files = [f for f in os.listdir(pdf_folder_path) if f.lower().endswith('.pdf')]

if not pdf_files:
    raise ValueError("No PDF files found in the directory.")

print(f"Found {len(pdf_files)} PDF files. Proceeding with loading...")


# Load multiple files
loaders = [UnstructuredLoader(file_path=os.path.join(pdf_folder_path, fn)) for fn in pdf_files]

all_documents = []

for loader in loaders:
    print(f"Loading raw document... {loader.file_path}")
    raw_documents = loader.load()

    print("Splitting text...")
    documents = text_splitter.split_documents(raw_documents)
    all_documents.extend(documents)

print("Creating vectorstore...")
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(all_documents, embeddings)

with open("vectorstore.pkl", "wb") as f:
    pickle.dump(vectorstore, f)

print("Vectorstore saved to vectorstore.pkl")
