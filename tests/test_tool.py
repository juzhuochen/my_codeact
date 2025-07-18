

from typing import Optional, Literal, TypedDict, Annotated, cast
from langgraph.types import Command
from langgraph.graph import add_messages
from langchain_core.messages import ToolCall, HumanMessage,AIMessage, ToolMessage, AnyMessage,SystemMessage
from my_codeact.utils.prompt_builder import build_system_prompt
from langchain.chat_models import init_chat_model


from langgraph.prebuilt import ToolNode
# get all tools
# tool defined by "@tool"
from my_codeact.tools.jupyter_tool import JUPYTER_TOOLS
tools = JUPYTER_TOOLS
tool_node = ToolNode(tools)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    current_tool_calls: Optional[ToolCall]
    last_observation: Optional[str] 
#    reflection: Optional[str]

    #code: Optional[str]
    #exec_result: Optional[str]


def call_model(state: AgentState) -> Command[Literal["tool_executor", "__end__"]]:
    
    messages = state["messages"]

    llm = init_chat_model("ollama:mistral:7b")

    response: AIMessage = cast(AIMessage,llm.invoke(messages))
    tool_calls: Optional[list[ToolCall]] = response.tool_calls

    if tool_calls:
        # goto tool node

        return Command(
            update={
                "messages": response,
                "current_tool_calls": tool_calls
            },
            goto="tool_executor"
        )
    else:
        # to end
        return Command(
            update={
                "messages": response,
            },
            goto="__end__"
        )
    
def tool_executor(state: AgentState) :
    messages = state["messages"]
    # latest msgs are tool call
    tool_calls = state["current_tool_calls"]
    observation = [] # also could be reflection
    if not tool_calls:
        return Command(
            goto="call_model"
        )
    # execute the tools
    for tool_call in tool_calls:
        result: ToolMessage = tool_node.invoke(tool_call)
        observation.append(result)


    return Command(
        update={
            "messages": observation,
            "current_tool_calls": None,
            "last_observation": observation[-1].content if observation else None
            },
            goto="call_model"
        )


from langgraph.graph import StateGraph

agent = StateGraph(AgentState)
agent.add_node("call_model",call_model)
agent.add_node("tool_executor", tool_executor)

agent.set_entry_point("call_model")



# --------------
# 使用示例
initial_state: AgentState = {
    "messages": [HumanMessage(content=""""
#角色：
你是一个智能助手。你需要通过编写和执行Python代码来完成任务。

执行规则:
1. 使用Python代码块(```python)来执行操作
2. 系统会显示完整的执行过程，包括代码、输出、返回值等
3. 可以引用之前代码片段中定义的变量
4. 如果不需要执行代码，直接用文本回复用户
5. 建议在代码中使用print()来输出中间结果，便于调试

输出说明:
- 📝 显示实际执行的代码
- 📤 显示print()等标准输出  
- 💡 显示表达式的返回值
- 🎨 显示matplotlib图表等可视化内容
- ⚠️ 显示警告信息
- ✅ 表示代码执行完成

    请帮我计算 1到9019的和""")],
    "current_tool_calls": None,
    "last_observation": None
}



#print(agent.compile().invoke(initial_state))
def create_agent():
   return  agent.compile()



for step in agent.compile().stream(initial_state):
   print(step)


    
