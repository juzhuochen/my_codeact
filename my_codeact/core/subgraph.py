"""CodeAct子图实现"""

from typing import Callable, Dict, Any, Optional, Sequence, Union
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import StructuredTool
from langchain_core.tools import tool as create_tool
from langgraph.graph import StateGraph, START, END

from .state import CodeActState, create_initial_state
from .nodes import CodeActNodes
from ..utils.prompt_builder import build_system_prompt


def create_codeact_subgraph(
    model: BaseChatModel,
    tools: Sequence[Union[StructuredTool, Callable]],
    eval_fn: Callable[[str, Dict[str, Any]], tuple[str, Dict[str, Any]]],
    *,
    max_iterations: int = 10,
    base_prompt: Optional[str] = None,
    include_examples: bool = True,
) -> StateGraph:
    """
    创建CodeAct子图

    Args:
        model: 语言模型
        tools: 工具列表
        eval_fn: 代码执行函数
        max_iterations: 最大迭代次数
        base_prompt: 基础提示
        include_examples: 是否包含示例

    Returns:
        配置好的StateGraph
    """

    # 标准化工具格式
    structured_tools = []
    for tool in tools:
        if isinstance(tool, StructuredTool):
            structured_tools.append(tool)
        else:
            structured_tools.append(create_tool(tool))

    # 构建工具上下文
    tools_context = {tool.name: tool.func for tool in structured_tools}

    # 构建系统提示
    system_prompt = build_system_prompt(
        tools=tools_context, base_prompt=base_prompt, include_examples=include_examples
    )

    # 创建节点实例
    nodes = CodeActNodes(model=model, eval_fn=eval_fn, system_prompt=system_prompt)

    # 创建状态图
    workflow = StateGraph(CodeActState)

    # 添加节点
    workflow.add_node("code_generator", nodes.code_generator)
    workflow.add_node("code_executor", nodes.code_executor)
    workflow.add_node("result_processor", nodes.result_processor)
    workflow.add_node("error_handler", nodes.error_handler)
    workflow.add_node("iteration_limiter", nodes.iteration_limiter)

    # 定义边 - 使用Command API进行动态路由，所以这里只定义固定边
    workflow.add_edge(START, "code_generator")

    # 节点之间的路由通过Command API在节点内部处理
    # 所有没有显式goto的Command都会流向END

    return workflow


def create_simple_eval_fn() -> (
    Callable[[str, Dict[str, Any]], tuple[str, Dict[str, Any]]]
):
    """
    创建一个简单的代码执行函数(仅用于演示，生产环境需要安全的沙盒)

    Returns:
        代码执行函数
    """
    import io
    import sys
    from contextlib import redirect_stdout

    def eval_fn(code: str, context: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """
        执行Python代码并返回输出和更新的变量

        警告: 这是一个简单实现，不适用于生产环境！
        生产环境应该使用安全的沙盒执行环境。
        """
        # 创建输出捕获
        output_buffer = io.StringIO()

        # 准备执行环境
        exec_globals = {"__builtins__": __builtins__}
        exec_locals = context.copy()

        try:
            # 捕获输出并执行代码
            with redirect_stdout(output_buffer):
                exec(code, exec_globals, exec_locals)

            # 获取输出
            output = output_buffer.getvalue()

            # 提取新变量(排除内置变量和函数)
            new_vars = {}
            for key, value in exec_locals.items():
                if not key.startswith("_") and key not in context:
                    # 只保存可序列化的基本类型
                    if isinstance(
                        value, (int, float, str, list, dict, bool, type(None))
                    ):
                        new_vars[key] = value

            return output.strip() if output.strip() else "代码执行完成", new_vars

        except Exception as e:
            raise RuntimeError(f"代码执行错误: {str(e)}")

    return eval_fn


# TODO: use Secure eval function
def secure_eval_fn():
    """docker"""
    pass


# 便捷函数用于快速创建和使用
def create_codeact_agent(
    model: BaseChatModel,
    tools: Sequence[Union[StructuredTool, Callable]] = None,
    eval_fn: Optional[Callable] = None,
    **kwargs,
):
    """
    便捷函数：创建一个可直接使用的CodeAct智能体

    Args:
        model: 语言模型
        tools: 工具列表
        eval_fn: 代码执行函数，如果为None则使用简单实现
        **kwargs: 其他参数传递给create_codeact_subgraph

    Returns:
        编译好的智能体
    """
    if tools is None:
        tools = []

    if eval_fn is None:
        eval_fn = create_simple_eval_fn()

    # 创建子图
    subgraph = create_codeact_subgraph(
        model=model, tools=tools, eval_fn=eval_fn, **kwargs
    )

    # 编译并返回
    return subgraph.compile()
