import json
from typing import Optional

from pydantic import BaseModel


from agents.get_agent import Agent

from fastapi import APIRouter

router = APIRouter()



from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from processing.process_pdf import ProcessPDF
from langchain.agents import initialize_agent, Tool
from langchain_core.tools import tool
from langchain_core.load import dumpd, dumps, load, loads

from agents.get_agent import Agent

# Load and merge FAISS indices
def load_faiss_index(file_name):
    pp = ProcessPDF(file_name)
    pp.load_vectorestore()
    return pp.vectorstore

faiss_index = load_faiss_index('dr_bernstein_diabetes_solution')
faiss_index_1 = load_faiss_index('standards_of_care_2025')
faiss_index.merge_from(faiss_index_1)


@tool("Diabetes Document Search", parse_docstring=True)
def get_relevent_docs(question: str, extended: bool = False) -> str:
    """
    Retrieve and format relevant documents from a FAISS index based on a given question.

    Args:
        question (str): The input question used to perform a similarity search in the FAISS index.

    Returns:
        str: A formatted string containing the contents of the most relevant documents, each labeled by index.
    """
    docs = faiss_index.similarity_search(question)
    doc_content = {}
    new_line = '\n'

    for idx, doc in enumerate(docs):
        doc_content[f'doc_{idx}'] = doc.page_content
     
    docs_str = ''.join([f"{key}: {value}{new_line}" for key, value in doc_content.items()])


    return docs

@router.get("/")
async def main():
    return {"message": "Hello World"}

class Item(BaseModel):
    message: str
    image: Optional[str] = None

import base64
from openai import OpenAI

client = OpenAI()

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# Initialize model
chat = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


@router.post("/question/")
async def test_post(data: Item):
    message_content = [
        {
            "type": "text",
            "text": "what's in this image?"
        },
        {
            "type": "image_url",
            "image_url": {
                "url": "https://raw.githubusercontent.com/kevinsqi/react-calendar-heatmap/HEAD/demo/public/react-calendar-heatmap.png?raw=true"
            }
        }
    ]

    human_message = HumanMessage(
        content=message_content
    )

    response = chat([human_message])
    print(response.content)

    return {"message": response.content}






@router.post("/test_image/")
def test_post_(data: Item):
    # print(data)

    return {"message": 'nse'}


@router.get("/response/")
def read_root():
    with open('response.json', 'r', encoding='utf-8') as f:
        contents = json.load(f)
        response = loads(contents)

    return {"response": response}