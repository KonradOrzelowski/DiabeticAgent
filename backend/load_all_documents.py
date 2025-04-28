import pickle

# Load documents from pickle
with open('all_documents.pkl', 'rb') as f:
    all_documents = pickle.load(f)

print(f"Loaded {len(all_documents)} documents from all_documents.pkl")


import re

docs_with_text = []

text_to_find = 'DIABETES AND POPULATION HEALTH'.lower() 

for doc in all_documents:
    text = doc.page_content.lower() 
    if text_to_find in text:
        docs_with_text.append(doc.page_content)

# Output the results
print(f"Found {len(docs_with_text)} documents containing 'docs_with_text'.")
for idx, rec in enumerate(docs_with_text):
    print(f"\nDocument {idx + 1} contains 'docs_with_text':\n")
    print(rec)  # Print the first 500 characters for review, adjust as needed
