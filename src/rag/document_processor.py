from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain_core.documents import Document
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader,PythonLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Optional, Type
import logging
from pathlib import Path

from src.config import rag_config
logger = logging.getLogger(__name__)


from src.config import rag_config


class DocumentProcessor:
    """
    异步文档处理器。

    """

    def __init__(self, config: rag_config.RAGConfig) -> None:
        self.config = config

        # 扩展名 → Loader 映射
        self.loader_registry: Dict[str, Type] = {
            ".py": PythonLoader,
            ".md": UnstructuredMarkdownLoader,
            # 可以根据需要添加更多类型
            # '.txt': TextLoader,
            # '.pdf': PyPDFLoader,
            # '.docx': Docx2txtLoader,
        }
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )

    async def process_directory_async(self, dir_path: str | None = None) -> List[Document]:
        """异步处理整个目录"""
        root = str(dir_path or self.config.document_directory)
        if not Path(root).exists():
            return []

        tasks = [
            self._load_and_split(root, suffix, loader_cls)
            for suffix, loader_cls in self.loader_registry.items()
        ]
        chunk_lists = await asyncio.gather(*tasks)
        return [chunk for lst in chunk_lists for chunk in lst]

    async def _load_and_split(
        self, root: str, pattern: str, loader_cls: Type
    ) -> List[Document]:
        """一次性异步加载并切分某类文件"""
        loader = DirectoryLoader(
            root,
            glob=f"**/*{pattern}",
            loader_cls=loader_cls,
            recursive=True,
        )
        docs = await loader.aload()
        return self.text_splitter.split_documents(docs)