"""代码提取工具模块"""

import re
from typing import Optional

# 代码块匹配模式
BACKTICK_PATTERN = r"(?:^|\n)```(.*?)(?:```(?:\n|$))"


def extract_code_blocks(text: str) -> str:
    """
    从文本中提取并合并所有代码块

    Args:
        text: 包含代码块的文本

    Returns:
        合并后的可执行代码字符串
    """
    code_blocks = re.findall(BACKTICK_PATTERN, text, re.DOTALL)

    if not code_blocks:
        return ""

    processed_blocks = []
    for block in code_blocks:
        block = block.strip()

        # 移除语言标识符
        lines = block.split("\n")
        if lines and (not lines[0].strip() or " " not in lines[0].strip()):
            block = "\n".join(lines[1:])

        if block.strip():  # 只添加非空代码块
            processed_blocks.append(block)

    return "\n\n".join(processed_blocks)


def validate_code_syntax(code: str) -> tuple[bool, Optional[str]]:
    """
    验证Python代码语法

    Args:
        code: 要验证的Python代码

    Returns:
        (是否有效, 错误信息)
    """
    if not code.strip():
        return False, "代码为空"

    try:
        compile(code, "<string>", "exec")
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    except Exception as e:
        return False, f"编译错误: {e}"


def has_print_statements(code: str) -> bool:
    """检查代码是否包含输出语句"""
    # 简单检查是否有print语句
    return "print(" in code or "print " in code
