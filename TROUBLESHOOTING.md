# 故障排查指南

## 常见问题和解决方案

### 问题 1: AI 生成的命令不正确

#### 症状
- 命令语法错误
- 参数不适配环境
- 缺少必要步骤
- 配置顺序错误

#### 解决方案

**步骤 1: 使用详细模式重新查询**
```bash
cd ~/.local/share/huawei-rag/scripts
python query_huawei.py "你的需求" --verbose --top-k 10
```

**步骤 2: 调整查询关键词**
```bash
# 示例：OSPF 配置
python query_huawei.py "OSPF area 配置"           # 尝试 1
python query_huawei.py "OSPF 区域 network 命令"  # 尝试 2
python query_huawei.py "OSPF 邻居建立过程"       # 尝试 3
```

**步骤 3: 添加协议过滤**
```bash
python query_huawei.py "你的需求" --protocol ospf --top-k 5
```

**步骤 4: 查看源文档**
```bash
# 从查询结果中获取源文件名，然后查看原文
find /tmp/huawei_chm_extract -name "文件名.html" | xargs cat
```

**步骤 5: 交叉验证多个结果**
对比前 5 个查询结果，找共同点和差异点。

---

### 问题 2: 查询结果不相关

#### 症状
- 返回的文档与需求不匹配
- 协议类型错误
- 相似度分数很低 (<30%)

#### 解决方案

**方法 1: 使用更具体的关键词**
```bash
# ❌ 太泛
python query_huawei.py "配置"

# ✅ 具体
python query_huawei.py "OSPF 单区域基础配置 area 0"
```

**方法 2: 添加协议过滤**
```bash
python query_huawei.py "配置命令" --protocol ospf
```

**方法 3: 检查数据库状态**
```bash
python -c "
import chromadb
client = chromadb.PersistentClient(path='/Users/ccc/.local/share/huawei-rag/data/chroma')
collection = client.get_collection('huawei_docs')
print(f'Total documents: {collection.count()}')

# 检查协议分布
results = collection.get(limit=100)
protocols = [m.get('protocol', 'unknown') for m in results['metadatas']]
from collections import Counter
print('Protocol distribution:', Counter(protocols))
"
```

如果文档数量太少（<1000），说明摄入未完成，等待后台任务完成。

---

### 问题 3: 命令参数需要调整

#### 症状
- 命令正确，但 IP、接口名、区域号等需要修改

#### 解决方案

**这是正常的！** AI 生成的是模板命令，你需要根据实际环境调整：

**常见需要替换的参数：**
- **Router ID**: `1.1.1.1` → 你的 Loopback IP
- **接口名**: `GigabitEthernet0/0/1` → 实际接口
- **IP 地址**: `192.168.1.0/24` → 实际网段
- **区域号**: `area 0` → 实际区域
- **AS 号**: `65001` → 实际 AS

**推荐做法：**
1. 先在测试环境验证命令
2. 复制命令到文本编辑器
3. 批量替换参数
4. 逐条执行并验证

---

### 问题 4: 缺少某些配置步骤

#### 症状
- 命令不完整
- 缺少前置配置
- 缺少验证步骤

#### 解决方案

**方法 1: 查询相关步骤**
```bash
# 分别查询各个步骤
python query_huawei.py "OSPF 接口配置" --protocol ospf
python query_huawei.py "OSPF 区域配置" --protocol ospf
python query_huawei.py "OSPF 验证命令" --protocol ospf
```

**方法 2: 查看完整配置案例**
```bash
python query_huawei.py "OSPF 配置案例 example" --protocol ospf --verbose
```

**方法 3: 使用 AI Skill 时明确需求**
在 OpenCode 中，明确告诉 AI：
> "帮我生成完整的 OSPF 配置，包括接口配置、区域配置、验证命令"

---

### 问题 5: 向量数据库查询慢

#### 症状
- 查询需要 10+ 秒
- 首次查询特别慢

#### 解决方案

**原因**: 首次加载嵌入模型需要时间（~670MB）

**优化方法：**
1. **保持查询脚本运行**（如果需要多次查询）
2. **使用 Python 交互模式**：
```python
# 启动一次，多次查询
python
>>> from query_huawei import query
>>> results = query("OSPF 配置", top_k=5)
>>> results = query("NAT 配置", top_k=5)  # 模型已加载，快很多
```

