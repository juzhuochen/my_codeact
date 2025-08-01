"""Jupyter Client Tool 实现"""

import json
import os
from typing import Dict, List, Any


class JupyterConfig:
    """Jupyter 配置管理 - 开发者直接操作"""

    def __init__(self, config_file: str = "jupyter_config.json"):
        self.config_file = config_file
        self._config = self._load_or_create_config()

    def _load_or_create_config(self) -> Dict[str, Any]:
        """加载或创建配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 创建默认配置
        default_config = {"module_paths": [""], "auto_imports": []}
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict[str, Any]):
        """保存配置文件"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def set_module_paths(self, paths: List[str]):
        """设置模块路径"""
        self._config["module_paths"] = paths
        self._save_config(self._config)

    def add_module_path(self, path: str):
        """添加单个模块路径"""
        if path not in self._config["module_paths"]:
            self._config["module_paths"].append(path)
            self._save_config(self._config)

    def set_auto_imports(self, imports: List[str]):
        """设置自动导入语句"""
        self._config["auto_imports"] = imports
        self._save_config(self._config)

    def get_module_paths(self) -> List[str]:
        """获取模块路径"""
        return self._config.get("module_paths", [])

    def get_auto_imports(self) -> List[str]:
        """获取自动导入语句"""
        return self._config.get("auto_imports", [])
