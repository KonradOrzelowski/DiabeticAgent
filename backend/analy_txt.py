from collections import Counter
import re
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Download resources (only needed once)
nltk.download('punkt')
nltk.download('stopwords')

# Load your extracted text from PDF
with open('output/standards-of-care-2025.txt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
import wordninja

import re
import wordninja

def clean_and_segment_text(text):
    # Step 1: Remove lines with only one character and lines starting with 'Figure' or 'Table'
    lines = text.splitlines()
    lines = [
        line for line in lines 
        if not re.fullmatch(r'\s*[a-zA-Z]\s*', line) and
           not re.match(r'^\s*(Figure|Table)\b', line, re.IGNORECASE)
    ]
    text = "\n".join(lines)


    # Step 3: Split overly long merged words
    words = text.split()
    fixed_words = []
    for word in words:
        if len(word) > 20:  # You can adjust the threshold
            fixed_words.extend(wordninja.split(word))
        else:
            fixed_words.append(word)

    return text

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

text = clean_and_segment_text(text)
text = clean_text(text)
with open('output/processed-standards-of-care-2025.txt', 'w', encoding='utf-8') as f:
    f.write(text)
# Preprocess text: lowercasing and removing non-alphabetic characters
# text = text.lower()
# text = re.sub(r'[^a-z\s]', '', text)

# Tokenize and remove stopwords
# tokens = word_tokenize(text)
# filtered_tokens = [word for word in tokens if word not in stopwords.words('english')]

# Frequency analysis
# word_freq = Counter(filtered_tokens)

# Show top 10 words
# print(word_freq.most_common(10))

# # Optional: Plot
# words, counts = zip(*word_freq.most_common(10))
# plt.bar(words, counts)
# plt.xticks(rotation=45)
# plt.title('Top 10 Frequent Words')
# plt.show()

# from keybert import KeyBERT

# kw_model = KeyBERT()

# keywords = kw_model.extract_keywords(text, top_n=50)

# # Print the extracted keywords
# for keyword in keywords:
#     print(f"Keyword: {keyword[0]} | Similarity: {keyword[1]}")

# Install necessary libraries if you haven't
# pip install nltk

import nltk
from nltk.util import ngrams
from collections import Counter
from nltk.corpus import stopwords
import string
import pandas as pd
# Download necessary resources (if not already installed)
# nltk.download('punkt')
# nltk.download('stopwords')

# Function to clean and extract frequent n-grams
def extract_frequent_ngrams(text, n=2, top_n=10):
    # Tokenize the text
    words = nltk.word_tokenize(text.lower())  # Convert text to lowercase
    
    # Remove punctuation and stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words and word not in string.punctuation]
    
    # Generate n-grams
    n_grams = ngrams(words, n)
    
    # Count frequency of n-grams
    n_gram_freq = Counter(n_grams)
    
    # Get the most common n-grams
    common_ngrams = n_gram_freq.most_common(top_n)
    
    # Convert tuple n-grams back to strings
    
    df = pd.DataFrame(common_ngrams, columns=['term', 'count'])
    df['ngram'] = n
    return df

lst = []
from tqdm import tqdm
for n in tqdm([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]):
    frequent_ngrams = extract_frequent_ngrams(text, n=n, top_n=50)
    lst.append(frequent_ngrams)


def modify_row(row):
    row.term = " ".join(row.term)
    return row

# Concatenate DataFrames along rows (axis=0)
combined_df = pd.concat(lst, axis=0, ignore_index=True)
# Apply the function to each row
combined_df = combined_df.apply(modify_row, axis=1)



# Display the result
print(combined_df)
combined_df.to_csv('combined_data.csv', index=False)