3. **批量查询脚本**：
```python
# batch_query.py
from query_huawei import query
import sys

queries = [
    "OSPF 配置",
    "BGP 配置",
    "NAT 配置",
    "IPsec 配置"
]

for q in queries:
    print(f"\n{'='*60}")
    print(f"Query: {q}")
    print('='*60)
    results = query(q, top_k=3)
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r['title']}")
        print(f"Commands: {r['commands'][:200]}...")
```

---

### 问题 6: 数据库损坏或需要重建

#### 症状
- 查询报错
- 返回结果异常
- 数据库文件损坏

#### 解决方案

**重建数据库：**
```bash
cd ~/.local/share/huawei-rag/scripts

# 停止正在运行的摄入进程
pkill -f ingest.py

# 删除旧数据库
rm -rf ~/.local/share/huawei-rag/data/chroma

# 重新摄入
python ingest.py --source /tmp/huawei_chm_extract/ --reset
```

---

## 改进建议

### 1. 创建自定义查询别名

在 `~/.bashrc` 或 `~/.zshrc` 添加：
```bash
alias hw-query='cd ~/.local/share/huawei-rag/scripts && python query_huawei.py'
alias hw-ospf='hw-query "OSPF 配置" --protocol ospf --verbose'
alias hw-nat='hw-query "NAT 配置" --protocol nat --verbose'
alias hw-vpn='hw-query "IPsec VPN" --protocol ipsec --verbose'
```

使用：
```bash
hw-ospf
hw-nat
hw-vpn "site to site"
```

### 2. 创建验证脚本

```bash
# verify_commands.sh
#!/bin/bash
# 验证生成的命令语法（模拟）

commands_file="$1"

if [ ! -f "$commands_file" ]; then
    echo "Usage: $0 <commands_file>"
    exit 1
fi

echo "Validating Huawei CLI commands..."

# 检查常见错误
grep -n "as any\|@ts-ignore" "$commands_file" && echo "⚠️  Found suspicious patterns"
grep -n "TODO\|FIXME" "$commands_file" && echo "⚠️  Found placeholder markers"

# 检查必要命令
grep -q "system-view" "$commands_file" || echo "⚠️  Missing 'system-view' command"
grep -q "quit\|return" "$commands_file" || echo "⚠️  Missing exit command"

echo "✅ Basic validation complete"
```

### 3. 添加反馈机制（未来功能）

可以扩展系统记录哪些查询效果好/不好：
```python
# 在 query_huawei.py 中添加
def rate_result(query_id, rating):
    """记录查询结果质量"""
    with open('~/.local/share/huawei-rag/ratings.jsonl', 'a') as f:
        f.write(json.dumps({
            'query_id': query_id,
            'rating': rating,  # 1-5
            'timestamp': time.time()
        }) + '\n')
```

---

## 最佳实践

### ✅ DO (推荐做法)

1. **始终使用 `--verbose` 查看完整上下文**
2. **对比多个结果（--top-k 5-10）**
3. **使用协议过滤器精确查询**
4. **在测试设备上验证命令**
5. **保存常用查询为脚本/别名**
6. **查询结果保存为文档供团队参考**

### ❌ DON'T (避免做法)

1. **不要盲目复制粘贴命令到生产环境**
2. **不要忽略相似度分数（<50% 需谨慎）**
3. **不要只看第一个结果**
4. **不要跳过参数替换步骤**
5. **不要在未完成摄入时期待完美结果**

---

## 获取帮助

### 查看文档
- GitHub README: https://github.com/ckj313/huawei-rag-assistant
- 使用示例: EXAMPLES.md
- 本故障排查: TROUBLESHOOTING.md

### 检查系统状态
```bash
# 检查摄入进度
tail -f ~/.local/share/huawei-rag/ingest.log

# 检查文档数量
python -c "import chromadb; c=chromadb.PersistentClient(path='/Users/ccc/.local/share/huawei-rag/data/chroma'); print(c.get_collection('huawei_docs').count())"

# 检查进程
ps aux | grep ingest.py
```

### 重新开始
```bash
# 完全重置并重建
pkill -f ingest.py
rm -rf ~/.local/share/huawei-rag/data/chroma
cd ~/.local/share/huawei-rag/scripts
python ingest.py --source /tmp/huawei_chm_extract/ --reset
```
