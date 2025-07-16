"""提示构建工具模块"""

import inspect
from typing import Optional, Dict, Any
from langchain_core.tools import StructuredTool


def build_system_prompt(
    tools: Dict[str, Any],
    base_prompt: Optional[str] = None,
    include_examples: bool = True,
) -> str:
    """
    构建CodeAct的系统提示

    Args:
        tools: 可用工具字典
        base_prompt: 基础提示文本
        include_examples: 是否包含示例

    Returns:
        完整的系统提示
    """
    prompt_parts = []

    # 基础提示
    if base_prompt:
        prompt_parts.append(base_prompt)

    # 核心指令
    core_instruction = """
你是一个CodeAct智能助手。你需要通过编写和执行Python代码来完成任务。

规则:
1. 使用Python代码块(```python)来执行操作
2. 使用print()输出你想要展示给用户的结果
3. 可以引用之前代码片段中定义的变量
4. 如果不需要执行代码，直接用文本回复用户

除了Python标准库，你还可以使用以下工具函数:
"""
    prompt_parts.append(core_instruction)

    # 工具描述
    if tools:
        tool_descriptions = []
        for tool_name, tool_func in tools.items():
            try:
                sig = str(inspect.signature(tool_func))
                doc = tool_func.__doc__ or "无描述"
                tool_desc = f'def {tool_name}{sig}:\n    """{doc}"""\n    ...'
                tool_descriptions.append(tool_desc)
            except Exception:
                # 如果获取签名失败，提供基本信息
                tool_descriptions.append(f"# {tool_name}: 可用工具函数")

        prompt_parts.append("\n".join(tool_descriptions))

    # 示例(可选)
    if include_examples:
        examples = """

示例:
用户: 计算1到10的平方和
助手: ```python
squares = [i**2 for i in range(1, 11)]
result = sum(squares)
print(f"1到10的平方和是: {result}")
```

用户: 获取当前时间
助手: ```python
import datetime
now = datetime.datetime.now()
print(f"当前时间: {now}")
```
"""
        prompt_parts.append(examples)

    return "\n".join(prompt_parts)


def build_error_recovery_prompt(error_msg: Optional[str], code: Optional[str]) -> str:
    """
    构建错误恢复提示

    Args:
        error_msg: 错误信息
        code: 出错的代码

    Returns:
        错误恢复提示
    """
    return f"""
执行代码时发生错误:

错误信息: {error_msg}

出错代码:
```python
{code}
```

请分析错误原因并提供修正后的代码。
"""
