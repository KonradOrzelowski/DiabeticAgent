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

# Define tool for document search
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

    return docs if extended else docs_str



def run_assistant():
    init_agent = Agent("gpt-4o-mini", tools=[get_relevent_docs], verbose = False)
    agent = init_agent.agent_with_chat_history
    config = {"configurable": {"session_id": init_agent.session_id}}

    while True:
        query = input(f"Human: ")
        response = agent.invoke({'input': query}, config)
        print(response['output'])

if __name__ == "__main__":
    faiss_index = load_faiss_index('dr_bernstein_diabetes_solution')
    faiss_index_1 = load_faiss_index('standards_of_care_2025')
    faiss_index.merge_from(faiss_index_1)

    run_assistant()
