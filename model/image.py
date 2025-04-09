from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessage, trim_messages
from langchain_openai import ChatOpenAI


model = ChatOpenAI(model_name="gpt-4o-mini")

import base64

import httpx

with open("Figure_1.png", "rb") as image_file:
    Figure_1 = base64.b64encode(image_file.read()).decode("utf-8")

with open("Figure_2.png", "rb") as image_file:
    Figure_2 = base64.b64encode(image_file.read()).decode("utf-8")

with open("Figure_3.png", "rb") as image_file:
    Figure_3 = base64.b64encode(image_file.read()).decode("utf-8")

language = "English"

trimmer = trim_messages(
    max_tokens=65,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)
messages = [
    
]
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.messages import HumanMessage

# prompt_template = ChatPromptTemplate([
#     ("system", "You are a helpful assistant diabetes"),
#     MessagesPlaceholder("msgs")
# ])

while True:
    query = input("Human: ")


    message = HumanMessage(
    content=[
        {"type": "text", "text": query},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{Figure_1}"},
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{Figure_2}"},
        },
                {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{Figure_3}"},
        },
    ],
    )
    messages = messages + [message]
    
    response = model.invoke(messages)

    print(response.content)
    messages = messages + [SystemMessage(content=response.content)]
    trimmer.invoke(messages)