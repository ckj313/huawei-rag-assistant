# Huawei RAG Assistant

华为网络设备配置 AI 助手 - 基于向量数据库 RAG 系统，从官方文档生成精确的 CLI 配置命令。

[![GitHub](https://img.shields.io/badge/GitHub-huawei--rag--assistant-blue)](https://github.com/ckj313/huawei-rag-assistant)

## 📚 文档导航

- **[README.md](README.md)** - 完整项目文档（本文件）
- **[CHEATSHEET.md](CHEATSHEET.md)** - 快速参考卡片（命令速查、技巧）⭐
- **[EXAMPLES.md](EXAMPLES.md)** - 详细使用示例和场景演示
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排查指南

## 功能特性

- 🔍 **智能文档查询**: 基于 ChromaDB 向量数据库，语义搜索 17,000+ 页华为 USG 防火墙官方文档
- 🤖 **AI 配置生成**: 通过 OpenCode Skill 系统，AI 自动生成配置命令
- 📚 **协议支持**: OSPF, BGP, IPsec, VPN, NAT, ACL, Security Policy, Firewall Zone 等
- 🇨🇳 **中文优化**: 使用 `thenlper/gte-large-zh` 嵌入模型，专为中文文档优化
- 💻 **纯命令生成**: 仅生成配置命令，不执行 SSH 操作，安全可控

## 项目结构

```
huawei-rag-assistant/
├── scripts/                    # 核心脚本
│   ├── html_parser.py         # CHM HTML 文档解析器
│   ├── ingest.py              # 向量数据库摄入脚本
│   └── query_huawei.py        # 文档查询 CLI 工具
├── skills/                     # OpenCode AI Skill
│   └── huawei-network-config.md
├── requirements.txt            # Python 依赖
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**依赖说明:**
- `chromadb>=1.0.0` - 向量数据库
- `sentence-transformers>=2.2.0` - 嵌入模型
- `beautifulsoup4>=4.12.0` - HTML 解析
- `lxml>=4.9.0` - XML/HTML 处理
- `tqdm>=4.65.0` - 进度条

### 2. 准备文档

提取华为 USG CHM 文档：

```bash
# 安装 chmlib (macOS)
brew install chmlib

# 提取 CHM 文件
extract_chmLib ~/Downloads/HUAWEI_usg.chm /tmp/huawei_chm_extract
```

### 3. 摄入文档到向量数据库

```bash
cd scripts

# 测试摄入 (100 个文件)
python ingest.py --source /tmp/huawei_chm_extract/V600R025C00/ --limit 100

# 完整摄入 (17,000+ 文件，需要 20-40 分钟)
python ingest.py --source /tmp/huawei_chm_extract/ --reset
```

**摄入参数:**
- `--source`: 源文档目录
- `--limit`: 限制处理文件数（用于测试）
- `--reset`: 重置数据库（清除现有数据）
- `--batch-size`: 批量插入大小（默认 100）

### 4. 查询文档

```bash
cd scripts

# 基础查询
python query_huawei.py "配置 OSPF 区域"

# 指定返回结果数量
python query_huawei.py "IPsec VPN" --top-k 5

# 按协议过滤
python query_huawei.py "NAT 地址池" --protocol nat

# 详细模式（显示完整文档片段）
python query_huawei.py "安全策略" --verbose

# JSON 输出
python query_huawei.py "BGP 邻居" --json
```

**支持的协议过滤器:**
- `ospf` - OSPF 路由
- `bgp` - BGP 路由
- `ipsec` - IPsec VPN
- `vpn` - 通用 VPN
- `nat` - NAT/PAT
- `acl` - 访问控制列表
- `firewall` - 安全策略和区域

## OpenCode AI Skill 集成

将 `skills/huawei-network-config.md` 复制到 OpenCode skills 目录：

```bash
cp skills/huawei-network-config.md ~/.config/opencode/skills/huawei-network-config/SKILL.md
```

然后在 OpenCode 中，AI 会在你询问华为配置问题时自动使用此 skill：

**示例对话:**

> 👤 帮我配置 OSPF 区域 0，接口 GigabitEthernet0/0/1

> 🤖 我来查询华为文档并生成配置...
> 
> ```bash
> <HUAWEI> system-view
> [HUAWEI] ospf 1 router-id 1.1.1.1
> [HUAWEI-ospf-1] area 0
> [HUAWEI-ospf-1-area-0.0.0.0] network 192.168.1.0 0.0.0.255
> ...
> ```

## 技术架构

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 向量数据库 | ChromaDB | 本地持久化，无需外部服务 |
| 嵌入模型 | `thenlper/gte-large-zh` | 中文优化，本地运行 (~670MB) |
| 文档解析 | BeautifulSoup + lxml | 处理 GB2312 编码的 HTML |
| 分块策略 | 800 字符 + 100 重叠 | 平衡上下文完整性和检索精度 |
| AI Skill | OpenCode Skill System | 指导 AI 使用 RAG 系统 |

## 华为 CLI 快速参考

### 视图层级

| 视图 | 提示符 | 进入命令 | 退出命令 |
|------|--------|----------|----------|
| 用户视图 | `<HUAWEI>` | 登录 | `quit` |
| 系统视图 | `[HUAWEI]` | `system-view` | `quit` / `return` |
| 接口视图 | `[HUAWEI-GigabitEthernet0/0/1]` | `interface GigabitEthernet0/0/1` | `quit` |
| 安全区域 | `[HUAWEI-zone-trust]` | `firewall zone trust` | `quit` |

### 常用命令

```bash
# 查看配置
display current-configuration

# 保存配置
save

# 查看接口
display interface brief

# 查看路由
display ip routing-table

# 查看防火墙会话
display firewall session table

# 查看安全策略
display security-policy rule all

# 查看 NAT 会话
display nat session all
```

### 安全区域优先级

| 区域 | 优先级 | 用途 |
|------|--------|------|
| Local | 100 | 设备本身 |
| Trust | 85 | 内网 |
| DMZ | 50 | DMZ 服务器 |
| Untrust | 5 | 互联网/外网 |

## 数据库位置

- **ChromaDB**: `~/.local/share/huawei-rag/data/chroma`
- **文档数量**: 17,000+ chunks (完整摄入后)
- **磁盘占用**: ~500MB (向量数据库 + 模型)

## ⚠️ 命令验证和修复

**重要**: AI 生成的命令可能存在问题，使用前必须验证！

### 验证清单

执行前检查：
- ✅ 语法是否正确（华为 CLI 格式）
- ✅ 参数是否适配你的环境（IP、接口名等）
- ✅ 命令顺序是否合理
- ✅ 是否缺少必要步骤
- ✅ 在测试环境验证后再用于生产

### 质量检查工具

```bash
# 检查查询结果质量
cd scripts
python check_quality.py "OSPF 配置" --protocol ospf

# 输出示例：
# 查询质量报告
# 状态: OK
# 高质量结果: 8 (>= 50%)
# 最佳分数: 85.23%
# 建议: ✅ 查询结果质量良好
```

### 如果命令有问题怎么办？

详见 **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** 完整故障排查指南：

1. **使用详细模式重新查询**: `--verbose --top-k 10`
2. **调整查询关键词**: 换个说法、更具体
3. **添加协议过滤器**: `--protocol ospf`
4. **交叉验证多个结果**: 对比前 5-10 个结果
5. **查看源文档**: 找到原始 HTML 文件查看上下文

**快速参考**: 查看 [CHEATSHEET.md](CHEATSHEET.md) 获取查询技巧和命令模板。

## 常见问题

### Q: 摄入速度太慢？

A: 这是正常的。CPU 运行嵌入模型速度约 2-3 files/s，完整摄入需要 3-4 小时。可以：
- 使用 `--limit` 参数先摄入部分文档测试
- 在后台运行: `nohup python ingest.py --source ... > ingest.log 2>&1 &`
- 使用更快的硬件（GPU 支持）

### Q: 如何更新文档？

A: 重新运行摄入脚本：
```bash
python ingest.py --source /tmp/huawei_chm_extract/ --reset
```

### Q: 支持其他华为设备吗？

A: 目前仅支持 USG 防火墙 V600R025C00 文档。要支持其他设备：
1. 提取对应的 CHM 文档
2. 运行摄入脚本

### Q: 如何添加自定义文档？

A: 将 HTML 文件放入文档目录，重新运行摄入脚本即可。

## 许可证

MIT License

## 致谢

- 华为官方文档
- ChromaDB 向量数据库
- Sentence Transformers 项目
- OpenCode AI Skill 系统
