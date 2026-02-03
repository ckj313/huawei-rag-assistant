# 快速参考卡片

## 🚀 快速开始

```bash
# 安装
pip install -r requirements.txt

# 摄入文档（首次使用）
cd scripts
python ingest.py --source /tmp/huawei_chm_extract/ --limit 200

# 查询
python query_huawei.py "OSPF 配置"
```

## 📋 常用命令

### 基础查询

```bash
# 简单查询
python query_huawei.py "配置 OSPF"

# 指定结果数量
python query_huawei.py "NAT 配置" --top-k 10

# 详细模式（显示完整文档）
python query_huawei.py "IPsec VPN" --verbose

# JSON 输出
python query_huawei.py "安全策略" --json
```

### 协议过滤

```bash
python query_huawei.py "配置命令" --protocol ospf
python query_huawei.py "地址池" --protocol nat
python query_huawei.py "隧道" --protocol ipsec
python query_huawei.py "策略" --protocol firewall
```

### 组合使用

```bash
# 详细 + 协议过滤 + 多结果
python query_huawei.py "BGP 邻居" --protocol bgp --verbose --top-k 5

# JSON + 协议过滤
python query_huawei.py "ACL 规则" --protocol acl --json > acl_config.json
```

## 🔍 查询技巧

### 关键词选择

| 需求 | ❌ 不好的查询 | ✅ 好的查询 |
|------|-------------|-----------|
| OSPF 配置 | "OSPF" | "OSPF area network 配置" |
| NAT 配置 | "NAT" | "NAT address-group source-nat" |
| IPsec VPN | "VPN" | "IPsec IKE policy 配置" |
| 安全策略 | "策略" | "security-policy rule permit" |

### 查询模板

```bash
# 基础配置
python query_huawei.py "[协议] 基础配置 命令" --protocol [协议]

# 高级特性
python query_huawei.py "[协议] [特性] 配置案例" --protocol [协议]

# 故障排查
python query_huawei.py "[协议] display 查看命令" --protocol [协议]
```

## 🛠️ 质量检查

```bash
# 检查查询质量
python check_quality.py "OSPF 配置"

# 带协议过滤的质量检查
python check_quality.py "NAT 地址池" --protocol nat

# 自定义质量阈值
python check_quality.py "BGP 邻居" --threshold 0.6
```

## 📊 系统维护

### 数据库管理

```bash
# 检查文档数量
python -c "import chromadb; c=chromadb.PersistentClient(path='/Users/ccc/.local/share/huawei-rag/data/chroma'); print('Docs:', c.get_collection('huawei_docs').count())"

# 重建数据库
pkill -f ingest.py
rm -rf ~/.local/share/huawei-rag/data/chroma
python ingest.py --source /tmp/huawei_chm_extract/ --reset
```

### 摄入管理

```bash
# 查看摄入进度
tail -f ~/.local/share/huawei-rag/ingest.log

# 检查摄入进程
ps aux | grep ingest.py

# 停止摄入
pkill -f ingest.py
```

## 🎯 协议速查

| 协议 | Filter 参数 | 常用查询 |
|------|------------|---------|
| OSPF | `--protocol ospf` | "OSPF area network" |
| BGP | `--protocol bgp` | "BGP peer neighbor" |
| IPsec | `--protocol ipsec` | "IPsec IKE policy" |
| VPN | `--protocol vpn` | "SSL-VPN L2TP" |
| NAT | `--protocol nat` | "NAT address-group" |
| ACL | `--protocol acl` | "ACL rule permit" |
| Firewall | `--protocol firewall` | "security-policy zone" |

## 💡 最佳实践

### ✅ DO

- 使用 `--verbose` 查看完整上下文
- 查询多个结果对比 (`--top-k 5-10`)
- 使用协议过滤器精确查询
- 在测试环境验证命令
- 调整参数适配你的环境

### ❌ DON'T

- 不要盲目复制到生产环境
- 不要忽略相似度分数
- 不要只看第一个结果
- 不要跳过参数替换
- 不要期待 100% 准确（需要人工验证）

## 🔧 便捷别名

添加到 `~/.bashrc` 或 `~/.zshrc`:

```bash
# 基础别名
alias hw='cd ~/.local/share/huawei-rag/scripts && python query_huawei.py'
alias hwq='hw --verbose'

# 协议别名
alias hw-ospf='hw --protocol ospf --verbose'
alias hw-bgp='hw --protocol bgp --verbose'
alias hw-nat='hw --protocol nat --verbose'
alias hw-vpn='hw --protocol ipsec --verbose'
alias hw-acl='hw --protocol acl --verbose'
alias hw-fw='hw --protocol firewall --verbose'

# 质量检查
alias hwc='cd ~/.local/share/huawei-rag/scripts && python check_quality.py'
```

使用：
```bash
hw "OSPF 配置"                    # 简单查询
hwq "OSPF area"                   # 详细查询
hw-ospf "区域配置"                # OSPF 专用
hwc "OSPF 配置" --protocol ospf   # 质量检查
```

## 📖 华为 CLI 速查

### 视图层级

```
用户视图    <HUAWEI>              system-view →
系统视图    [HUAWEI]              interface GE0/0/1 →
接口视图    [HUAWEI-GE0/0/1]      quit ← 
系统视图    [HUAWEI]              quit ←
用户视图    <HUAWEI>
```

### 常用命令

```bash
# 查看
display current-configuration    # 当前配置
display interface brief          # 接口状态
display ip routing-table         # 路由表
display firewall session table   # 会话表

# 保存
save                            # 保存配置

# 导航
system-view                     # 进入系统视图
quit                           # 退出当前视图
return                         # 直接回到用户视图
```

### 安全区域

| 区域 | 优先级 | 用途 |
|------|--------|------|
| local | 100 | 设备本身 |
| trust | 85 | 内网 |
| dmz | 50 | DMZ |
| untrust | 5 | 外网 |

## 🆘 遇到问题？

1. **查询结果不相关** → 使用更具体的关键词 + 协议过滤
2. **命令不正确** → 查看多个结果交叉验证
3. **参数需要调整** → 正常！根据实际环境修改
4. **查询很慢** → 首次加载模型需要时间，后续会快
5. **数据库异常** → 查看 TROUBLESHOOTING.md

详细故障排查：[TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 📚 更多资源

- [README.md](README.md) - 完整文档
- [EXAMPLES.md](EXAMPLES.md) - 使用示例
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排查
- [GitHub](https://github.com/ckj313/huawei-rag-assistant) - 项目仓库
