"""CodeAct状态定义模块"""

from typing import Any, Optional, TypedDict, Annotated
from langgraph.graph import add_messages


class CodeActState(TypedDict):
    """CodeAct子图的状态定义"""

    # 核心消息流
    messages: Annotated[list, add_messages]

    # CodeAct特有状态
    extracted_code: Optional[str]
    """从LLM响应中提取的Python代码"""

    execution_result: Optional[str]
    """代码执行的结果输出"""

    execution_context: dict[str, Any]
    """持久化的执行环境变量"""

    # 控制流状态
    iteration_count: int
    """当前迭代次数"""

    max_iterations: int
    """最大允许迭代次数"""

    # 工具相关
    available_tools: dict[str, Any]
    """当前可用的工具集合"""

    # 错误处理
    last_error: Optional[str]
    """最后一次执行错误信息"""

    retry_count: int
    """当前错误重试次数"""


# 用于创建初始状态的工厂函数
def create_initial_state(
    messages: list, tools: dict[str, Any] = None, max_iterations: int = 10
) -> CodeActState:
    """创建初始的CodeAct状态"""
    return CodeActState(
        messages=messages,
        extracted_code=None,
        execution_result=None,
        execution_context={},
        iteration_count=0,
        max_iterations=max_iterations,
        available_tools=tools or {},
        last_error=None,
        retry_count=0,
    )
