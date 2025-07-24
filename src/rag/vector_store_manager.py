from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from typing import List, Optional, Type, Dict, Any
import logging
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from src.config.rag_config import RAGConfig
logger = logging.getLogger(__name__)

class VectorStoreManager:
    """向量库管理器"""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        
        # 向量库类映射
        self.vectorstore_classes: Dict[str, Any] = {
            'chroma': Chroma,
            'faiss': FAISS,
        }
        
        # 嵌入模型类映射
        self.embedding_classes = {
            'ollama': OllamaEmbeddings,
            'openai': OpenAIEmbeddings,
        }
        
        self._embedding_model = None
        self._vectorstore = None
        
        # 线程池，用于处理I/O密集型和CPU密集型任务
        self._executor = ThreadPoolExecutor(max_workers=2)
    
    async def get_embedding_model_async(self):
        """异步获取嵌入模型实例"""
        if self._embedding_model is None:
            embedding_cls = self.embedding_classes.get(self.config.embedding_type)
            if not embedding_cls:
                raise ValueError(f"Unsupported embedding type: {self.config.embedding_type}")
            
            try:
                # 在线程池中初始化嵌入模型（可能涉及网络请求）
                loop = asyncio.get_event_loop()
                self._embedding_model = await loop.run_in_executor(
                    self._executor,
                    lambda: embedding_cls(**self.config.embedding_config)
                )
                logger.info(f"Initialized {self.config.embedding_type} embedding model")
            except Exception as e:
                logger.error(f"Failed to initialize embedding model: {e}")
                raise
        
        return self._embedding_model
    
    async def create_vectorstore_async(self, documents: List[Document]) -> VectorStore:
        """异步创建新的向量库"""
        if not documents:
            raise ValueError("No documents provided for vector store creation")
        
        vectorstore_cls = self.vectorstore_classes.get(self.config.vectorstore_type)
        if not vectorstore_cls:
            raise ValueError(f"Unsupported vectorstore type: {self.config.vectorstore_type}")
        
        embedding_model = await self.get_embedding_model_async()
        
        try:
            logger.info(f"Creating {self.config.vectorstore_type} vector store with {len(documents)} documents")
            
            # 在线程池中执行向量库创建（CPU/IO密集型操作）
            loop = asyncio.get_event_loop()
            
            if self.config.vectorstore_type == 'chroma':
                vectorstore = await loop.run_in_executor(
                    self._executor,
                    self._create_chroma_vectorstore,
                    documents, embedding_model
                )
            elif self.config.vectorstore_type == 'faiss':
                vectorstore = await loop.run_in_executor(
                    self._executor,
                    self._create_faiss_vectorstore,
                    documents, embedding_model
                )
            else: 
                raise ValueError(f"Unsupported vectorstore type: {self.config.vectorstore_type}") 
            
            logger.info("Vector store created successfully")
            self._vectorstore = vectorstore
            return vectorstore
            
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise
    
    def _create_chroma_vectorstore(self, documents: List[Document], embedding_model) -> Chroma:
        """在线程池中同步创建Chroma向量库"""
        return Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            persist_directory=self.config.persist_directory,
            collection_name=self.config.collection_name
        )
    
    def _create_faiss_vectorstore(self, documents: List[Document], embedding_model) -> FAISS:
        """在线程池中同步创建FAISS向量库"""
        vectorstore = FAISS.from_documents(
            documents=documents,
            embedding=embedding_model
        )
        # FAISS 需要手动保存
        vectorstore.save_local(self.config.persist_directory)
        return vectorstore
    
    async def load_existing_vectorstore_async(self) -> Optional[VectorStore]:
        """异步加载已存在的向量库"""
        persist_path = Path(self.config.persist_directory)
        
        if not persist_path.exists():
            logger.info(f"Persist directory {persist_path} does not exist")
            return None
        
        embedding_model = await self.get_embedding_model_async()
        
        try:
            # 在线程池中执行向量库加载
            loop = asyncio.get_event_loop()
            
            if self.config.vectorstore_type == 'chroma':
                vectorstore = await loop.run_in_executor(
                    self._executor,
                    self._load_chroma_vectorstore,
                    embedding_model
                )
                
                # 检查集合是否有数据（需要在线程池中执行）
                count = await loop.run_in_executor(
                    self._executor,
                    lambda: vectorstore._collection.count()
                )
                
                if count == 0:
                    logger.info("Existing Chroma collection is empty")
                    return None
                    
            elif self.config.vectorstore_type == 'faiss':
                if not (persist_path / "index.faiss").exists():
                    logger.info("FAISS index file not found")
                    return None
                    
                vectorstore = await loop.run_in_executor(
                    self._executor,
                    self._load_faiss_vectorstore,
                    embedding_model
                )
            else:
                raise ValueError(f"Unsupported vectorstore type: {self.config.vectorstore_type}")
            
            logger.info(f"Loaded existing {self.config.vectorstore_type} vector store")
            self._vectorstore = vectorstore
            return vectorstore
            
        except Exception as e:
            logger.error(f"Failed to load existing vector store: {e}")
            return None
    
    def _load_chroma_vectorstore(self, embedding_model) -> Chroma:
        """在线程池中同步加载Chroma向量库"""
        return Chroma(
            persist_directory=self.config.persist_directory,
            embedding_function=embedding_model,
            collection_name=self.config.collection_name
        )
    
    def _load_faiss_vectorstore(self, embedding_model) -> FAISS:
        """在线程池中同步加载FAISS向量库"""
        return FAISS.load_local(
            self.config.persist_directory,
            embedding_model,
            allow_dangerous_deserialization=True
        )
    
    async def get_or_create_vectorstore_async(self, documents: List[Document] | None = None) -> VectorStore:
        """异步获取或创建向量库"""
        if self._vectorstore is not None:
            return self._vectorstore
        
        # 尝试异步加载已存在的向量库
        existing_store = await self.load_existing_vectorstore_async()
        if existing_store is not None:
            return existing_store
        
        # 如果没有现有的向量库，创建新的
        if documents is None:
            raise ValueError("No existing vector store found and no documents provided for creation")
        
        return await self.create_vectorstore_async(documents)
    
    async def close(self):
        """关闭线程池资源"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=True)
    
    def __del__(self):
        """析构函数，确保资源释放"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)