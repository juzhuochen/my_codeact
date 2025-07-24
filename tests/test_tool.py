

from typing_extensions import Optional, Literal, TypedDict, Annotated, cast
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
    current_tool_calls: Optional[list[ToolCall]]
    last_observation: Optional[str] 
#    reflection: Optional[str]

    #code: Optional[str]
    #exec_result: Optional[str]

llm = init_chat_model("ollama:qwen3:32b")

def call_model(state: AgentState) -> Command[Literal["tool_executor", "__end__"]]:
    
    system_prompt =  build_system_prompt()
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = cast(AIMessage, llm.bind_tools(tools=tools).invoke(messages))
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

    tool_calls = state["current_tool_calls"]
    if not tool_calls:
        return Command(
            goto="call_model"
        )
    
    # latest msgs are tool calls
    last_message = state["messages"][-1]

        # 直接调用工具节点，让它处理所有错误
    result = tool_node.invoke({"messages": [last_message]})
        
        # 处理返回结果
    if isinstance(result, dict) and "messages" in result:
            tool_messages = result["messages"]
    elif isinstance(result, list):
            tool_messages = result
    else:
            tool_messages = [result]
        
    last_obs = tool_messages[-1].content if tool_messages else None



    return Command(
        update={
            "messages": tool_messages, # tool messages
            "current_tool_calls": None,
            "last_observation": last_obs
            },
            goto="call_model"
        )



from langgraph.graph import StateGraph

agent = StateGraph(AgentState)
agent.add_node("call_model",call_model)
agent.add_node("tool_executor", tool_executor)

agent.set_entry_point("call_model")



def create_agent():
   return  agent.compile()

# used this compiled graph in langgraph cli tool
codeact = create_agent()


