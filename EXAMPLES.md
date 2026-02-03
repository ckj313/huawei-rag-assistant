# 使用示例

## 基础查询示例

### 1. OSPF 配置查询

```bash
python scripts/query_huawei.py "配置 OSPF 区域 0" --protocol ospf --verbose
```

**输出示例:**
```
🔍 查询: "配置 OSPF 区域 0"
🎯 过滤: protocol=ospf
📊 找到 5 个相关结果

======================================================================
[1] OSPF 单区域配置
    Protocol: ospf | Score: 85.23%
======================================================================

📋 相关命令:
   • system-view
   • ospf 1 router-id 1.1.1.1
   • area 0
   • network 192.168.1.0 0.0.0.255

📄 文档片段:
   配置思路：
   1. 创建 OSPF 进程并配置 Router ID
   2. 进入 Area 0 视图
   3. 使用 network 命令宣告网络
   4. 在接口上启用 OSPF（可选）
   ...
```

### 2. NAT 配置查询

```bash
python scripts/query_huawei.py "NAT 地址池 source-nat" --protocol nat --top-k 3
```

### 3. IPsec VPN 查询

```bash
python scripts/query_huawei.py "IPsec IKE policy 配置" --protocol ipsec --verbose
```

## AI Skill 使用示例

### 场景 1: OSPF 基础配置

**用户输入:**
> 帮我配置 OSPF，区域 0，Router ID 1.1.1.1，宣告网络 192.168.1.0/24

**AI 响应:**

````markdown
## 配置目标
在华为 USG 防火墙上配置 OSPF 单区域，Router ID 为 1.1.1.1，宣告网络 192.168.1.0/24

## 前置条件
- 已配置接口 IP 地址
- 接口状态为 UP

## 配置步骤

### 步骤 1: 创建 OSPF 进程并配置 Router ID
```
<HUAWEI> system-view
[HUAWEI] ospf 1 router-id 1.1.1.1
```

### 步骤 2: 配置 Area 0 并宣告网络
```
[HUAWEI-ospf-1] area 0
[HUAWEI-ospf-1-area-0.0.0.0] network 192.168.1.0 0.0.0.255
[HUAWEI-ospf-1-area-0.0.0.0] quit
[HUAWEI-ospf-1] quit
```

### 步骤 3: 保存配置
```
<HUAWEI> save
```

## 验证命令
```
<HUAWEI> display ospf peer brief
<HUAWEI> display ospf routing
<HUAWEI> display ip routing-table protocol ospf
```

## 注意事项
- Router ID 建议使用设备的 Loopback 接口地址
- network 命令中的掩码是反掩码格式（0.0.0.255 表示 /24）
- 确保邻居设备也配置了 OSPF c并在同一区域
````

### 场景 2: NAT 配置

**用户输入:**
> 配置 NAT 地址池，公网地址 1.1.1.10-1.1.1.20，内网 192.168.1.0/24 访问外网

**AI 响应:**

````markdown
## 配置目标
配置源 NAT，使内网 192.168.1.0/24 通过地址池 1.1.1.10-1.1.1.20 访问外网

## 配置步骤

### 步骤 1: 配置安全区域
```
<HUAWEI> system-view
[HUAWEI] firewall zone trust
[HUAWEI-zone-trust] add interface GigabitEthernet0/0/1
[HUAWEI-zone-trust] quit

[HUAWEI] firewall zone untrust
[HUAWEI-zone-untrust] add interface GigabitEthernet0/0/2
[HUAWEI-zone-untrust] quit
```

### 步骤 2: 创建 NAT 地址池
```
[HUAWEI] nat address-group natpool1
[HUAWEI-address-group-natpool1] mode pat
[HUAWEI-address-group-natpool1] section 0 1.1.1.10 1.1.1.20
[HUAWEI-address-group-natpool1] quit
```

### 步骤 3: 配置安全策略
```
[HUAWEI] security-policy
[HUAWEI-policy-security] rule name allow_internet
[HUAWEI-policy-security-rule-allow_internet] source-zone trust
[HUAWEI-policy-security-rule-allow_internet] destination-zone untrust
[HUAWEI-policy-security-rule-allow_internet] source-address 192.168.1.0 mask 255.255.255.0
[HUAWEI-policy-security-rule-allow_internet] action permit
[HUAWEI-policy-security-rule-allow_internet] quit
[HUAWEI-policy-security] quit
```

