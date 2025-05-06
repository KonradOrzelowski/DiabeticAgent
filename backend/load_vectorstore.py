from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from process_pdf import ProcessPDF

def load_faiss_index(file_name):
    pp = ProcessPDF(file_name)
    pp.load_vectorestore()
    return pp.vectorstore

faiss_index = load_faiss_index('dr_bernstein_diabetes_solution')
faiss_index_1 = load_faiss_index('standards_of_care_2025')

faiss_index.merge_from(faiss_index_1)

question = "Should I give insulin before I eat? Something like 10 or 20 minutes before a meal?"

docs = faiss_index.similarity_search(question)
doc_content = {}

for idx, doc in enumerate(docs):
    doc_content[f'doc_{idx}'] = doc.page_content
    print(f"{f'Doc {idx}':-^50}")
    lines = doc.page_content.split('\n')

    # Print each non-empty line
    for line in lines:
        if line.strip():
            print(line)

messages = [
    {
        "role": "system",
        "content": (
            "You are a diabetic assistant. "
            "Your role is to assist users in better managing type 1 diabetes. "
            "You may reference the documents provided to answer questions."
        )
    },
    {
        "role": "user",
        "content": f"Helpful documents:\n\n{doc_content}\n\nPlease respond to the following question:\n\n{question}"
    }
]

print(messages)
