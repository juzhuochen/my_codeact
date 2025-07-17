"""CodeAct节点函数实现"""

from typing import Callable, Any, Dict, Optional
from langchain_core.language_models import BaseChatModel
from langgraph.types import Command

from ..core.state import CodeActState
from ..utils.code_extractor import extract_code_blocks, validate_code_syntax
from ..utils.prompt_builder import build_error_recovery_prompt


class CodeActNodes:
    """CodeAct节点集合"""

    def __init__(
        self,
        model: BaseChatModel,
        eval_fn: Callable[[str, Dict[str, Any]], tuple[str, Dict[str, Any]]],
        system_prompt: str,
        executor: Optional[Any] = None,  # 新增：用于管理jupyter executor
    ):
        self.model = model
        self.eval_fn = eval_fn
        self.system_prompt = system_prompt
        self.executor = executor  # 用于生命周期管理

    def code_generator(self, state: CodeActState) -> Command:
        """
        代码生成节点 - 调用LLM生成响应并提取代码
        """
        # 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt}] + state[
            "messages"
        ]

        # 如果有错误，添加错误恢复提示
        if state.get("last_error") and state.get("extracted_code"):
            error_prompt = build_error_recovery_prompt(
                state["last_error"], state["extracted_code"]
            )
            messages.append({"role": "user", "content": error_prompt})

        # 调用LLM
        response = self.model.invoke(messages)

        # 提取代码
        extracted_code = extract_code_blocks(response.content)

        # 更新状态并决定下一步
        update_data = {
            "messages": [response],
            "extracted_code": extracted_code,
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

        # 路由决策
        if extracted_code:
            # 验证代码语法
            is_valid, error_msg = validate_code_syntax(extracted_code)
            if not is_valid:
                update_data["last_error"] = error_msg
                update_data["retry_count"] = state.get("retry_count", 0) + 1

                # 如果重试次数过多，结束
                if update_data["retry_count"] > 3:
                    return Command(
                        update={
                            **update_data,
                            "messages": [
                                {
                                    "role": "assistant",
                                    "content": f"代码语法错误过多，无法继续: {error_msg}",
                                }
                            ],
                        }
                    )

                # 重试代码生成
                return Command(goto="code_generator", update=update_data)

            # 代码有效，执行代码
            return Command(goto="code_executor", update=update_data)
        else:
            # 没有代码，任务完成
            return Command(update=update_data)

    def code_executor(self, state: CodeActState) -> Command:
        """
        代码执行节点 - 在jupyter kernel中执行代码
        """
        code = state.get("extracted_code", "")
        existing_context = state.get("execution_context", {})

        try:
            # 使用jupyter executor执行代码
            # 注意：jupyter kernel会自动维护变量状态，所以不需要传递context
            print(code)
            output, new_vars = self.eval_fn(code, existing_context)
            print(output)
            # 更新执行上下文（对于jupyter，这主要是为了兼容性）
            updated_context = {**existing_context, **new_vars}

            return Command(
                goto="result_processor",
                update={
                    "execution_result": output,
                    "execution_context": updated_context,
                    "last_error": None,
                    "retry_count": 0,
                },
            )

        except Exception as e:
            error_msg = str(e)
            return Command(
                goto="error_handler",
                update={"last_error": error_msg, "execution_result": None},
            )

    def result_processor(self, state: CodeActState) -> Command:
        """
        结果处理节点 - 处理执行结果并决定是否继续
        """
        result = state.get("execution_result", "")

        # 将执行结果作为用户消息添加到对话中
        result_message = {
            "role": "user", 
            "content": f"执行结果:\n\n{result}\n"
            }

        # 检查是否达到最大迭代次数
        if state.get("iteration_count", 0) >= state.get("max_iterations", 10):
            return Command(
                goto="iteration_limiter", update={"messages": [result_message]}
            )

        # 继续下一轮生成
        return Command(goto="code_generator", update={"messages": [result_message]})

    def error_handler(self, state: CodeActState) -> Command:
        """
        错误处理节点 - 处理执行错误
        """
        error_msg = state.get("last_error", "")
        retry_count = state.get("retry_count", 0) + 1

        # 如果重试次数过多，终止
        if retry_count > 3:
            error_response = {
                "role": "assistant",
                "content": f"代码执行失败次数过多，终止执行。最后错误: {error_msg}",
            }
            return Command(update={"messages": [error_response]})

        # 否则重新生成代码
        return Command(goto="code_generator", update={"retry_count": retry_count})

    def iteration_limiter(self, state: CodeActState) -> Command:
        """
        迭代限制节点 - 处理达到最大迭代次数的情况
        """
        limit_message = {
            "role": "assistant",
            "content": f"已达到最大迭代次数({state['max_iterations']})，任务可能未完全完成。",
        }
        return Command(update={"messages": [limit_message]})

    def cleanup(self):
        """清理资源，关闭jupyter kernel"""
        if self.executor and hasattr(self.executor, 'shutdown_kernel'):
            self.executor.shutdown_kernel()
    
    def __del__(self):
        """析构函数，确保资源清理"""
        self.cleanup()