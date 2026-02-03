#!/usr/bin/env python3
"""
ingest.py - 华为文档数据摄入脚本

将 HTML 文档处理后存入 ChromaDB 向量数据库。

用法:
    python ingest.py --source /tmp/huawei_chm_extract/V600R025C00/
    python ingest.py --source /tmp/huawei_chm_extract/V600R025C00/ --limit 100
    python ingest.py --source /tmp/huawei_chm_extract/ --limit 500 --batch-size 50
"""

import argparse
from pathlib import Path
from tqdm import tqdm
import chromadb
from sentence_transformers import SentenceTransformer
from html_parser import parse_huawei_html
import re
import sys

# 配置
CHROMA_PATH = Path.home() / ".local/share/huawei-rag/data/chroma"
EMBEDDING_MODEL = "thenlper/gte-large-zh"  # 中文优化的嵌入模型
CHUNK_SIZE = 800  # 字符
CHUNK_OVERLAP = 100


def chunk_text(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list:
    """
    将文本分割成重叠的块

    Args:
        text: 原始文本
        chunk_size: 每块最大字符数
        overlap: 块之间的重叠字符数

    Returns:
        list: 文本块列表
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # 尝试在句子边界分割
        if end < len(text):
            # 寻找最后一个句子结束符
            last_period = chunk.rfind("。")
            last_newline = chunk.rfind("\n")
            last_semicolon = chunk.rfind("；")
            break_point = max(last_period, last_newline, last_semicolon)

            if break_point > chunk_size // 2:
                chunk = text[start : start + break_point + 1]
                end = start + break_point + 1

        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap
        if start >= len(text):
            break

    return chunks


def main():
    parser = argparse.ArgumentParser(description="Ingest Huawei docs into ChromaDB")
    parser.add_argument(
        "--source", required=True, help="Source directory containing HTML files"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of files to process"
    )
    parser.add_argument(
        "--batch-size", type=int, default=100, help="Batch size for database insertion"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Reset the database before ingesting"
    )
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source directory not found: {source_path}")
        sys.exit(1)

    # 初始化嵌入模型
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    print("(First run will download ~670MB model)")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Model loaded successfully.")

    # 初始化 ChromaDB
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    if args.reset:
        try:
            client.delete_collection("huawei_docs")
            print("Existing collection deleted.")
        except:
            pass

    collection = client.get_or_create_collection(
        name="huawei_docs",
        metadata={"description": "Huawei USG firewall documentation"},
    )

    existing_count = collection.count()
    print(f"Existing documents in collection: {existing_count}")

    # 获取 HTML 文件列表
    html_files = list(source_path.glob("**/*.html"))
    print(f"Found {len(html_files)} HTML files")

    if args.limit:
        html_files = html_files[: args.limit]
        print(f"Processing limited to {args.limit} files")

    # 批量处理
    batch_docs = []
    batch_metadatas = []
    batch_ids = []
    doc_id = existing_count  # 从现有文档数开始编号

    processed_files = 0
    skipped_files = 0
    total_chunks = 0

    for file_path in tqdm(html_files, desc="Processing files"):
        try:
            result = parse_huawei_html(str(file_path))

            # 跳过内容太少的文件
            if len(result["text"]) < 100:
                skipped_files += 1
                continue

            # 分块
            chunks = chunk_text(result["text"])

            for i, chunk in enumerate(chunks):
                if len(chunk) < 50:  # 跳过太短的块
                    continue

                batch_docs.append(chunk)
                batch_metadatas.append(
                    {
                        "source_file": str(file_path),
                        "protocol": result["metadata"]["protocol"],
                        "chunk_index": i,
                        "title": result["title"][:200] if result["title"] else "",
                        "commands": "; ".join(result["commands"][:5])[
                            :500
                        ],  # 前5个命令，限制长度
                        "command_count": result["metadata"]["command_count"],
                    }
                )
                batch_ids.append(f"doc_{doc_id}")
                doc_id += 1
                total_chunks += 1

                # 批量提交
                if len(batch_docs) >= args.batch_size:
                    try:
                        embeddings = model.encode(batch_docs, show_progress_bar=False)
                        collection.add(
                            documents=batch_docs,
                            embeddings=embeddings.tolist(),
                            metadatas=batch_metadatas,
                            ids=batch_ids,
                        )
                    except Exception as e:
                        print(f"\nWarning: Batch insert failed: {e}")

                    batch_docs = []
                    batch_metadatas = []
                    batch_ids = []

            processed_files += 1

        except Exception as e:
            print(f"\nWarning: Failed to process {file_path}: {e}")
            skipped_files += 1
            continue

    # 提交剩余批次
    if batch_docs:
        try:
            embeddings = model.encode(batch_docs, show_progress_bar=False)
            collection.add(
                documents=batch_docs,
                embeddings=embeddings.tolist(),
                metadatas=batch_metadatas,
                ids=batch_ids,
            )
        except Exception as e:
            print(f"\nWarning: Final batch insert failed: {e}")

    # 输出统计
    print("\n" + "=" * 50)
    print("Ingestion Complete!")
    print("=" * 50)
    print(f"Files processed: {processed_files}")
    print(f"Files skipped: {skipped_files}")
    print(f"Total chunks created: {total_chunks}")
    print(f"Total documents in collection: {collection.count()}")
    print(f"Database location: {CHROMA_PATH}")


if __name__ == "__main__":
    main()
