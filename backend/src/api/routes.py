from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.get_agent import Agent


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=False,  # must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from processing.process_pdf import ProcessPDF
from langchain.agents import initialize_agent, Tool
from langchain_core.tools import tool
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

import json
from langchain_core.load import dumpd, dumps, load, loads

# @app.get("/model/")
# def read_root():
#     query = 'Hi, gimme some docs about glucose spikes'

#     init_agent = Agent("gpt-4o-mini", tools=[get_relevent_docs], verbose=True)
#     agent = init_agent.agent_with_chat_history
#     config = {"configurable": {"session_id": init_agent.session_id}}

#     response = agent.invoke({'input': query}, config)

#     with open('response.json', 'w', encoding='utf-8') as f:
#         dumps_response = dumps(response, pretty=True)
#         json.dump(dumps_response, f, indent=4)

#     return {"response": response}
from pydantic import BaseModel

@app.get("/")
async def main():
    return {"message": "Hello World"}

class Item(BaseModel):
    message: str

from langchain_core.chat_history import InMemoryChatMessageHistory

chats_by_session_id = {}


def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    chat_history = chats_by_session_id.get(session_id)
    if chat_history is None:
        chat_history = InMemoryChatMessageHistory()
        chats_by_session_id[session_id] = chat_history
    return chat_history

init_agent = Agent("gpt-4o-mini", tools=[get_relevent_docs], verbose=True)
agent = init_agent.agent_with_chat_history

@app.post("/question/")
async def test_post(data: Item):
    # print(data.message)

    config = {"configurable": {"session_id": init_agent.session_id}}

    response = agent.invoke({'input': data.message}, config)



    return {"message": response}

@app.get("/response/")
def read_root():
    with open('response.json', 'r', encoding='utf-8') as f:
        contents = json.load(f)
        response = loads(contents)

    return {"response": response}