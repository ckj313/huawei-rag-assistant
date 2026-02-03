# OpenCode AI Skills

## 安装 Skill

将 skill 复制到 OpenCode skills 目录：

```bash
# 完整安装（推荐）
cp -r skills/huawei-network-config ~/.config/opencode/skills/

# 验证安装
ls -la ~/.config/opencode/skills/huawei-network-config/SKILL.md
```

## Skill 文件结构

OpenCode skill 标准格式：

```
skill-name/
  SKILL.md              # 必需：Skill 定义文件
  supporting-file.*     # 可选：支持文件
```

**重要**: 文件必须命名为 `SKILL.md`（全大写），OpenCode 才能识别。

## 使用 Skill

安装后，在 OpenCode 中询问华为配置相关问题时，AI 会自动加载此 skill：

**示例对话：**

> 👤 帮我配置 OSPF 区域 0
> 
> 🤖 *自动加载 huawei-network-config skill*
> 
> 我来查询华为文档并生成配置...
> 
> ```bash
> <HUAWEI> system-view
> [HUAWEI] ospf 1 router-id 1.1.1.1
> [HUAWEI-ospf-1] area 0
> ...
> ```

## Skill 触发条件

AI 会在以下情况自动使用此 skill：

- 用户询问华为 USG 防火墙配置
- 提到网络协议（OSPF, BGP, IPsec, VPN, NAT, ACL）
- 关键词：华为、USG、防火墙、安全策略、路由协议

## 手动测试 Skill

```bash
# 查询文档（手动方式）
cd ../scripts
python query_huawei.py "OSPF 配置" --protocol ospf --verbose

# 检查查询质量
python check_quality.py "OSPF 配置" --protocol ospf
```

## Skill 工作原理

1. **触发**: AI 识别到华为配置相关问题
2. **查询**: 调用 `query_huawei.py` 搜索向量数据库
3. **提取**: 从查询结果中提取相关命令
4. **生成**: 根据用户需求组织配置命令
5. **输出**: 返回格式化的配置步骤

## 注意事项

- ⚠️ Skill 依赖向量数据库，需先运行 `ingest.py` 摄入文档
- ⚠️ 生成的命令需要人工验证后再执行
- ⚠️ 参数需要根据实际环境调整（IP、接口名等）

## 更多信息

- [Skill 详细说明](huawei-network-config/SKILL.md)
- [项目文档](../README.md)
- [使用示例](../EXAMPLES.md)
- [故障排查](../TROUBLESHOOTING.md)
