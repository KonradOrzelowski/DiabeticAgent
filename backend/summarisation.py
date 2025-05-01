from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
# from keybert import KeyBERT
import openai
import os
from langchain_openai import ChatOpenAI  # Fix LLM import
from tqdm import tqdm


openai_api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model_name="gpt-4.1-nano", api_key=openai_api_key)

# kw_model = KeyBERT()
embeddings = OpenAIEmbeddings()

import json

with open('output/standards-of-care-2025-chunks.json', 'r') as file:
    chunks = json.load(file)


def summarize_text(text):

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert text editor tasked with cleaning and improving text extracted from PDFs. "
                "Your goal is to fix formatting issues (such as incorrect line breaks, unwanted hyphenation, and improper spacing), "
                "eliminate redundancy, simplify overly complex sentences, and ensure grammatical correctness. "
                "Use clear, formal, and active language while preserving the original meaning. Your output should be well-organized and concise."
            )
        },
        {
            "role": "user",
            "content": f"Please clean and format the following text:\n\n{text}"
        }
    ]



    response = model.invoke(messages)
    return response

    
formated_chunks = {}



for key, value in tqdm(chunks.items()):
    formated_chunks[key] = summarize_text(value).content

with open('output/standards-of-care-2025-chunks-formated.json', 'w') as f:
    json.dump(formated_chunks, f, indent=4)

# summary = summarize_text(data['chunk_0'])
# print('-'*20, 'response', '-'*20)
# print(summary.content)

    # doc = Document(
    #     page_content=chunk,
    #     metadata={
    #         "keywords": keyword_list,
    #         "summary": summary
    #     }
    # )
    # documents.append(doc)
    

# vectorstore = FAISS.from_documents(documents, embeddings)
