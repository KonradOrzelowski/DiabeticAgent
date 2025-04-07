from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessage, trim_messages
from langchain_openai import ChatOpenAI


model = ChatOpenAI(model_name="gpt-4o-mini")

import base64

import httpx

with open("Figure_1.png", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

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
trimmer.invoke(messages)

while True:
    query = input("Human: ")


    message = HumanMessage(
    content=[
        {"type": "text", "text": query},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
        },
    ],
    )
    messages = messages + [message]
    response = model.invoke(messages)

    print(response.content)
    messages = messages + [SystemMessage(content=response.content)]
    print(len(messages))