import os
import json
import pickle

# Set your folder path here
folder_path = 'output/standards-of-care-2025/jsons'

pages = []

# Load JSONs and collect (page_number, content)
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'page_number' in data and 'content' in data:
                pages.append((data['page_number'], data['content']))

# Sort by page_number
pages.sort(key=lambda x: x[0])

# Format with separators
formatted_pages = []
for page_number, content in pages:
    separator = f"\n-------------------- page {page_number} --------------------\n"
    formatted_pages.append(separator + content)

# Join everything
full_text = "\n".join(formatted_pages)

# Save to pickle
with open('output/standards-of-care-2025.pkl', 'wb') as f:
    pickle.dump(full_text, f)

print("Merged content with page separators saved to output/standards-of-care-2025.pkl")

with open('output/standards-of-care-2025.txt', 'w', encoding='utf-8') as f:
    f.write(full_text)

import pickle

# Load documents from pickle
with open('output/standards-of-care-2025.pkl', 'rb') as f:
    all_documents = pickle.load(f)

print(f"Loaded {len(all_documents)} documents from all_documents.pkl")

print(type(all_documents), len(all_documents))
print(all_documents[1000:2000])