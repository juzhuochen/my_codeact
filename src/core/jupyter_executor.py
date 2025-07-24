"""Jupyter客户端执行器模块"""

import time
from typing import Dict, Any, Tuple, Optional
from jupyter_client.manager import KernelManager
from jupyter_client.client import KernelClient


class JupyterExecutor:
    """基于jupyter_client的代码执行器"""
    
    def __init__(self, kernel_name: str = 'python3', timeout: int = 30):
        self.kernel_name = kernel_name
        self.timeout = timeout
        self.km: Optional[KernelManager] = None
        self.kc: Optional[KernelClient] = None
        self._is_started = False
    
    def start_kernel(self):
        """启动内核"""
        if self._is_started:
            return
            
        try:
            self.km = KernelManager(kernel_name=self.kernel_name)
            self.km.start_kernel()
            self.kc = self.km.client()
            self._is_started = True
            print(f"Jupyter内核已启动: {self.kernel_name}")
        except Exception as e:
            raise RuntimeError(f"启动Jupyter内核失败: {e}")
    
    def shutdown_kernel(self):
        """关闭内核"""
        if not self._is_started:
            return
            
        try:
            if self.kc:
                self.kc.stop_channels()
            if self.km:
                self.km.shutdown_kernel()
            self._is_started = False
            print("Jupyter内核已关闭")
        except Exception as e:
            print(f"关闭Jupyter内核时出错: {e}")
    
    def execute_code(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """
        执行代码并返回详细结果
        
        Args:
            code: 要执行的Python代码
            
        Returns:
            (格式化的执行结果, 新变量字典)
        """
        if not self._is_started:
            self.start_kernel()
        
        try:
            # 执行代码
            msg_id = self.kc.execute(code)
            
            # 收集不同类型的输出
            stdout_outputs = []  # print输出
            stderr_outputs = []  # 错误输出
            result_outputs = []  # 表达式结果
            display_outputs = []  # display输出
            errors = []
            execution_count = None
            
            # 等待执行完成
            while True:
                try:
                    msg = self.kc.get_iopub_msg(timeout=self.timeout)
                    parent_id = msg['parent_header'].get('msg_id')
                    
                    if parent_id != msg_id:
                        continue
                    
                    msg_type = msg['msg_type']
                    content = msg['content']
                    
                    if msg_type == 'status' and content['execution_state'] == 'idle':
                        # 执行完成
                        break
                    elif msg_type == 'stream':
                        # 区分stdout和stderr
                        stream_name = content.get('name', 'stdout')
                        text = content['text']
                        if stream_name == 'stdout':
                            stdout_outputs.append(text)
                        else:
                            stderr_outputs.append(text)
                    elif msg_type == 'error':
                        # 执行错误
                        error_info = {
                            'name': content['ename'],
                            'value': content['evalue'],
                            'traceback': content['traceback']
                        }
                        errors.append(error_info)
                    elif msg_type == 'execute_result':
                        # 表达式结果
                        execution_count = content.get('execution_count')
                        if 'text/plain' in content['data']:
                            result_outputs.append(content['data']['text/plain'])
                    elif msg_type == 'display_data':
                        # 显示数据（如图表、HTML等）
                        if 'text/plain' in content['data']:
                            display_outputs.append(content['data']['text/plain'])
                            
                except Exception as e:
                    errors.append({'name': 'TimeoutError', 'value': str(e), 'traceback': []})
                    break
            
            # 格式化输出结果
            formatted_result = self._format_execution_result(
                code=code,
                stdout_outputs=stdout_outputs,
                stderr_outputs=stderr_outputs,
                result_outputs=result_outputs,
                display_outputs=display_outputs,
                errors=errors,
                execution_count=execution_count
            )
            
            # 如果有错误，抛出异常
            if errors:
                error_details = []
                for error in errors:
                    if isinstance(error, dict):
                        error_details.append(f"{error['name']}: {error['value']}")
                        if error.get('traceback'):
                            error_details.extend(error['traceback'])
                    else:
                        error_details.append(str(error))
                raise RuntimeError('\n'.join(error_details))
            
            # 获取变量状态
            new_vars = self._get_variables()
            
            return formatted_result, new_vars
            
        except Exception as e:
            # 重新抛出异常，让上层处理
            raise RuntimeError(f"代码执行失败: {e}")
    
    def _format_execution_result(
        self, 
        code: str,
        stdout_outputs: list,
        stderr_outputs: list, 
        result_outputs: list,
        display_outputs: list,
        errors: list,
        execution_count: int = None
    ) -> str:
        """格式化执行结果为易读格式"""
        
        result_parts = []
        
        # 1. 显示执行的代码
        result_parts.append("📝 **执行代码:**")
        result_parts.append("```python")
        result_parts.append(code.strip())
        result_parts.append("```")
        result_parts.append("")
        
        # 2. 显示执行计数（如果有）
        if execution_count is not None:
            result_parts.append(f"🔢 **执行计数:** [{execution_count}]")
            result_parts.append("")
        
        # 3. 显示标准输出
        if stdout_outputs:
            result_parts.append("📤 **输出结果:**")
            result_parts.append("```")
            result_parts.append(''.join(stdout_outputs).strip())
            result_parts.append("```")
            result_parts.append("")
        
        # 4. 显示表达式结果
        if result_outputs:
            result_parts.append("💡 **返回值:**")
            result_parts.append("```")
            result_parts.append('\n'.join(result_outputs).strip())
            result_parts.append("```")
            result_parts.append("")
        
        # 5. 显示display输出
        if display_outputs:
            result_parts.append("🎨 **显示输出:**")
            result_parts.append("```")
            result_parts.append('\n'.join(display_outputs).strip())
            result_parts.append("```")
            result_parts.append("")
        
        # 6. 显示stderr（警告等）
        if stderr_outputs:
            result_parts.append("⚠️ **警告信息:**")
            result_parts.append("```")
            result_parts.append(''.join(stderr_outputs).strip())
            result_parts.append("```")
            result_parts.append("")
        
        # 7. 如果没有任何输出，显示执行完成
        if not (stdout_outputs or result_outputs or display_outputs):
            result_parts.append("✅ **代码执行完成** (无输出)")
            result_parts.append("")
        
        return '\n'.join(result_parts).strip()
    
    def _get_variables(self) -> Dict[str, Any]:
        """
        获取当前kernel中的变量（简化实现）
        
        在实际使用中，jupyter kernel会自动维护变量状态，
        这里返回空字典，因为变量已经在kernel中持久化了
        """
        # 简化实现：jupyter kernel自动维护变量状态
        # 如果需要获取变量列表，可以执行 who 命令
        return {}
    
    def is_alive(self) -> bool:
        """检查内核是否仍然活跃"""
        if not self._is_started or not self.km:
            return False
        return self.km.is_alive()
    
    def restart_kernel(self):
        """重启内核"""
        print("重启Jupyter内核...")
        self.shutdown_kernel()
        time.sleep(1)  # 等待清理完成
        self.start_kernel()
    
    def __enter__(self):
        """上下文管理器支持"""
        self.start_kernel()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器支持"""
        self.shutdown_kernel()


def create_jupyter_eval_fn(kernel_name: str = 'python3', timeout: int = 30):
    """
    创建基于jupyter_client的代码执行函数
    
    Args:
        kernel_name: 内核名称
        timeout: 执行超时时间
        
    Returns:
        符合CodeAct接口的执行函数
    """
    # 创建全局执行器实例
    executor = JupyterExecutor(kernel_name=kernel_name, timeout=timeout)
    
    def eval_fn(code: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        执行Python代码的函数
        
        Args:
            code: 要执行的代码
            context: 执行上下文（jupyter中会自动维护，这里忽略）
            
        Returns:
            (输出结果, 新变量字典)
        """
        try:
            return executor.execute_code(code)
        except Exception as e:
            # 如果内核死了，尝试重启
            if not executor.is_alive():
                try:
                    executor.restart_kernel()
                    return executor.execute_code(code)
                except Exception as restart_error:
                    raise RuntimeError(f"内核重启失败: {restart_error}")
            else:
                raise e
    
    # 返回函数和执行器，以便外部管理生命周期
    return eval_fn, executor