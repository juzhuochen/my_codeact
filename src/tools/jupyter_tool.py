import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from jupyter_client.manager import KernelManager
from langchain_core.tools import tool
from src.config.jupyter_config import JupyterConfig


class JupyterExecutor:
    """Jupyter 代码执行器"""

    def __init__(self, config: JupyterConfig):
        self.config = config
        self.sessions: Dict[str, KernelManager] = {}
        self.clients: Dict[str, Any] = {}
        self.injected_sessions: Set[str] = set()

    def _resolve_paths(self, paths: List[str]) -> List[str]:
        """解析并验证路径"""
        resolved = []
        for path_str in paths:
            try:
                path = Path(path_str).resolve()
                if path.exists() and path.is_dir():
                    resolved.append(str(path))
            except Exception:
                continue
        return resolved

    def _generate_injection_code(self, session_id: str) -> str:
        """生成模块注入代码"""
        if session_id in self.injected_sessions:
            return ""

        paths = self._resolve_paths(self.config.get_module_paths())
        imports = self.config.get_auto_imports()

        if not paths and not imports:
            return ""

        code_parts = []

        # 路径注入
        if paths:
            code_parts.append("import sys")
            for path in paths:
                code_parts.append(
                    f"if {path!r} not in sys.path: sys.path.insert(0, {path!r})"
                )

        # 自动导入
        code_parts.extend(imports)

        if code_parts:
            self.injected_sessions.add(session_id)
            return "\n".join(code_parts) + "\n"

        return ""

    def _get_or_create_session(self, session_id: str) -> tuple[KernelManager, Any]:
        """获取或创建 session"""
        if session_id not in self.sessions:
            km = KernelManager(kernel_name="python3")
            km.start_kernel()
            self.sessions[session_id] = km
            self.clients[session_id] = km.client()

        return self.sessions[session_id], self.clients[session_id]

    def execute(
        self, code: str, session_id: Optional[str] = None, timeout: int = 30
    ) -> Dict[str, Any]:
        """执行代码"""
        if session_id is None:
            session_id = str(uuid.uuid4())

        km, kc = self._get_or_create_session(session_id)

        # 组合注入代码和用户代码
        injection_code = self._generate_injection_code(session_id)
        full_code = injection_code + code

        # 执行代码
        msg_id = kc.execute(full_code)

        outputs = []
        errors = []
        start_time = time.time()

        while True:
            try:
                msg = kc.get_iopub_msg(timeout=5)
                if msg["parent_header"].get("msg_id") != msg_id:
                    continue

                msg_type = msg["msg_type"]
                content = msg["content"]

                if msg_type == "stream":
                    outputs.append(content["text"])
                elif msg_type in ("execute_result", "display_data"):
                    outputs.append(str(content["data"].get("text/plain", "")))
                elif msg_type == "error":
                    errors.append("\n".join(content["traceback"]))
                elif msg_type == "status" and content["execution_state"] == "idle":
                    break

            except Exception:
                if time.time() - start_time > timeout:
                    errors.append(f"执行超时 ({timeout}s)")
                    break

        return {
            "success": len(errors) == 0,
            "output": "".join(outputs).strip(),
            "errors": errors,
            "session_id": session_id,
        }

    def reset_session(self, session_id: str):
        """重置 session"""
        if session_id in self.sessions:
            try:
                self.sessions[session_id].shutdown_kernel()
            except:
                pass
            finally:
                self.sessions.pop(session_id, None)
                self.clients.pop(session_id, None)
                self.injected_sessions.discard(session_id)


# 全局配置和执行器
_config = JupyterConfig()
_executor = JupyterExecutor(_config)


@tool
def execute_jupyter_code(
    code: str, session_id: Optional[str] = None, timeout: int = 30
) -> str:
    """
    在持久的 Jupyter 环境中执行 Python 代码

    Args:
        code: 要执行的 Python 代码
        session_id: 会话ID，用于维持变量状态。如果为None则自动生成
        timeout: 执行超时时间（秒），默认30秒

    Returns:
        执行结果的字符串表示
    """
    try:
        result = _executor.execute(code, session_id, timeout)

        if result["success"]:
            output = result["output"] or "代码执行完成"
            return f"✓ 执行成功 (session: {result['session_id']}):\n{output}"
        else:
            errors = "\n".join(result["errors"])
            return f"✗ 执行失败 (session: {result['session_id']}):\n{errors}"

    except Exception as e:
        return f"✗ 工具异常: {str(e)}"


@tool
def reset_jupyter_session(session_id: str) -> str:
    """
    重置指定的 Jupyter session

    Args:
        session_id: 要重置的会话ID

    Returns:
        重置结果消息
    """
    try:
        _executor.reset_session(session_id)
        return f"✓ Session {session_id} 已重置"
    except Exception as e:
        return f"✗ 重置失败: {str(e)}"


# === 开发者配置接口 ===


def configure_jupyter_modules(
    module_paths: Optional[List[str]] = None,
    auto_imports: Optional[List[str]] = None,
    config_file: str = "jupyter_config.json",
):
    """
    配置 Jupyter 模块环境

    Args:
        module_paths: 自定义模块路径列表
        auto_imports: 自动导入语句列表
        config_file: 配置文件路径
    """
    global _config, _executor

    # 重新创建配置对象
    _config = JupyterConfig(config_file)

    if module_paths is not None:
        _config.set_module_paths(module_paths)

    if auto_imports is not None:
        _config.set_auto_imports(auto_imports)

    # 重新创建执行器
    _executor = JupyterExecutor(_config)

    print(f"✓ Jupyter 配置已更新")
    print(f"  模块路径: {_config.get_module_paths()}")
    print(f"  自动导入: {_config.get_auto_imports()}")


def get_jupyter_config() -> Dict[str, Any]:
    """获取当前 Jupyter 配置"""
    return {
        "module_paths": _config.get_module_paths(),
        "auto_imports": _config.get_auto_imports(),
        "config_file": _config.config_file,
    }


# 工具列表
JUPYTER_TOOLS = [execute_jupyter_code, reset_jupyter_session]
