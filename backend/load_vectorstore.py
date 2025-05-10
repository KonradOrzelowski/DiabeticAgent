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

def get_prompt_question(question, extended=False):

    docs = faiss_index.similarity_search(question)
    doc_content = {}
    new_line = '\n'

    for idx, doc in enumerate(docs):
        doc_content[f'doc_{idx}'] = doc.page_content
    

    message = HumanMessage(f"""
    Helpful documents:
    -------------------
    
    {''.join([f"{key}: {value}{new_line}" for key, value in doc_content.items()])}

    Please respond to the following question:
    -----------------------------------------

    {question}
    """)

    if extended:
        return message, doc_content, question
    else:
        return message



import json
language = "English"

trimmer = trim_messages(
    max_tokens=4,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

query =   """
    Help me to analyiste my night sugar from this period:
    | date       |   min |   max |   mean |   25th_per |   50th_per |   75th_per |
    |:-----------|------:|------:|-------:|-----------:|-----------:|-----------:|
    | 2024-09-24 |    49 |   118 |  91.13 |      83.75 |       89.5 |     100    |
    | 2024-09-25 |    92 |   132 | 113.83 |     108    |      113.5 |     119.5  |
    | 2024-09-26 |    54 |   127 |  85.06 |      70    |       81   |     100    |
    | 2024-09-27 |    39 |   124 |  95.14 |      83    |       99   |     112    |
    | 2024-09-28 |    39 |   138 |  98.92 |      85    |       99   |     116    |
    | 2024-09-29 |    63 |   136 | 108.32 |      99.25 |      112   |     124.25 |
    | 2024-09-30 |    55 |   172 | 112.62 |     103    |      112   |     127    |
    | 2024-10-01 |    39 |   191 | 113.06 |      64.75 |      118.5 |     160.75 |
    | 2024-10-02 |    91 |   143 | 114.65 |     106    |      118.5 |     125    |
    | 2024-10-03 |    97 |   146 | 115.3  |     101.75 |      114.5 |     123.5  |
    | 2024-10-04 |    93 |   168 | 115.1  |     103    |      109.5 |     122.25 |
    | 2024-10-05 |   101 |   146 | 120.98 |     113    |      120   |     129    |
    | 2024-10-06 |    46 |   154 |  98.05 |      68.5  |       80   |     138    |
    | 2024-10-07 |    82 |   143 | 113.69 |      98.75 |      115   |     126.5  |
    | 2024-10-08 |    39 |   108 |  81.69 |      71.5  |       79   |      93.5  |
    
    """



assistant_instruction_str = (
                "You are a diabetic assistant. "
                "Your role is to assist users in better managing type 1 diabetes. "
                "You should use all available knowledge, including both the provided documents "
                "and the broader knowledge you have from your training. "
                "Make sure to reference the documents where relevant, "
                "but do not limit your responses to them if additional context or insights from your training would be helpful."
            )

assistant_instruction = SystemMessage(content=assistant_instruction_str)
assistant_instruction.pretty_print()

messages_lst = [assistant_instruction]
while True:
    query = input(f"Len: {len(messages_lst)} Human: ")
    message, doc_content, question = get_prompt_question(query, True)
    messages_lst = messages_lst + [message]
    
    response = model.invoke(messages_lst)
    model_response = AIMessage(response.content)
    model_response.pretty_print()

    messages_lst = messages_lst + [model_response]
    trimmer.invoke(messages_lst)

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