from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_core.messages import HumanMessage, SystemMessage, trim_messages
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

from process_pdf import ProcessPDF

def load_faiss_index(file_name):
    pp = ProcessPDF(file_name)
    pp.load_vectorestore()
    return pp.vectorstore

faiss_index = load_faiss_index('dr_bernstein_diabetes_solution')
faiss_index_1 = load_faiss_index('standards_of_care_2025')

faiss_index.merge_from(faiss_index_1)

model = ChatOpenAI(model_name="gpt-4o-mini")

def get_promt_question(question):

    docs = faiss_index.similarity_search(question)
    doc_content = {}

    for idx, doc in enumerate(docs):
        doc_content[f'doc_{idx}'] = doc.page_content
        # print(f"{f'Doc {idx}':-^50}")
        # lines = doc.page_content.split('\n')

        # # Print each non-empty line
        # for line in lines:
        #     if line.strip():
        #         print(line)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a diabetic assistant. "
                "Your role is to assist users in better managing type 1 diabetes. "
                "You should use all available knowledge, including both the provided documents "
                "and the broader knowledge you have from your training. "
                "Make sure to reference the documents where relevant, "
                "but do not limit your responses to them if additional context or insights from your training would be helpful."
            )
        },
        {
            "role": "user",
            "content": f"Helpful documents:\n\n{doc_content}\n\nPlease respond to the following question:\n\n{question}"
        }
    ]

    return messages

# messages = get_promt_question(question)
# lst = [SystemMessage(content = messages[0]['content']), HumanMessage(content = messages[1]['content'])]
# print()

language = "English"

trimmer = trim_messages(
    max_tokens=65,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)
messages_lst = [
    
]


while True:
    query = input("Human: ")
    messages = get_promt_question(query)
    lst = [SystemMessage(content = messages[0]['content']), HumanMessage(content = messages[1]['content'])]

    messages_lst = messages_lst + lst
    
    response = model.invoke(messages_lst)

    print(response.content)
    messages_lst = messages_lst + [SystemMessage(content=response.content)]
    trimmer.invoke(messages_lst)