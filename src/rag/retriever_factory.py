from langchain.tools.retriever import create_retriever_tool
from langchain_core.tools import Tool
from langchain_core.vectorstores import VectorStore
from typing import List, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.rag.vector_store_manager import VectorStoreManager
from src.config.rag_config import RAGConfig

logger = logging.getLogger(__name__)

class RetrieverFactory:
    """异步检索器工厂"""
    
    def __init__(self, vector_store_manager: VectorStoreManager, config: RAGConfig):
        self.vector_store_manager = vector_store_manager
        self.config = config
        
        # 线程池，用于处理可能的阻塞操作
        self._executor = ThreadPoolExecutor(max_workers=1)
    
    async def create_retriever_tool_async(self, 
                                         vectorstore: Optional[VectorStore] = None,
                                         tool_name: Optional[str] = None,
                                         description: Optional[str] = None) -> Tool:
        """异步创建检索工具"""
        if vectorstore is None:
            vectorstore = await self.vector_store_manager.get_or_create_vectorstore_async()
        
        if tool_name is None:
            tool_name = self.config.retriever_tool_name
        
        if description is None:
            description = self.config.retriever_tool_description
        
        try:
            # 在线程池中创建检索器和工具（避免潜在的阻塞操作）
            loop = asyncio.get_event_loop()
            tool = await loop.run_in_executor(
                self._executor,
                self._create_retriever_tool_sync,
                vectorstore, tool_name, description
            )
            
            logger.info(f"Created retriever tool: {tool_name}")
            return tool
            
        except Exception as e:
            logger.error(f"Failed to create retriever tool: {e}")
            raise
    
    def _create_retriever_tool_sync(self, vectorstore: VectorStore, tool_name: str, description: str) -> Tool:
        """在线程池中同步创建检索工具"""
        # 创建检索器
        retriever = vectorstore.as_retriever(
            search_type=self.config.search_type,
            search_kwargs=self.config.search_kwargs
        )
        
        # 使用 LangChain 的 create_retriever_tool
        tool = create_retriever_tool(
            retriever=retriever,
            name=tool_name,
            description=description,
            document_separator="\n\n< DOCUMENT CHUNK SEPAEATOR />\n\n",
            response_format="content_and_artifact"
        )
        
        return tool
    
    async def create_multiple_retriever_tools_async(self, configs: List[dict]) -> List[Tool]:
        """异步创建多个检索工具"""
        tools = []
        vectorstore = await self.vector_store_manager.get_or_create_vectorstore_async()
        
        # 为每个配置创建异步任务
        create_tasks = []
        for config in configs:
            task = asyncio.create_task(
                self._create_single_retriever_tool_async(vectorstore, config)
            )
            create_tasks.append(task)
        
        # 并发执行所有创建任务
        results = await asyncio.gather(*create_tasks, return_exceptions=True)
        
        # 处理结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                config_name = configs[i].get('name', 'unknown')
                logger.error(f"Failed to create tool {config_name}: {result}")
            else:
                tools.append(result)
        
        return tools
    
    async def _create_single_retriever_tool_async(self, vectorstore: VectorStore, config: dict) -> Tool:
        """异步创建单个检索工具"""
        try:
            # 在线程池中创建检索器
            loop = asyncio.get_event_loop()
            tool = await loop.run_in_executor(
                self._executor,
                self._create_single_tool_sync,
                vectorstore, config
            )
            
            logger.info(f"Created retriever tool: {config['name']}")
            return tool
            
        except Exception as e:
            logger.error(f"Failed to create tool {config.get('name', 'unknown')}: {e}")
            raise
    
    def _create_single_tool_sync(self, vectorstore: VectorStore, config: dict) -> Tool:
        """在线程池中同步创建单个工具"""
        # 为每个配置创建不同的检索器
        retriever = vectorstore.as_retriever(
            search_type=config.get("search_type", "similarity"),
            search_kwargs=config.get("search_kwargs", {"k": 5})
        )
        
        tool = create_retriever_tool(
            retriever=retriever,
            name=config["name"],
            description=config["description"]
        )
        
        return tool
    
    async def close(self):
        """关闭线程池资源"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=True)
    
    def __del__(self):
        """析构函数，确保资源释放"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)