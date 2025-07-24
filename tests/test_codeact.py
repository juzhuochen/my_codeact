from my_codeact.tools.jupyter_tool import configure_jupyter_modules
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode


configure_jupyter_modules(
    module_paths=["my_codeact.test_data"],
    auto_imports=["import cloudpss",]
)
llm = init_chat_model("ollama:qwen3:32b")

from my_codeact.tools.jupyter_tool import execute_jupyter_code
code = """
import S_S_SyncComp as SA

"""
llm_with_tool = llm.bind_tools([execute_jupyter_code])

response = llm_with_tool.invoke("调用工具执行代码:\n" + code)

tool_node = ToolNode([execute_jupyter_code])
tool_resp = tool_node.invoke({"messages": [response]})

print(tool_resp)