### 步骤 4: 配置 NAT 策略
```
[HUAWEI] nat-policy
[HUAWEI-policy-nat] rule name nat_outbound
[HUAWEI-policy-nat-rule-nat_outbound] source-zone trust
[HUAWEI-policy-nat-rule-nat_outbound] destination-zone untrust
[HUAWEI-policy-nat-rule-nat_outbound] source-address 192.168.1.0 mask 255.255.255.0
[HUAWEI-policy-nat-rule-nat_outbound] action source-nat address-group natpool1
[HUAWEI-policy-nat-rule-nat_outbound] quit
[HUAWEI-policy-nat] quit
```

## 验证命令
```
<HUAWEI> display nat session all
<HUAWEI> display nat address-group natpool1
<HUAWEI> display firewall session table
```

## 注意事项
- 地址池使用 PAT 模式可以节省公网 IP
- 确保路由配置正确，内网流量能到达防火墙
- 在 ISP 路由器上需要配置到地址池的回程路由
````

### 场景 3: ACL 配置

**用户输入:**
> 创建 ACL 允许 192.168.1.0/24 访问 Web 服务器 10.1.1.100 的 80 和 443 端口

**AI 响应:**

````markdown
## 配置目标
创建高级 ACL，允许 192.168.1.0/24 访问 Web 服务器 10.1.1.100 的 HTTP(80) 和 HTTPS(443) 端口

## 配置步骤

### 步骤 1: 创建高级 ACL
```
<HUAWEI> system-view
[HUAWEI] acl number 3000
[HUAWEI-acl-adv-3000] rule 10 permit tcp source 192.168.1.0 0.0.0.255 destination 10.1.1.100 0 destination-port eq 80
[HUAWEI-acl-adv-3000] rule 20 permit tcp source 192.168.1.0 0.0.0.255 destination 10.1.1.100 0 destination-port eq 443
[HUAWEI-acl-adv-3000] quit
```

### 步骤 2: (可选) 应用到接口
```
[HUAWEI] interface GigabitEthernet0/0/1
[HUAWEI-GigabitEthernet0/0/1] traffic-filter outbound acl 3000
[HUAWEI-GigabitEthernet0/0/1] quit
```

## 验证命令
```
<HUAWEI> display acl 3000
<HUAWEI> display traffic-filter applied-record
```

## 注意事项
- ACL 3000-3999 是高级 ACL，可以匹配协议、端口等
- 规则编号决定匹配顺序，数字小的先匹配
- 使用反掩码格式（0.0.0.255 表示 /24）
- 默认 ACL 最后有隐式拒绝所有规则
````

## 高级查询示例

### 组合条件查询

```bash
# 查询 BGP 邻居配置，返回 10 个结果
python scripts/query_huawei.py "BGP peer neighbor AS" --protocol bgp --top-k 10

# 查询 IPsec VPN 配置，详细模式
python scripts/query_huawei.py "IPsec tunnel SA" --protocol ipsec --verbose

# 查询防火墙安全策略，JSON 输出
python scripts/query_huawei.py "security-policy rule action permit" --protocol firewall --json
```

### 批量查询脚本

```bash
#!/bin/bash
# query_all.sh - 批量查询常见配置

protocols=("ospf" "bgp" "nat" "ipsec" "acl" "firewall")

for proto in "${protocols[@]}"; do
    echo "=== $proto 配置 ==="
    python scripts/query_huawei.py "基础配置" --protocol "$proto" --top-k 3
    echo
done
```

## JSON 输出处理

```bash
# 查询并保存为 JSON
python scripts/query_huawei.py "OSPF 配置" --json > ospf_config.json

# 使用 jq 处理
python scripts/query_huawei.py "OSPF 配置" --json | jq '.[0].commands'

# 提取所有命令
python scripts/query_huawei.py "NAT 配置" --json | jq -r '.[].commands' | sort -u
```

## 监控摄入进度

```bash
# 查看摄入日志
tail -f ~/.local/share/huawei-rag/ingest.log

# 检查文档数量
python -c "
import chromadb
client = chromadb.PersistentClient(path='~/.local/share/huawei-rag/data/chroma')
collection = client.get_collection('huawei_docs')
print(f'Total documents: {collection.count()}')
"

# 查看摄入进程
ps aux | grep ingest.py
```
