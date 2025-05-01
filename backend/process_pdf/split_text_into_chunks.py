# Main Chunking Functions
from chunking_evaluation.chunking import (
    LLMSemanticChunker
)

# Additional Dependencies
from chromadb.utils import embedding_functions
import os

openai_api_key = os.getenv("OPENAI_API_KEY")

def split_text_into_chunks(text):

    embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=openai_api_key, model_name="text-embedding-3-large")

    llm_chunker = LLMSemanticChunker(
        organisation="openai", 
        model_name="gpt-4.1-mini", 
        api_key=openai_api_key
    )

    llm_chunker_chunks = llm_chunker.split_text(text)

    dct = {}
    for idx, chunk in enumerate(llm_chunker_chunks):
        dct[f'chunk_{idx}'] = chunk
    
    return dct
