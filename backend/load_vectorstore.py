from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    BaseMessage,
    SystemMessage,
    trim_messages,
)
from langchain_openai import ChatOpenAI

from process_pdf import ProcessPDF

def load_faiss_index(file_name):
    pp = ProcessPDF(file_name)
    pp.load_vectorestore()
    return pp.vectorstore

faiss_index = load_faiss_index('dr_bernstein_diabetes_solution')
faiss_index_1 = load_faiss_index('standards_of_care_2025')

faiss_index.merge_from(faiss_index_1)

model = ChatOpenAI(model_name="gpt-4o-mini")

# def get_prompt_question(question, extended=False):

#     docs = faiss_index.similarity_search(question)
#     doc_content = {}
#     new_line = '\n'

#     for idx, doc in enumerate(docs):
#         doc_content[f'doc_{idx}'] = doc.page_content

#     docs_str = {''.join([f"{key}: {value}{new_line}" for key, value in doc_content.items()])}
    

#     message = HumanMessage(f"""
#     Helpful documents:
#     -------------------
#     {docs_str}
    

#     Please respond to the following question:
#     -----------------------------------------

#     {question}
#     """)

#     if extended:
#         return message, doc_content, question
#     else:
#         return message



import json
language = "English"

trimmer = trim_messages(
    max_tokens=4,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False
)




from langchain.agents import initialize_agent, Tool
from langchain_core.tools import tool

@tool("Diabetes Document Search", parse_docstring=True)
def get_relevent_docs(question: str) -> str:
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
    return docs_str
from langchain.agents import AgentExecutor, create_react_agent

tools = [get_relevent_docs]

assistant_instruction_str = (
                "You are a diabetic assistant. "
                "Your role is to assist users in better managing type 1 diabetes. "
                "Answer the following questions as best you can. You have access to the following tools:"
                f"{tools}"
                "Make sure to reference the documents where relevant, "
                "but do not limit your responses to them if additional context or insights from your training would be helpful."
)

assistant_instruction = SystemMessage(content=assistant_instruction_str)
assistant_instruction.pretty_print()


from langchain.agents.react.agent import create_react_agent
from langchain.agents import AgentExecutor

from langchain.prompts import PromptTemplate

tool_names = [tool.name for tool in tools]
prompt_template = PromptTemplate(
    input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
    template="""
You are a diabetic assistant. 
Your role is to assist users in managing type 1 diabetes.

You can use the following tools:
{tools}

When answering, follow this format exactly:
Thought: You could think about what to do
Action: You may take one of this actions if you think so [{tool_names}]
Action Input: The input to the action

Then, after observing the result of the action, continue the thought process and provide a final answer if ready.

Begin!

Question: {input}

{agent_scratchpad}
"""
)




agent = create_react_agent(llm=model, tools=tools, prompt=prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True, handle_parsing_errors=True)


def run_assistant():
    messages_lst = [assistant_instruction]
    while True:
        query = input(f"Len: {len(messages_lst)} Human: ")

        # message, doc_content, question = get_prompt_question(query, True)
        messages_lst.append(query)

        
        response = agent_executor.invoke({'input': query})

        print(response)

        model_response = AIMessage(response['output'])
        model_response.pretty_print()

        messages_lst.append(model_response)
        messages_lst = trimmer.invoke(messages_lst)

run_assistant()

# from langchain.load.dump import dumps

# messages_string = dumps(messages.content, ensure_ascii=False, pretty = True)
# doc_content = dumps(doc_content, ensure_ascii=False, pretty = True)
# question = dumps(question, ensure_ascii=False, pretty = True)

# with open('json_exports/messages_string.json', 'w', encoding='utf-8') as f:
#     f.write(messages.pretty_repr())


# with open('json_exports/doc_content.json', 'w', encoding='utf-8') as f:
#     f.write(doc_content)


# with open('json_exports/question.json', 'w', encoding='utf-8') as f:
#     f.write(question)


# # response = model.invoke(messages)
# # response_string = dumps(response, ensure_ascii=False, pretty = True)

# # with open('response_string.json', 'w', encoding='utf-8') as f:
# #     f.write(response_string)