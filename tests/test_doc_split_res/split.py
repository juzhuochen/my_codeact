import logging
from collections import defaultdict
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# --- 配置 ---
# 如需查看详细处理过程，请将日志级别调整为 logging.INFO
logging.basicConfig(level=logging.WARNING)

# 输入和输出目录设置
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "tanzhendong_comment"
OUTPUT_DIR = BASE_DIR / "split_results"

# --- 1. 从目录加载文档 ---
# 使用 DirectoryLoader 高效加载指定目录下的所有 Markdown 文件
dir_loader = DirectoryLoader(
    str(INPUT_DIR),
    glob="**/*.md",
    show_progress=True,
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}, # 确保使用UTF-8编码
    use_multithreading=True,
    max_concurrency=10,
)

loaded_docs = dir_loader.load()
logging.info(f"从 {INPUT_DIR} 加载了 {len(loaded_docs)} 个文档")

# --- 2. 定义切分器 ---
# 步骤 A: 按 Markdown 标题切分
# 这会根据标题（#, ##, ###）将文档分割成逻辑块
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False, # 保留标题在块内容中
)

# 步骤 B: 按字符递归切分
# 用于将过长的标题块切成更小的尺寸
# 注意：这里没有使用自定义分隔符，因为新方案的重点是先按标题切分
char_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3500,  # 每块最大字符数
    chunk_overlap=512,   # 块间重叠字符数
    length_function=len,
)

# --- 3. 执行切分并分组 ---
# 按源文件路径对切分后的块进行分组
grouped_chunks: dict[str, list[str]] = defaultdict(list)

print("开始处理文档切分...")
for doc in loaded_docs:
    # 第一步：使用 Markdown 标题进行切分
    title_chunks = markdown_splitter.split_text(doc.page_content)
    
    # 第二步：对上一步切分出的每个块，如果过长，则进行字符级切分
    final_chunks_for_doc: list[Document] = []
    for title_chunk in title_chunks:
        # 继承原始文档的元数据，并添加标题元数据
        title_chunk.metadata.update(doc.metadata)
        # 进行字符级切分
        sub_docs = char_splitter.split_documents([title_chunk])
        final_chunks_for_doc.extend(sub_docs)

    # 将处理完的块内容存入分组字典
    source_path:str = doc.metadata.get("source", "")
    if source_path:
        for chunk in final_chunks_for_doc:
            grouped_chunks[source_path].append(chunk.page_content)
    
    logging.info(f"文档 '{Path(source_path).name}' 被切分为 {len(final_chunks_for_doc)} 个块")

total_chunks_count = sum(len(chunks) for chunks in grouped_chunks.values())
print(f"\n所有文档总共被切分为 {total_chunks_count} 个块。")


# --- 4. 将切分结果写入文件 ---
# 为每个原始文件生成一个对应的切分结果文件
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
separator = "\n\n<=== Chunk SEPARATOR ===>\n\n"  # 文件内部分隔符

print("\n开始将切分结果写入文件...")
for src_path, chunks in grouped_chunks.items():
    # 使用原始文件名作为输出文件名
    file_name = Path(src_path).name
    out_file = OUTPUT_DIR / file_name

    # 使用 utf-8-sig 编码确保在 Windows 记事本等编辑器中能正常显示中文
    with out_file.open("w", encoding="utf-8-sig") as f:
        f.write(separator.join(chunks))

    print(f"已将 {len(chunks)} 个块写入到: {out_file}")

print("\n处理完成！")

