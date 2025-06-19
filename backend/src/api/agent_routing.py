import json
from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter

from langchain_community.vectorstores import FAISS
from processing.process_pdf import ProcessPDF
from langchain_core.tools import tool
from langchain_core.load import loads

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

router = APIRouter()
# Load and merge FAISS indices
def load_faiss_index(file_name):
    pp = ProcessPDF(file_name)
    pp.load_vectorestore()
    return pp.vectorstore

faiss_index = load_faiss_index('dr_bernstein_diabetes_solution')
faiss_index_1 = load_faiss_index('standards_of_care_2025')
faiss_index.merge_from(faiss_index_1)


@tool("DiabetesDocumentSearch", parse_docstring=True)
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


def process_image(message, image):
    message_content = [{"type": "text", "text": message}]

    if image:
        message_content.append({
            "type": "image_url",
            "image_url": {"url": image}
        })

    chat = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = chat([HumanMessage(content=message_content)])

    return response

@router.post("/question/")
async def test_post(data: Item):
    response = process_image(data.message, data.image)

    response.pretty_print()
    return {"message": response.text()}