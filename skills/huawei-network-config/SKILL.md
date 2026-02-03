---
name: huawei-network-config
description: Use when user asks about Huawei USG firewall configuration, network protocols (OSPF, BGP, IPsec, VPN, NAT, ACL, security-policy), or needs CLI commands for Huawei devices. Triggers on keywords like '华为', 'USG', 'firewall', 'OSPF', 'BGP', 'NAT', 'VPN', 'ACL', '防火墙', '安全策略'.
---

# Huawei Network Configuration Assistant

华为 USG 防火墙配置助手 - 基于官方文档 RAG 系统生成精确 CLI 命令。

## Overview

This skill enables AI to query Huawei USG firewall documentation via vector database and generate accurate CLI commands for network configuration tasks.

**Capabilities:**
- Query 17,000+ pages of official Huawei documentation
- Generate CLI commands for protocols: OSPF, BGP, IPsec, VPN, NAT, ACL, etc.
- Provide step-by-step configuration workflows
- Include verification commands

**Limitations:**
- Commands only (no SSH execution)
- Based on V600R025C00 documentation
- Chinese documentation with some English terms

## When to Use

Use this skill when the user:
- Asks about Huawei USG firewall configuration
- Needs CLI commands for network protocols
- Wants to configure security policies, NAT, VPN, or routing
- Mentions keywords: 华为, USG, OSPF, BGP, NAT, VPN, ACL, 防火墙, 安全策略

## Workflow

### Step 1: Understand Requirements

Clarify what the user wants to configure:
- **Protocol/Feature**: OSPF? BGP? NAT? VPN? ACL? Security Policy?
- **Scenario**: Basic setup? Advanced features? Troubleshooting?
- **Parameters**: Any specific IP addresses, interfaces, or values?

### Step 2: Query Documentation

Use the query script to search relevant documentation:

```bash
cd ~/.local/share/huawei-rag/scripts
python query_huawei.py "<user's requirement>" --top-k 5 --verbose
```

**Query Templates:**

| Need | Query Command |
|------|---------------|
| OSPF 基础配置 | `python query_huawei.py "OSPF 区域配置 network" --protocol ospf` |
| BGP 邻居配置 | `python query_huawei.py "BGP peer 邻居配置" --protocol bgp` |
| IPsec VPN | `python query_huawei.py "IPsec policy IKE 配置" --protocol ipsec` |
| 安全策略 | `python query_huawei.py "security-policy rule permit" --protocol firewall` |
| NAT 配置 | `python query_huawei.py "NAT 地址池 source-nat" --protocol nat` |
| ACL 配置 | `python query_huawei.py "ACL rule permit deny" --protocol acl` |
| VPN 配置 | `python query_huawei.py "SSL-VPN L2TP" --protocol vpn` |

**Protocol Filters:**
- `--protocol ospf` - OSPF routing
- `--protocol bgp` - BGP routing
- `--protocol ipsec` - IPsec VPN
- `--protocol vpn` - General VPN
- `--protocol nat` - NAT/PAT
- `--protocol acl` - Access Control Lists
- `--protocol firewall` - Security policies & zones

### Step 3: Extract & Organize Commands

From the query results:
1. Extract commands from the `commands` field
2. Read the `text` field for context and sequence
3. Organize commands in logical configuration order
4. Adapt parameters to user's specific requirements

### Step 4: Generate Configuration

Output format:

```
## 配置目标
[Brief description of what will be configured]

## 前置条件
- [Prerequisites, e.g., "已配置接口 IP 地址"]

## 配置步骤

### 步骤 1: [Step Name]
\`\`\`
# [Explanation]
<HUAWEI> system-view
[HUAWEI] [command]
\`\`\`

### 步骤 2: [Step Name]
\`\`\`
# [Explanation]
[HUAWEI] [command]
\`\`\`

## 验证命令
\`\`\`
<HUAWEI> display [relevant show command]
\`\`\`

## 注意事项
- [Important notes or warnings]
```

## Huawei CLI Quick Reference

### View Hierarchy

| View | Prompt | Enter | Exit |
|------|--------|-------|------|
| User View | `<HUAWEI>` | Login | `quit` |
| System View | `[HUAWEI]` | `system-view` | `quit` / `return` |
| Interface View | `[HUAWEI-GigabitEthernet0/0/1]` | `interface GigabitEthernet0/0/1` | `quit` |
| Security Zone | `[HUAWEI-zone-trust]` | `firewall zone trust` | `quit` |
| ACL View | `[HUAWEI-acl-adv-3000]` | `acl number 3000` | `quit` |

### Common Commands

```
# 查看配置
display current-configuration

# 保存配置
save

# 查看接口
display interface brief

# 查看路由
display ip routing-table

# 查看会话
display firewall session table

# 查看安全策略
display security-policy rule all

# 查看 NAT
display nat session all
```

### Security Zones

| Zone | Priority | Typical Use |
|------|----------|-------------|
| Local | 100 | Device itself |
| Trust | 85 | Internal network |
| DMZ | 50 | DMZ servers |
| Untrust | 5 | Internet/External |

## Important Constraints

1. **NO SSH execution** - Generate commands only, user executes manually
2. **Document-based** - Commands must be from or reference query results
3. **Cite sources** - Mention which document the command comes from
4. **Be cautious** - When uncertain, recommend checking official documentation
5. **Chinese/English mix** - Documentation is Chinese, commands are English

## Example Interaction

**User**: 帮我配置 OSPF，区域 0，接口 GigabitEthernet0/0/1

**AI Actions**:
1. Query: `python query_huawei.py "OSPF area 0 network interface" --protocol ospf --verbose`
2. Extract relevant commands from results
3. Adapt to user's interface (GigabitEthernet0/0/1)
4. Generate configuration:

```
## 配置目标
在 GigabitEthernet0/0/1 接口上启用 OSPF，加入 Area 0

## 配置步骤

### 步骤 1: 创建 OSPF 进程
\`\`\`
<HUAWEI> system-view
[HUAWEI] ospf 1 router-id 1.1.1.1
\`\`\`

### 步骤 2: 配置 Area 0 并宣告网络
\`\`\`
[HUAWEI-ospf-1] area 0
[HUAWEI-ospf-1-area-0.0.0.0] network x.x.x.x 0.0.0.255
[HUAWEI-ospf-1-area-0.0.0.0] quit
[HUAWEI-ospf-1] quit
\`\`\`

### 步骤 3: (可选) 在接口上启用 OSPF
\`\`\`
[HUAWEI] interface GigabitEthernet0/0/1
[HUAWEI-GigabitEthernet0/0/1] ospf enable 1 area 0
[HUAWEI-GigabitEthernet0/0/1] quit
\`\`\`

## 验证命令
\`\`\`
<HUAWEI> display ospf peer brief
<HUAWEI> display ospf routing
\`\`\`

## 注意事项
- 请将 `router-id` 替换为实际设备的 Loopback 地址
- 请将 `network` 命令中的网段替换为接口实际 IP 所在网段
```

## Database Info

- **Location**: `~/.local/share/huawei-rag/data/chroma`
- **Documents**: 17,000+ chunks from V600R025C00 documentation
- **Embedding Model**: `thenlper/gte-large-zh` (Chinese-optimized)
- **Query Script**: `~/.local/share/huawei-rag/scripts/query_huawei.py`
