from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import pickle
from tqdm import tqdm  # Optional: for progress bar

# Set up the splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

pdf_folder_path = "documents/"
if not os.path.exists(pdf_folder_path):
    raise FileNotFoundError(f"The folder {pdf_folder_path} does not exist.")

pdf_files = [f for f in os.listdir(pdf_folder_path) if f.lower().endswith('.pdf')]

if not pdf_files:
    raise ValueError("No PDF files found in the directory.")

print(f"Found {len(pdf_files)} PDF files. Proceeding with loading...")

from unstructured.cleaners.core import clean_extra_whitespace, clean_non_ascii_chars, remove_punctuation, group_broken_paragraphs

import re
import string

exclude_phrases = [
    'Check for updates',
    'American Diabetes Association',
    'Professional Practice Committee',
    'Diabetes Care 2025;',
    'diabetesjournals.org/care',
    'Diabetes Technology',
    'O R P D N A E R A C G N I V O R P M I .',
    'Standards of Care in Diabetes2025',
    '2024 by the . Readers may use this article as long as the work is properly cited, the use is educational and not for prot, and the work is not altered. More information is available at .diabetesjournals.org/journals/pages/license.'
    ,'A complete list of members of the American DiabetesAssociationProfessionalPracticeCommittee can be found at -SINT.'
    ,'Diabetes Care Volume 48, Supplement 1, January 2025'
    ,'Duality of interest information for each author is available at'
]

def clean_text(text):
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove phrases
    pattern = '|'.join(re.escape(phrase) for phrase in exclude_phrases)

    text = re.sub(pattern, ' ', text)

    # Remove URLs separately
    text = re.sub(r'http\S+|www\S+', '', text)

    # Remove extra whitespace again if needed
    text = re.sub(r'\s+', ' ', text)

    lines = text.splitlines()
    lines = [line for line in lines if len(line.strip()) > 3]
    cleaned_text = '\n'.join(lines)

    return cleaned_text.strip()



post_processors=[clean_extra_whitespace, clean_non_ascii_chars, group_broken_paragraphs, clean_text]




loaders = []
for fn in pdf_files:
    file_path=os.path.join(pdf_folder_path, fn)

    pdf2load = UnstructuredPDFLoader(file_path = file_path, strategy="hi_res", post_processors = post_processors) 
    loaders.append(pdf2load)


all_documents = []

for loader in tqdm(loaders, desc="Processing PDFs"):
    print(f"Loading raw document... {loader.file_path}")
    raw_documents = loader.load()

    print("Splitting text...")
    documents = text_splitter.split_documents(raw_documents)
    all_documents.extend(documents)

# Save all_documents with pickle
with open('all_documents.pkl', 'wb') as f:
    pickle.dump(all_documents, f)

print(f"Saved {len(all_documents)} documents to all_documents.pkl")

# print("Creating vectorstore...")
# embeddings = OpenAIEmbeddings()
# vectorstore = FAISS.from_documents(all_documents, embeddings)

# # Save the FAISS vectorstore using FAISS native method
# vectorstore.save_local("faiss_index/")

# print("Vectorstore saved to faiss_index/ ✅")
