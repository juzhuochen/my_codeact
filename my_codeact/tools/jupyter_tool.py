"""Jupyter Client Tool 封装为 LangChain Tool"""

import asyncio
import io
import sys
import time
import uuid
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Optional, Tuple, Any
from jupyter_client.manager import KernelManager
from langchain_core.tools import tool


class JupyterSessionManager:
    """管理多个 Jupyter session 的生命周期"""
    
    def __init__(self):
        self.sessions: Dict[str, KernelManager] = {}
        self.clients: Dict[str, Any] = {}
        self.last_activity: Dict[str, float] = {}
        
    def get_or_create_session(self, session_id: str) -> Tuple[KernelManager, Any]:
        """获取或创建 Jupyter session"""
        if session_id not in self.sessions:
            # 创建新的 kernel manager
            km = KernelManager(kernel_name='python3')
            km.start_kernel()
            
            # 获取客户端
            kc = km.client()
            
            self.sessions[session_id] = km
            self.clients[session_id] = kc
            
        self.last_activity[session_id] = time.time()
        return self.sessions[session_id], self.clients[session_id]
    
    def execute_code(self, session_id: str, code: str, timeout: int = 30) -> Dict[str, Any]:
        """在指定 session 中执行代码"""
        km, kc = self.get_or_create_session(session_id)
        
        # 执行代码
        msg_id = kc.execute(code)
        
        outputs = []
        errors = []
        
        start_time = time.time()
        while True:
            try:
                msg = kc.get_iopub_msg(timeout=10)
                
                if msg['parent_header'].get('msg_id') == msg_id:
                    msg_type = msg['msg_type']
                    content = msg['content']
                    
                    if msg_type == 'stream':
                        outputs.append(content['text'])
                    elif msg_type == 'execute_result':
                        outputs.append(str(content['data'].get('text/plain', '')))
                    elif msg_type == 'display_data':
                        outputs.append(str(content['data'].get('text/plain', '')))
                    elif msg_type == 'error':
                        error_msg = '\n'.join(content['traceback'])
                        errors.append(error_msg)
                    elif msg_type == 'status' and content['execution_state'] == 'idle':
                        # 执行完成
                        break
                        
            except Exception as e:
                # 检查是否超时
                if time.time() - start_time > timeout:
                    errors.append(f"代码执行超时 ({timeout}s)")
                    break
                # 其他异常继续等待
                continue
        
        result = {
            'success': len(errors) == 0,
            'output': ''.join(outputs).strip(),
            'errors': errors,
            'session_id': session_id
        }
        
        return result
    
    def cleanup_session(self, session_id: str):
        """清理指定 session"""
        if session_id in self.sessions:
            try:
                self.sessions[session_id].shutdown_kernel()
            except:
                pass
            finally:
                self.sessions.pop(session_id, None)
                self.clients.pop(session_id, None)
                self.last_activity.pop(session_id, None)
    
    def cleanup_inactive_sessions(self, max_idle_time: int = 3600):
        """清理不活跃的 session (默认1小时)"""
        current_time = time.time()
        inactive_sessions = [
            sid for sid, last_time in self.last_activity.items()
            if current_time - last_time > max_idle_time
        ]
        
        for session_id in inactive_sessions:
            self.cleanup_session(session_id)


# 全局 session manager 实例
_session_manager = JupyterSessionManager()


@tool
def execute_jupyter_code(
    code: str, 
    session_id: Optional[str] = None,
    timeout: int = 30
) -> str:
    """
    在持久的 Jupyter 环境中执行 Python 代码
    
    Args:
        code: 要执行的 Python 代码
        session_id: 会话ID，用于维持变量状态。如果为None则自动生成
        timeout: 执行超时时间（秒），默认30秒
        
    Returns:
        执行结果的字符串表示，包含输出和错误信息
    """
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    try:
        result = _session_manager.execute_code(session_id, code, timeout)
        
        if result['success']:
            output = result['output'] if result['output'] else "代码执行完成。"
            return f"执行成功 (session: {session_id}):\n{output}\n"
        else:
            error_msg = '\n'.join(result['errors'])
            return f"执行出错 (session: {session_id}):\n{error_msg}\n"
            
    except Exception as e:
        return f"工具执行异常 (session: {session_id}):\n{str(e)}\n"


@tool  
def list_jupyter_variables(session_id: str) -> str:
    """
    列出指定 Jupyter session 中的所有变量
    
    Args:
        session_id: 会话ID
        
    Returns:
        变量列表的字符串表示
    """
    code = """
import sys
# 获取当前命名空间中的用户定义变量
user_vars = {}
for name, obj in globals().items():
    if not name.startswith('_') and not callable(obj) and not isinstance(obj, type(sys)):
        try:
            user_vars[name] = type(obj).__name__
        except:
            user_vars[name] = 'unknown'

if user_vars:
    for name, type_name in user_vars.items():
        print(f"{name}: {type_name}")
else:
    print("当前 session 中没有用户定义的变量")
"""
    
    return execute_jupyter_code(code, session_id)


@tool
def reset_jupyter_session(session_id: str) -> str:
    """
    重置指定的 Jupyter session，清除所有变量
    
    Args:
        session_id: 要重置的会话ID
        
    Returns:
        重置结果消息
    """
    try:
        _session_manager.cleanup_session(session_id)
        return f"Session {session_id} 已重置"
    except Exception as e:
        return f"重置 session {session_id} 失败: {str(e)}"


# 工具列表，用于 ToolNode
JUPYTER_TOOLS = [
    execute_jupyter_code,
#    list_jupyter_variables, 
#    reset_jupyter_session
]