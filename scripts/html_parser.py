"""
html_parser.py - 华为 CHM 文档解析器

功能:
1. GB2312 → UTF-8 编码转换
2. 提取 <pre class="screen"> 中的命令示例
3. 提取 <span class="cmdqueryname"> 中的命令名
4. 提取标题和正文文本
5. 返回结构化数据
"""

from bs4 import BeautifulSoup
from pathlib import Path
import re


def parse_huawei_html(file_path: str) -> dict:
    """
    解析华为 HTML 文档

    Args:
        file_path: HTML 文件路径

    Returns:
        {
            "text": str,        # 清理后的文本内容
            "commands": list,   # 提取的命令列表
            "title": str,       # 文档标题
            "metadata": dict    # 元数据（文件名、协议类型等）
        }
    """
    # 读取文件，处理 GB2312 编码
    with open(file_path, "rb") as f:
        content = f.read()

    # 尝试多种编码解码
    html = None
    for encoding in ["gb2312", "gbk", "gb18030", "utf-8", "latin-1"]:
        try:
            html = content.decode(encoding)
            break
        except (UnicodeDecodeError, LookupError):
            continue

    if html is None:
        # 最后手段：忽略错误
        html = content.decode("utf-8", errors="ignore")

    soup = BeautifulSoup(html, "lxml")

    # 移除 script 和 style 标签
    for tag in soup(["script", "style", "link", "meta"]):
        tag.decompose()

    # 提取命令 - 从 <pre class="screen"> 块
    commands = []
    for pre in soup.find_all("pre", class_="screen"):
        cmd_text = pre.get_text(strip=True)
        if cmd_text:
            # 清理命令文本
            cmd_text = re.sub(r"\s+", " ", cmd_text)
            commands.append(cmd_text[:500])  # 限制长度

    # 提取命令 - 从 <span> 标签 (class 包含命令相关关键字)
    cmd_classes = ["cmdqueryname", "keyword", "parmname"]
    for cls in cmd_classes:
        for span in soup.find_all("span", class_=cls):
            cmd = span.get_text(strip=True)
            if cmd and len(cmd) > 2:
                commands.append(cmd)

    # 提取 <strong> 标签中的命令（在 screen 块内）
    for strong in soup.find_all("strong"):
        parent = strong.find_parent("pre", class_="screen")
        if parent:
            cmd = strong.get_text(strip=True)
            if cmd and len(cmd) > 2:
                commands.append(cmd)

    # 去重并保持顺序
    seen = set()
    unique_commands = []
    for cmd in commands:
        if cmd not in seen and cmd:
            seen.add(cmd)
            unique_commands.append(cmd)

    # 提取标题
    title = ""
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

    # 提取正文文本
    text = soup.get_text(separator="\n", strip=True)
    # 清理多余空白
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    # 推断协议类型
    protocol = infer_protocol(file_path, text)

    return {
        "text": text,
        "commands": unique_commands,
        "title": title,
        "metadata": {
            "source_file": str(file_path),
            "protocol": protocol,
            "command_count": len(unique_commands),
        },
    }


def infer_protocol(file_path: str, text: str) -> str:
    """根据文件名和内容推断协议类型"""
    path_lower = str(file_path).lower()
    text_lower = text.lower()[:2000]  # 只检查前2000字符

    # 协议关键词映射（优先级从高到低）
    protocols = [
        ("ospf", ["ospf", "ospfv3"]),
        ("bgp", ["bgp", "ebgp", "ibgp"]),
        ("ipsec", ["ipsec", "ike-peer", "ike proposal"]),
        ("vpn", ["vpn", "ssl-vpn", "l2tp", "pptp"]),
        ("nat", ["nat-policy", "nat server", "nat address-group", "napt"]),
        ("acl", ["acl number", "acl name", "access-list"]),
        ("firewall", ["firewall zone", "security-policy", "trust", "untrust"]),
        ("vlan", ["vlan", "vlanif", "trunk", "access"]),
        ("interface", ["interface", "eth-trunk", "gigabitethernet"]),
        ("routing", ["ip route", "route-policy", "static route"]),
        ("qos", ["qos", "traffic-policy", "traffic-classifier"]),
        ("aaa", ["aaa", "authentication", "authorization", "accounting"]),
        ("dns", ["dns", "domain"]),
        ("ntp", ["ntp"]),
        ("snmp", ["snmp"]),
        ("syslog", ["syslog", "info-center"]),
    ]

    for proto, keywords in protocols:
        for kw in keywords:
            if kw in path_lower or kw in text_lower:
                return proto

    return "general"


def extract_config_blocks(text: str) -> list:
    """从文本中提取配置块"""
    blocks = []

    # 匹配配置块模式
    # 华为配置通常以 # 开头，或以 [ 开头
    config_pattern = r"(?:^|\n)((?:[#\[].*\n?)+)"
    matches = re.findall(config_pattern, text, re.MULTILINE)

    for match in matches:
        if len(match.strip()) > 20:
            blocks.append(match.strip())

    return blocks


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = parse_huawei_html(file_path)

        print(f"Title: {result['title']}")
        print(f"Protocol: {result['metadata']['protocol']}")
        print(f"Text length: {len(result['text'])}")
        print(f"Commands found: {len(result['commands'])}")

        if result["commands"]:
            print("\nSample commands:")
            for cmd in result["commands"][:10]:
                print(f"  - {cmd[:80]}{'...' if len(cmd) > 80 else ''}")
    else:
        print("Usage: python html_parser.py <html_file>")
