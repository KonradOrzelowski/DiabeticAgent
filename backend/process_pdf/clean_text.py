from collections import Counter
import re
import matplotlib.pyplot as plt

# # Load your extracted text from PDF
# with open('output/standards-of-care-2025.txt', 'r', encoding='utf-8') as f:
#     text = f.read()


import re
import wordninja
import unicodedata
import re
import unicodedata
import wordninja

def clean_text(text, short_line_length=3, exclude_keywords=None, exclude_regex=None, avoid_splitting = 15):
    """
    Cleans and segments the input text by removing unwanted characters, lines, and specific content.
    
    Parameters:
    - text (str): The text to clean and segment.
    - short_line_length (int): Minimum line length to retain. Lines with fewer characters will be removed.
    - exclude_keywords (list of str, optional): List of keywords (e.g., 'Figure', 'Table') that, if found at the beginning of a line, will exclude that line.
    - exclude_regex (str, optional): A custom regular expression pattern. Lines that match this pattern will be removed.
    
    Returns:
    - str: The cleaned and filtered text.
    """
    # Normalize unicode characters and remove non-ASCII characters
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    
    # Convert all characters to lowercase for uniformity
    text = text.lower()

    # Remove page markers and URLs
    text = re.sub(r'^\s*-{2,}\s*page\s*\d+\s*-{2,}\s*$', '', text, flags=re.IGNORECASE | re.MULTILINE).strip()
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove non-ASCII characters that weren't already removed by normalization
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    # Replace non-standard quotes with standard quotes
    text = text.replace('“', '"').replace('”', '"').replace('’', "'")
    
    # Trim leading and trailing spaces
    text = text.strip()

    # Remove hyphenation at line breaks (e.g., "individu-\nals" → "individuals")
    text = re.sub(r'-\n', '', text)

    # Replace remaining newlines with space (optional, for paragraph formatting)
    text = text.replace('\n', ' ')

    # Clean up parentheses and extra spaces
    text = re.sub(r"\([^()]*\)", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Split joined words (like "atpresentation" → "at presentation")
    words = []
    for word in text.split():
        if len(word) > avoid_splitting:  # Heuristic to avoid splitting short normal words
            words.extend(wordninja.split(word))
        else:
            words.append(word)
    
    text = " ".join(words)

    # Step 1: Split the text into individual lines
    lines = text.splitlines()

    # Step 2: Filter out lines that don't meet the conditions
    filtered_lines = []
    for line in lines:
        # Exclude lines with just one character (or below the short_line_length threshold)
        if len(line.strip()) <= short_line_length:
            continue
        
        # Exclude lines starting with keywords like 'Figure' or 'Table' (if specified)
        if exclude_keywords:
            if any(line.lower().startswith(keyword.lower()) for keyword in exclude_keywords):
                continue
        
        # Exclude lines matching the custom regular expression pattern (if specified)
        if exclude_regex:
            if re.match(exclude_regex, line):
                continue
        
        # If the line passed all filters, keep it
        filtered_lines.append(line)
    
    # Join the remaining lines back into a single text block
    text = "\n".join(filtered_lines)
    
    return text


# text = clean_text(text)
# # text = clean_text(text)
# with open('output/processed-standards-of-care-2025.txt', 'w', encoding='utf-8') as f:
#     f.write(text)

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

# import nltk
# from nltk.util import ngrams
# from collections import Counter
# from nltk.corpus import stopwords
# import string
# import pandas as pd
# # Download necessary resources (if not already installed)
# # nltk.download('punkt')
# # nltk.download('stopwords')

# # Function to clean and extract frequent n-grams
# def extract_frequent_ngrams(text, n=2, top_n=10):
#     # Tokenize the text
#     words = nltk.word_tokenize(text.lower())  # Convert text to lowercase
    
#     # Remove punctuation and stopwords
#     stop_words = set(stopwords.words('english'))
#     words = [word for word in words if word not in stop_words and word not in string.punctuation]
    
#     # Generate n-grams
#     n_grams = ngrams(words, n)
    
#     # Count frequency of n-grams
#     n_gram_freq = Counter(n_grams)
    
#     # Get the most common n-grams
#     common_ngrams = n_gram_freq.most_common(top_n)
    
#     # Convert tuple n-grams back to strings
    
#     df = pd.DataFrame(common_ngrams, columns=['term', 'count'])
#     df['ngram'] = n
#     return df

# lst = []
# from tqdm import tqdm
# for n in tqdm([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]):
#     frequent_ngrams = extract_frequent_ngrams(text, n=n, top_n=50)
#     lst.append(frequent_ngrams)


# def modify_row(row):
#     row.term = " ".join(row.term)
#     return row

# # Concatenate DataFrames along rows (axis=0)
# combined_df = pd.concat(lst, axis=0, ignore_index=True)
# # Apply the function to each row
# combined_df = combined_df.apply(modify_row, axis=1)



# # Display the result
# print(combined_df)
# combined_df.to_csv('combined_data.csv', index=False)



