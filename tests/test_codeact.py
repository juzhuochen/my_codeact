from my_codeact import create_codeact_agent
from langchain_ollama import ChatOllama
from tests.test_data.math import add_numbers, multiply_numbers

llm = ChatOllama(model="qwen3:0.6b")
tools = [add_numbers, multiply_numbers]

agent = create_codeact_agent(model=llm, tools=tools, base_prompt="你是一个计算助手")
