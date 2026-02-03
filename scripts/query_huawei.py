#!/usr/bin/env python3
"""
query_huawei.py - 查询华为文档向量数据库

用法:
    python query_huawei.py "配置 OSPF 区域"
    python query_huawei.py "IPsec VPN" --top-k 5
    python query_huawei.py "防火墙安全策略" --verbose
    python query_huawei.py "NAT 配置" --json
"""

import argparse
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
import sys

# 配置
CHROMA_PATH = Path.home() / ".local/share/huawei-rag/data/chroma"
EMBEDDING_MODEL = "thenlper/gte-large-zh"

# 全局模型缓存
_model = None


def get_model():
    """获取或加载嵌入模型（带缓存）"""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def query(query_text: str, top_k: int = 5, filter_protocol: str = None) -> list:
    """
    查询向量数据库

    Args:
        query_text: 查询文本
        top_k: 返回结果数量
        filter_protocol: 可选的协议过滤器

    Returns:
        list of dict: [
            {
                "text": str,       # 文档片段
                "commands": str,   # 相关命令
                "source": str,     # 源文件
                "protocol": str,   # 协议类型
                "title": str,      # 文档标题
                "score": float     # 相似度分数
            }
        ]
    """
    model = get_model()

    # 检查数据库是否存在
    if not CHROMA_PATH.exists():
        print(f"Error: Database not found at {CHROMA_PATH}")
        print("Please run ingest.py first to create the database.")
        sys.exit(1)

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    try:
        collection = client.get_collection("huawei_docs")
    except Exception as e:
        print(f"Error: Collection 'huawei_docs' not found: {e}")
        print("Please run ingest.py first to create the database.")
        sys.exit(1)

    # 生成查询嵌入
    query_embedding = model.encode([query_text])[0].tolist()

    # 构建查询参数
    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }

    # 添加协议过滤器
    if filter_protocol:
        query_kwargs["where"] = {"protocol": filter_protocol}

    # 执行查询
    results = collection.query(**query_kwargs)

    # 格式化输出
    output = []
    for i in range(len(results["ids"][0])):
        doc = results["documents"][0][i]
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        # 限制文本长度以便显示
        text = doc[:800] + "..." if len(doc) > 800 else doc

        output.append(
            {
                "text": text,
                "commands": metadata.get("commands", ""),
                "source": metadata.get("source_file", ""),
                "protocol": metadata.get("protocol", "unknown"),
                "title": metadata.get("title", ""),
                "score": round(1 - distance, 4),  # 转换距离为相似度
            }
        )

    return output


def format_result(result: dict, index: int, verbose: bool = False) -> str:
    """格式化单个结果为可读文本"""
    lines = [
        f"\n{'=' * 70}",
        f"[{index}] {result['title'] or 'Untitled'}",
        f"    Protocol: {result['protocol']} | Score: {result['score']:.2%}",
        f"{'=' * 70}",
    ]

    if result["commands"]:
        lines.append(f"\n\U0001f4cb 相关命令:")
        for cmd in result["commands"].split(";"):
            cmd = cmd.strip()
            if cmd:
                # 截断过长的命令
                display_cmd = cmd[:100] + "..." if len(cmd) > 100 else cmd
                lines.append(f"   \u2022 {display_cmd}")

    if verbose:
        lines.append(f"\n\U0001f4c4 文档片段:")
        # 格式化文档内容
        text_lines = result["text"].split("\n")
        for line in text_lines[:20]:  # 最多显示20行
            line = line.strip()
            if line:
                lines.append(f"   {line}")
        if len(text_lines) > 20:
            lines.append("   ...")

        lines.append(f"\n\U0001f4c1 来源: {Path(result['source']).name}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Query Huawei USG documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "配置 OSPF 区域"
  %(prog)s "IPsec VPN 站点到站点" --top-k 5
  %(prog)s "NAT 地址池" --protocol nat --verbose
  %(prog)s "安全策略" --json
        """,
    )
    parser.add_argument("query", help="Search query in Chinese or English")
    parser.add_argument(
        "--top-k", "-k", type=int, default=5, help="Number of results (default: 5)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show full document text"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--protocol",
        "-p",
        type=str,
        default=None,
        help="Filter by protocol (ospf, bgp, ipsec, vpn, nat, acl, firewall, etc.)",
    )
    args = parser.parse_args()

    # 执行查询
    results = query(args.query, args.top_k, args.protocol)

    if not results:
        print("No results found.")
        return

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f'\n\U0001f50d 查询: "{args.query}"')
        if args.protocol:
            print(f"\U0001f3af 过滤: protocol={args.protocol}")
        print(f"\U0001f4ca 找到 {len(results)} 个相关结果")

        for i, result in enumerate(results, 1):
            print(format_result(result, i, args.verbose))

        print("\n" + "-" * 70)
        print("Tip: Use --verbose for full document text, --json for structured output")


if __name__ == "__main__":
    main()
