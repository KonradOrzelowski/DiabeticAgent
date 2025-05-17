from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from langchain.agents.react.agent import create_react_agent
from langchain.agents import AgentExecutor

prompt_template = PromptTemplate(
    # input_variables=["tools", "tool_names", "input", "agent_scratchpad", "chat_history"],
    template="""
        You are a diabetic assistant. 
        Your role is to assist users in managing type 1 diabetes.
        {chat_history}
        You can use the following tools:
        {tools}

        When answering, follow this format exactly:
        Thought: You could think about what to do
        Action: You may take one of these actions if you think so from [{tool_names}]
        Action Input: Firstly, decide if you need to use a tools

        Then, after observing the result of the action, continue the thought process and provide a final answer if ready.

        Begin!

        Question: {input}

        {agent_scratchpad}
    """
    )


class Agent:
    def __init__(self, model_name, tools, verbose = True):
        self.model_name = model_name
        self.model = ChatOpenAI(model_name=self.model_name)

        self.tools = tools
        self.tool_names = [tool.name for tool in self.tools]

        self.verbose = verbose

        self.session_id = "test-session"

        self.memory = InMemoryChatMessageHistory(session_id=self.session_id)

        self.prompt_template = prompt_template
        self.prompt_template.partial(tools = self.tools, tool_names = self.tool_names)

        self.agent = create_react_agent(llm=self.model,
                                        tools=self.tools,
                                        prompt=self.prompt_template)


        self.agent_executor = AgentExecutor(
                                    agent=self.agent, tools=self.tools, verbose=self.verbose,
                                    return_intermediate_steps=True,
                                    handle_parsing_errors=True
                                    )

        self.agent_with_chat_history = RunnableWithMessageHistory(
            self.agent_executor,
            lambda session_id: self.memory,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="output"  # Ensure this key matches the output of your agent
        )



