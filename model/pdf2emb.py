from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
# 3. Load and split the PDF document
pdf_path = "checking_blood_glucose.pdf"
loader = PyPDFLoader(pdf_path)
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)

# Store splits
vectorstore = FAISS.from_documents(documents=docs, embedding=OpenAIEmbeddings())

# LLM
llm = ChatOpenAI(model_name="gpt-4o-mini")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
from langchain_core.prompts import PromptTemplate


prompt = PromptTemplate.from_template("""
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the anser base on  context its okay make a note and gimme answer
Question: {question} 
Context: {context} 
Answer:
""")
context_chain = vectorstore.as_retriever() | format_docs

qa_chain = (
    {
        "context": context_chain,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

print(qa_chain.invoke("What are sugar level i shoud target?"))