import os
from pydantic import BaseModel, Field
from typing import Dict, Any
from dotenv import load_dotenv, find_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if find_dotenv:
    load_dotenv()
    logger.info(f".env 文件已加载")
else:
    logger.warning(".env 文件未找到或加载失败。请确保存在 .env 文件。")


class RAGConfig(BaseModel):
    """RAG 系统配置 - 支持环境变量"""

    # 文档处理配置
    document_directory: str = Field(
        default_factory=lambda: os.getenv("RAG_DOCUMENT_DIRECTORY", "")
    )
    chunk_size: int = Field(
        default_factory=lambda: int(os.getenv("RAG_CHUNK_SIZE", "4000"))
    )
    chunk_overlap: int = Field(
        default_factory=lambda: int(os.getenv("RAG_CHUNK_OVERLAP", "500"))
    )

    # 向量库配置
    vectorstore_type: str = Field(
        default_factory=lambda: os.getenv("RAG_VECTORSTORE_TYPE", "chroma")
    )
    persist_directory: str = Field(
        default_factory=lambda: os.getenv("RAG_PERSIST_DIRECTORY", "")
    )
    collection_name: str = Field(
        default_factory=lambda: os.getenv("RAG_COLLECTION_NAME", "default")
    )

    # 嵌入模型配置
    embedding_type: str = Field(
        default_factory=lambda: os.getenv("RAG_EMBEDDING_TYPE", "ollama")
    )
    embedding_model: str = Field(
        default_factory=lambda: os.getenv("RAG_EMBEDDING_MODEL", "")
    )
    embedding_base_url: str = Field(
        default_factory=lambda: os.getenv(
            "RAG_EMBEDDING_BASE_URL", "http://localhost:11434"
        )
    )

    # 检索配置
    search_type: str = Field(
        default_factory=lambda: os.getenv("RAG_SEARCH_TYPE", "similarity")
    )
    search_k: int = Field(default_factory=lambda: int(os.getenv("RAG_SEARCH_K", "5")))

    # 工具配置
    retriever_tool_name: str = Field(default="document_retriever")
    retriever_tool_description: str = Field(
        default="向量检索工具，根据用户查询和文档片段的向量相似度返回相关的 CloudPSS 知识库文档片段"
    )

    @property
    def search_kwargs(self) -> Dict[str, Any]:
        """检索参数"""
        return {"k": self.search_k}

    @property
    def embedding_config(self) -> Dict[str, Any]:
        """获取嵌入模型配置"""
        if self.embedding_type == "ollama":
            return {"model": self.embedding_model, "base_url": self.embedding_base_url}
        elif self.embedding_type == "openai":
            return {"model": self.embedding_model}
        elif self.embedding_type == "huggingface":
            return {"model_name": self.embedding_model}
        return {}
