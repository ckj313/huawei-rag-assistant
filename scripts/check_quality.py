#!/usr/bin/env python3
"""
check_quality.py - 检查查询结果质量

用法:
    python check_quality.py "OSPF 配置"
    python check_quality.py "NAT 地址池" --protocol nat
"""

import argparse
from query_huawei import query


def check_quality(query_text, protocol=None, threshold=0.5):
    """
    检查查询结果质量

    Args:
        query_text: 查询文本
        protocol: 协议过滤器
        threshold: 质量阈值（相似度分数）

    Returns:
        dict: 质量报告
    """
    results = query(query_text, top_k=10, filter_protocol=protocol)

    if not results:
        return {
            "status": "ERROR",
            "message": "没有找到相关结果",
            "suggestions": [
                "尝试使用不同的关键词",
                "检查数据库是否完成摄入",
                "使用更通用的搜索词",
            ],
        }

    # 分析结果质量
    high_quality = [r for r in results if r["score"] >= threshold]
    medium_quality = [r for r in results if 0.3 <= r["score"] < threshold]
    low_quality = [r for r in results if r["score"] < 0.3]

    # 检查命令数量
    has_commands = [r for r in results if r.get("commands")]

    # 检查协议一致性
    if protocol:
        correct_protocol = [r for r in results if r.get("protocol") == protocol]
        protocol_accuracy = len(correct_protocol) / len(results) if results else 0
    else:
        protocol_accuracy = None

    # 生成质量报告
    report = {
        "status": "OK" if high_quality else "WARNING",
        "total_results": len(results),
        "high_quality_count": len(high_quality),
        "medium_quality_count": len(medium_quality),
        "low_quality_count": len(low_quality),
        "best_score": results[0]["score"] if results else 0,
        "avg_score": sum(r["score"] for r in results) / len(results) if results else 0,
        "has_commands_ratio": len(has_commands) / len(results) if results else 0,
        "protocol_accuracy": protocol_accuracy,
        "suggestions": [],
    }

    # 生成建议
    if report["best_score"] < 0.3:
        report["suggestions"].append("⚠️  相似度很低，建议更换关键词")
    elif report["best_score"] < threshold:
        report["suggestions"].append("⚠️  相似度偏低，建议查看更多结果或调整关键词")

    if report["has_commands_ratio"] < 0.5:
        report["suggestions"].append("⚠️  部分结果缺少命令，可能需要更精确的查询")

    if protocol and protocol_accuracy and protocol_accuracy < 0.8:
        report["suggestions"].append(
            f"⚠️  协议匹配度只有 {protocol_accuracy:.0%}，检查查询关键词"
        )

    if not report["suggestions"]:
        report["suggestions"].append("✅ 查询结果质量良好")

    return report


def format_report(report):
    """格式化质量报告"""
    lines = [
        "\n" + "=" * 60,
        "查询质量报告",
        "=" * 60,
        f"状态: {report['status']}",
        f"总结果数: {report['total_results']}",
        f"高质量结果: {report['high_quality_count']} (>= 50%)",
        f"中等质量: {report['medium_quality_count']} (30-50%)",
        f"低质量: {report['low_quality_count']} (< 30%)",
        f"最佳分数: {report['best_score']:.2%}",
        f"平均分数: {report['avg_score']:.2%}",
        f"包含命令比例: {report['has_commands_ratio']:.2%}",
    ]

    if report["protocol_accuracy"] is not None:
        lines.append(f"协议匹配准确度: {report['protocol_accuracy']:.2%}")

    lines.extend(["\n建议:", *[f"  {s}" for s in report["suggestions"]], "=" * 60])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check query result quality")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--protocol", "-p", help="Protocol filter")
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=0.5,
        help="Quality threshold (default: 0.5)",
    )
    args = parser.parse_args()

    print(f'\n🔍 检查查询: "{args.query}"')
    if args.protocol:
        print(f"🎯 协议过滤: {args.protocol}")

    report = check_quality(args.query, args.protocol, args.threshold)
    print(format_report(report))

    # 显示最佳结果预览
    if report["total_results"] > 0:
        print("\n📋 最佳结果预览:")
        results = query(args.query, top_k=3, filter_protocol=args.protocol)
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r['title'][:60]}...")
            print(f"    Score: {r['score']:.2%} | Protocol: {r['protocol']}")
            if r["commands"]:
                cmds = r["commands"].split(";")[:3]
                print(
                    f"    Commands: {', '.join([c.strip()[:40] for c in cmds if c.strip()])}..."
                )


if __name__ == "__main__":
    main()
