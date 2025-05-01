from process_pdf.extract_pdf_to_text import extract_pdf_to_text
from process_pdf.clean_text import clean_text

# extract_pdf_to_text(file_name = 'standards-of-care-2025')

# Load your extracted text from PDF
with open('output/standards-of-care-2025.txt', 'r', encoding='utf-8') as f:
    text = f.read()

text = clean_text(text)

with open('output/processed-standards-of-care-2025.txt', 'w', encoding='utf-8') as f:
    f.write(text)


# Main Chunking Functions
from chunking_evaluation.chunking import (
    ClusterSemanticChunker,
    LLMSemanticChunker,
    FixedTokenChunker,
    RecursiveTokenChunker,
    KamradtModifiedChunker
)
# Additional Dependencies
import tiktoken
from chromadb.utils import embedding_functions
from chunking_evaluation.utils import openai_token_count
import os

embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=os.environ["OPENAI_API_KEY"], model_name="text-embedding-3-large")

def openai_token_count(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string, disallowed_special=()))
    return num_tokens



import os
import pickle
import json

# Assuming LLMSemanticChunker is defined and available in your environment
llm_chunker = LLMSemanticChunker(
    organisation="openai", 
    model_name="gpt-4.1-mini", 
    api_key=os.getenv("OPENAI_API_KEY")  # Using getenv to avoid crashes if key is not set
)

# Split the text into chunks
llm_chunker_chunks = llm_chunker.split_text(text)

# Save the chunks as a pickle file
with open('output/standards-of-care-2025-chunks.pkl', 'wb') as f:
    pickle.dump(llm_chunker_chunks, f)

# Save chunks into a dictionary
dct = {f'chunk_{idx}': chunk for idx, chunk in enumerate(llm_chunker_chunks)}


with open('output/standards-of-care-2025-chunks.json', 'w') as f:
    json.dump(dct, f, indent=4)

openai_api_key = os.getenv("OPENAI_API_KEY")
def split_text_into_chunks(text):

    embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=openai_api_key, model_name="text-embedding-3-large")

    llm_chunker = LLMSemanticChunker(
        organisation="openai", 
        model_name="gpt-4.1-mini", 
        api_key=openai_api_key
    )

    llm_chunker_chunks = llm_chunker.split_text(text)
    dct = {f'chunk_{idx}': chunk for idx, chunk in enumerate(llm_chunker_chunks)}
    return dct

