from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from process_pdf import ProcessPDF

def load_faiss_index(file_name):
    pp = ProcessPDF(file_name)
    pp.load_vectorestore()
    return pp.vectorstore

faiss_index = load_faiss_index('dr_bernstein_diabetes_solution')
faiss_index_1 = load_faiss_index('standards_of_care_2025')

faiss_index.merge_from(faiss_index_1)



from langchain.agents import initialize_agent, Tool
from langchain_core.tools import tool

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

    if extended:
        return docs
    else:
        return docs_str

from langchain.agents import AgentExecutor, create_react_agent

tools = [get_relevent_docs]


from langchain.agents.react.agent import create_react_agent
from langchain.agents import AgentExecutor

from langchain.prompts import PromptTemplate

tool_names = [tool.name for tool in tools]
prompt_template = PromptTemplate(
    input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
    template="""
You are a diabetic assistant. 
Your role is to assist users in managing type 1 diabetes.
'placeholder' {chat_history}
You can use the following tools:
{tools}

When answering, follow this format exactly:
Thought: You could think about what to do
Action: You may take one of this actions if you think so [{tool_names}]
Action Input: Firstly, decide if you need to use a tool

Then, after observing the result of the action, continue the thought process and provide a final answer if ready.

Begin!

Question: {input}

{agent_scratchpad}
"""
)

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
model = ChatOpenAI(model_name="gpt-4o-mini")
memory = InMemoryChatMessageHistory(session_id="test-session")
agent = create_react_agent(llm=model, tools=tools, prompt=prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True, handle_parsing_errors=True)

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="output"  # Ensure this key matches the output of your agent
)
config = {"configurable": {"session_id": "test-session"}}

def run_assistant():

    while True:
        query = input(f"Human: ")
       
        response = agent_with_chat_history.invoke({'input': query}, config)

        print(response)


run_assistant()
