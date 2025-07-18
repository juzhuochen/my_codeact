"""提示构建工具模块"""

import inspect
from typing import Optional, Dict, Any
from langchain_core.tools import StructuredTool


def build_system_prompt(
    tools: Optional[Dict[str, Any]],
    base_prompt: Optional[str] = None,
) -> str:
    """
    构建CodeAct的系统提示

    Args:
        tools: 可用工具字典
        base_prompt: 基础提示文本

    Returns:
        完整的系统提示
    """
    prompt_parts = []

    # 基础提示
    if base_prompt:
        prompt_parts.append(base_prompt)

    # 核心指令
    core_instruction = """
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
"""
    prompt_parts.append(core_instruction)
    # other instruction
    return prompt_parts
