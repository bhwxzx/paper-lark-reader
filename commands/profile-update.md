# 生成或更新研究画像

## 触发条件

用户明确要求生成或更新研究画像、研究概述或研究方向总结时使用。

画像生成或更新是独立流程；读论文、讨论或上传时不要自动触发。

执行前读取：

- `references/lark-workflows.md`
- `references/command-pitfalls.md`
- `templates/research-profile.md`

## 硬性规则

画像只能来自：
- 用户提供的研究领域关键词。
- 现有 `研究概述` 中已沉淀的研究关键词和画像级概括。
- 已归档 Base 论文索引字段：`Title`、`Abstract`、`标签`、`年份`、`出版`。

不得读取本地 `*.paper-note.md`、PDF 抽取文本、`*.context.json`、`*.text.json` 或任何单篇全文笔记来扩写画像。

## 前置检查

定位 skill 根目录：包含 `SKILL.md` 的 `paper-lark-reader/` 目录。读取 `<SKILL_ROOT>/config/defaults.json`，不要读取当前项目目录下的同名文件。若 `space_id`、`app_token` 或 `table_id` 缺失，停止并提示用户先执行建库流程。

```bash
& ".\py.cmd" scripts/paper_lark_cli.py check
```

## 步骤

### 1. 收集用户关键词

提示用户提供研究领域关键词。若用户已在请求中给出关键词（如：强化学习、运控、Sim2Real），直接使用。

### 2. 获取已有论文索引

调用飞书 API 读取 Base 里的已读论文大盘数据。为防止日志过长，使用静默重定向，你只需要关注 `record_list.json` 中保存的数据。
```bash
npx lark-cli base +record-list \
  --base-token <app_token> \
  --table-id <table_id> \
  --field-id Title \
  --field-id Abstract \
  --field-id 标签 \
  --field-id 年份 \
  --field-id 出版 \
  --limit 200 > record_list.json
```
如果 Base 为空，则只能基于用户的核心词生成初始画像，并注明数据不足。如果有现有 `研究概述` 节点，可获取并参考其正文。

### 3. 生成画像内容 (核心)

使用 `templates/research-profile.md` 作为基础骨架，将生成的 Markdown 内容严格写入本地文件 `研究概述.md`（保存在 `papers/` 根目录或当前工作目录即可）。

**填充要求（必须对齐模板的五章结构）：**
- **第 1 章（关键词）**：填入用户的核心方向和出现频率最高的标签。
- **第 2 章（大盘）**：统计 `record_list.json` 里的年份跨度和高频出版会议/期刊。
- **第 3 章（痛点）**：从 Abstract 归纳出用户正在试图解决的技术难点（如奖励函数设计、模型泛化性）。
- **第 4 章（技术偏好）**：从标签和 Abstract 里找出用户爱看的路线（如 PPO、Isaac Gym 等仿真器）。
- **第 5 章（阅读备忘录）**：🚨 **极其重要！** 请你化身为 AI 秘书，基于上述 1~4 章的归纳，为自己定下 3 条铁规：“未来在阅读新的控制/RL论文时，我必须帮用户重点寻找/高亮哪些内容？”

**飞书防坑强制命令：**
生成的 `研究概述.md` 第一行，**必须、绝对**是 `# 研究概述`。绝不能用其他大标题，否则上传时飞书 API 会强制把文档名改为 `Untitled`！

### 4. 预览并确认

在聊天窗口中向用户展示这 5 章的精简预览。覆盖飞书云端已有 `研究概述` 前必须获得用户确认。

### 5. 写入飞书

列出知识库根节点：
```bash
npx lark-cli wiki nodes list --params '{"space_id":"<space_id>","page_size":50}'
```

**分支 A：若找到标题为 `研究概述` 且 `obj_type` 为 `docx` 的节点**
确认覆盖影响后写入：
```bash
npx lark-cli docs +update \
  --api-version v2 \
  --doc <doc_token> \
  --command overwrite \
  --doc-format markdown \
  --content @研究概述.md > .lark_temp.log

npx lark-cli drive files patch \
  --params '{"file_token":"<doc_token>","type":"docx"}' \
  --data '{"new_title":"研究概述"}' > .lark_temp.log
```

**分支 B：若未找到，则创建新节点**
```bash
npx lark-cli wiki +node-create \
  --space-id <space_id> \
  --obj-type docx \
  --title "研究概述"
```
记录返回的 `obj_token` 为 `<doc_token>`，`node_token` 为 `<node_token>`。
然后执行写入并修正标题：
```bash
npx lark-cli docs +update \
  --api-version v2 \
  --doc <doc_token> \
  --command overwrite \
  --doc-format markdown \
  --content @研究概述.md > .lark_temp.log

npx lark-cli drive files patch \
  --params '{"file_token":"<doc_token>","type":"docx"}' \
  --data '{"new_title":"研究概述"}' > .lark_temp.log
```

回读验证标题（每次 overwrite 后必须执行）：
```bash
npx lark-cli wiki spaces get_node --params '{"token":"<node_token>"}'
```

### 6. 清理临时文件
执行完毕后，清理静默日志和包含全部 Base 记录的巨大临时 JSON，释放空间：
```bash
Remove-Item -Path .lark_temp.log, record_list.json -Force -ErrorAction SilentlyContinue
```

## 输出

返回：
- `node_token`
- `obj_token`
- Wiki 链接优先使用命令返回的 URL；若返回值缺失，fallback 为 `https://www.feishu.cn/wiki/<node_token>`

## 验收

- 生成的 Markdown 完整包含五大结构，第一行标题必定是 `# 研究概述`。
- 画像的论点全部有已读论文（Abstract 或标签）的支撑。
- 覆盖已有 `研究概述` 前已获得了确认。
- 飞书文档标题回读为 `研究概述`。

## 反例

- 不要在用户未提供关键词时编造研究领域。
- 不要把单篇论文特有的超参数当作“长期方法偏好”。
- 绝不读取本地笔记文件或单篇论文的 PDF JSON。
- **绝不允许生成的 Markdown 文件漏掉顶部的 `# 研究概述` 一级标题。**