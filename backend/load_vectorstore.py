from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = OpenAIEmbeddings()

new_vector_store = FAISS.load_local(
    "faiss_index", embeddings, allow_dangerous_deserialization=True
)

docs = new_vector_store.similarity_search("High sugar values during fasting")

for idx, doc in enumerate(docs):
    # Split by \n
    print(f"{f'Doc {idx}':-^50}")
    lines = doc.page_content .split('\n')

    # Print each line separately
    for line in lines:
        if line.strip():  # Skip empty lines
            print(line)



