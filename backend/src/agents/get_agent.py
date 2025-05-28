from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from langchain.agents.react.agent import create_react_agent
from langchain.agents import AgentExecutor

prompt_template = PromptTemplate(
    template="""
        You are a diabetic assistant. 
        Your role is to assist users in managing type 1 diabetes.

        {chat_history}

        You can use the following tools:
        {tools}

        You must respond by doing **only one of the following**:
        - If you need more information, respond with:
            Thought: Describe your reasoning.
            Action: Choose one tool from [{tool_names}]
            Action Input: What you want to use the tool for.
        - If you are ready to answer the question, respond with:
            Final Answer: [your answer]

        ⚠️ Important rules:
        - Never provide both an Action and Final Answer at the same time.
        - Once you have enough information or the tools are not useful, you **must** give a Final Answer.
        - Repeating the same tools or actions multiple times is not allowed.

        Begin!

        Question: {input}

        {agent_scratchpad}


    """
    )


class Agent:
    def __init__(self, model_name, tools, verbose = True, max_iterations = 5):
        self.model_name = model_name
        self.model = ChatOpenAI(model_name=self.model_name)

        self.tools = tools

        tools_str = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
        tool_names_str = ", ".join([tool.name for tool in self.tools])

        self.verbose = verbose
        self.max_iterations = max_iterations

        self.session_id = "test-session"

        self.memory = InMemoryChatMessageHistory(session_id=self.session_id)

        self.prompt_template = prompt_template.partial(tools = tools_str, tool_names = tool_names_str)

        self.agent = create_react_agent(llm=self.model,
                                        tools=self.tools,
                                        prompt=self.prompt_template)


        self.agent_executor = AgentExecutor(
                                    agent=self.agent, tools=self.tools, verbose=self.verbose,
                                    return_intermediate_steps=True,
                                    handle_parsing_errors=True,
                                    max_iterations=self.max_iterations
                                    )

        self.agent_with_chat_history = RunnableWithMessageHistory(
            self.agent_executor,
            lambda session_id: self.memory,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="output"
        )



