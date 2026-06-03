# 命令陷阱与查阅规则

执行任何 `lark-cli` 命令前必须阅读本文件。

本 skill 不绑定固定 `lark-cli` 版本。执行前以当前环境的 `--help` 或 `schema` 确认参数；若 help 与已验证行为冲突，优先使用本文记录的已验证命令形态并记录错误。

## 网络与代理环境禁令

当前工作环境依赖特定的海外代理节点来维持你的后台大脑连接，访问国内飞书 API 出现网络延迟、卡顿或超时属于**完全正常的现象**。

为了防止网络环境被破坏导致你的进程崩溃，你必须**绝对遵守**以下三条纪律：
1. **禁止一切网络连通性测试**：**绝对禁止**使用 `curl`、`ping`、`Test-NetConnection` 或 `Get-NetTCPConnection` 等命令去测试飞书服务器是否连通。
2. **严禁修改网络配置**：**绝对禁止**尝试查询、重启、禁用或修改任何网络适配器（如 `Disable-NetAdapter`、`Clash` 网卡等），也绝对禁止修改或清除终端的 `http_proxy` 环境变量。
3. **遇到超时的唯一解法（无脑重试）**：如果调用 `npx lark-cli` 或其他 API 时遇到网络超时、连接失败等报错，**禁止去排查网络原因**！你唯一的处理方式是：使用`for`循环，直接对报错的命令进行 3 到 5 次的自动重试（每次重试前 `sleep 2`）。

## 🚨 Python 虚拟环境执行禁令（致命规则）

本项目的所有本地 Python 解析脚本，严重依赖特定的 Conda 虚拟环境。由于后台终端可能丢失 `conda` 环境变量，**绝对禁止**使用 `python`、`python3` 或 `conda run` 开头执行脚本！

**唯一合法的执行格式**：每一次调用本地 Python 脚本时，必须使用项目根目录下的 `py.cmd` 作为代理执行器。格式必须固定为：
`& ".\py.cmd" scripts/<具体脚本名.py> <参数>`

## 查阅规则

构造命令前先确认参数格式：

```bash
# 查看原生命令请求结构
npx lark-cli schema <resource>.<method>

# 查看 CLI 版本；不要使用 `lark-cli version`
npx lark-cli --version

# 查看 shortcut 或原生命令 flag
npx lark-cli <resource> <cmd> --help
npx lark-cli <resource> +<shortcut> --help
```

| 类型 | 示例 | 参数方式 | `--format` |
|---|---|---|---|
| shortcut | `wiki +node-create` | 专属 flag，如 `--space-id` | 通常不支持 |
| 原生命令 | `wiki nodes list` | `--params '{"key":"val"}'` | 支持 |

Base 业务操作优先使用 `lark-cli base +...`。只有 shortcut 缺少必要能力时，才使用 `lark-cli api` 或原生命令，并且必须先查 schema/help。

## 已知陷阱

### P1 Wiki 原生命令参数走 `--params`

错误：

```bash
npx lark-cli wiki nodes list --space-id <space_id>
```

正确：

```bash
npx lark-cli wiki nodes list --params '{"space_id":"<space_id>","page_size":50}'
npx lark-cli wiki spaces get_node --params '{"token":"<wiki_node_token>"}'
```

### P2 `field-create/update` 的 `type` 使用字符串

错误：

```bash
--json '{"field_name":"Title","type":1}'
```

正确：

```bash
--json '{"name":"Title","type":"text"}'
```

### P3 `docs +update --api-version v2` 使用 `--command`

当前已验证的 v2 写 Markdown 兜底命令使用 `--command`、`--doc-format` 和 `--content`。如果 `docs +update --help` 展示 `--mode/--markdown`，但执行时报 `--command is required`，仍使用下面的已验证命令形态：

```bash
npx lark-cli docs +update \
  --api-version v2 \
  --doc <doc_token> \
  --command overwrite \
  --doc-format markdown \
  --content @<NOTE.md>
```

`@<file>` 按当前工作目录解析。跨目录时先 `cd` 到文件所在目录。标题同步使用 `drive files patch`。

`overwrite` 后标题可能回退为 `Untitled`。每次 `docs +update --command overwrite` 后，都要重新 `drive files patch` 并用 `wiki spaces get_node` 回读标题。

读取 docx 时不要使用不存在的 `--format markdown`；需要读取正文时使用默认 JSON、`--format pretty`，或按 `docs +fetch --help` 支持的格式选择。

### P4 `lark-cli api` 路径不加 `/open-apis`

错误：

```bash
npx lark-cli api GET /open-apis/<resource-path>
```

正确：

```bash
npx lark-cli api GET /bitable/v1/apps/...
```

CLI 会自动添加 `/open-apis` 前缀。

### P5 shortcut 不要加 `--format`

错误：

```bash
npx lark-cli wiki +node-create ... --format json
```

正确：

```bash
npx lark-cli wiki +node-create ...
```

需要结构化输出时优先使用 `-q/--jq`，或改用支持 `--format` 的原生命令。

### P6 `+record-delete` 一次只删一条

```bash
for rid in rec1 rec2; do
  npx lark-cli base +record-delete \
    --base-token <app_token> \
    --table-id <table_id> \
    --record-id "$rid" \
    --yes
done
```

### P7 批量删除字段要限速

```bash
for fid in fld1 fld2; do
  npx lark-cli base +field-delete \
    --base-token <app_token> \
    --table-id <table_id> \
    --field-id "$fid" \
    --yes
  sleep 2
done
```

连续字段删除可能触发频率限制。

### P8 创建知识库用 `--data`

```bash
npx lark-cli wiki spaces create \
  --data '{"name":"论文仓库","description":"学术论文管理知识库"}'
```

不要使用不存在的 `--name` 或 `--description` flag。

### P9 `+field-update` 是全量 PUT

更新选项前先读取现有字段：

```bash
npx lark-cli base +field-list --base-token <app_token> --table-id <table_id>
```

然后构造包含完整旧选项和新选项的 JSON：

```bash
npx lark-cli base +field-update \
  --base-token <app_token> \
  --table-id <table_id> \
  --field-id <field_id> \
  --json '{"name":"标签","type":"select","multiple":true,"options":[<已有选项...>,{"name":"新标签"}]}'
```

缺少 `name`、`type` 或完整 `options` 可能导致旧配置丢失。

连续更新多个字段可能触发 `OpenAPIUpdateField limited`。多个 `+field-update` 要串行执行，字段之间等待约 2 秒；限频后只重试失败字段。
