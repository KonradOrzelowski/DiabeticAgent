from langchain.embeddings import OpenAIEmbeddings
import openai
import os
from langchain_openai import ChatOpenAI
from tqdm import tqdm
import json

def summarize_text(text, model):
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
    return model.invoke(messages)

def format_chunks(chunks):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    model = ChatOpenAI(model_name="gpt-4.1-nano", api_key=openai_api_key)

    formatted_chunks = {}

    for key, value in tqdm(chunks.items()):
        try:
            formatted_chunks[key] = summarize_text(value, model).content
        except Exception as e:
            print(f"[ERROR] Failed to process chunk {key}: {e}")

    return formatted_chunks

def main():
    with open('output/standards-of-care-2025-chunks.json', 'r') as file:
        chunks = json.load(file)

    formatted_chunks = format_chunks(chunks)

    with open('output/standards-of-care-2025-chunks-formatted.json', 'w') as f:
        json.dump(formatted_chunks, f, indent=4)

# if __name__ == "__main__":
#     main()

