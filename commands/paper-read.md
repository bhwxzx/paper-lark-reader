# 阅读论文

## 触发条件

用户要求阅读、精读、总结 PDF 论文，或生成论文笔记时使用。首次给出 PDF 并要求“帮我阅读下这篇论文”“总结这篇论文”“精读这个 PDF”“分析这篇论文”等，都必须进入本流程。

默认行为是生成本地 Markdown 论文笔记。不得把首次论文阅读请求降级为只在聊天里给摘要；只有用户明确要求“只要聊天总结”“不生成笔记”“离线口头总结”时，才可不生成笔记，并必须说明未使用飞书标签、出版选项和研究画像。

执行前读取：

- `references/note-writing-guide.md`
- `references/publication-policy.md`
- `references/command-pitfalls.md`

## 输入

- 一个本地 PDF 路径（通常位于 `papers/<paper_name>/<paper_name>.pdf`）。
- 已初始化且可访问的飞书论文知识库；若用户明确要求离线阅读，可生成本地笔记，但必须说明未使用飞书标签、出版选项和研究画像。

## 前置检查

禁止快捷摘要：读取 PDF 后不得直接输出最终阅读总结来替代本流程。必须先完成环境检查和论文库只读上下文获取。
由于沙箱环境限制，调用 Python 脚本必须使用项目根目录下的 `py.cmd`。

```bash
& ".\py.cmd" scripts/paper_lark_cli.py check
```

定位 skill 根目录：包含 `SKILL.md` 的 `paper-lark-reader/` 目录。读取 `<SKILL_ROOT>/config/defaults.json`，确认存在 `space_id`、`app_token` 和 `table_id`，并只读验证目标库可访问。

## 步骤

### 1. 获取论文库上下文与研究画像（必需）

**第一步：获取已有选项**
只读获取 Base 字段配置，用于取得 `标签` 和 `出版` 的现有选项。不需要读取已有论文索引记录或 `年份` 选项：
```bash
npx lark-cli base +field-list \
  --base-token <app_token> \
  --table-id <table_id>
```

**第二步：获取研究画像（🚨 优先本地读取）**
为了提速并节省配额，**必须优先**在当前工作区根目录查找并直接读取本地的 `研究概述.md` 文件。
只有当本地不存在该文件时，才允许 fallback 到通过飞书 CLI 查找云端节点：
```bash
npx lark-cli wiki nodes list --params '{"space_id":"<space_id>","page_size":50}'
# 若找到节点，再使用 docs +fetch 获取内容
```
获取到的画像内容将用于撰写笔记中的`评价与启发`章节。若均读取失败，提示用户并进入离线确认门。

### 2. PDF 预处理与隔离输出

必须将产生的中间文件隔离存放到 PDF 所在目录的 `notes/` 子文件夹中。若该子文件夹不存在，需自动创建。

```bash
& ".\py.cmd" scripts/paper_lark_cli.py paper-prep \
  --pdf <paper_dir>/<paper_name>.pdf \
  --output <paper_dir>/notes/<paper_name>.context.json \
  --write-intermediates
```

若已知 DOI，加 `--doi 10.xxxx/xxxxx` 提高出版核验准确率。
依赖链 `extract -> metadata -> infer` 必须串行执行，禁止把依赖前一步输出文件的命令放进并行工具调用。

### 3. 判断出版信息

基于 `notes/<paper_name>.context.json` 中的 `metadata` 和 `publication` 判断出版、年份和置信度。联网核验只用于出版元数据，不用于扩写论文内容。

若 Crossref 失败但 PDF 内部包含明确 DOI、venue 和 year，可继续生成本地笔记。`出版` 优先复用步骤 1 中获取的已有选项；无合适选项时按常用简称生成候选。

### 4. 生成笔记

使用 `templates/paper-note.md`。关键规则：

- `Title`：规范为 Title Case；不破坏模型名、缩写、基因/蛋白名和连字符词。
- `Abstract`：保留英文原意，不改写成总结。
- `标题`：`Title` 的忠实中文翻译。
- `摘要`：`Abstract` 的忠实中文翻译。
- `出版`：优先复用已有出版选项；无合适选项时生成候选。
- `标签`：结合论文内容和已有标签建议 2-4 个；优先复用已有标签。
- `评价与启发`：区分作者客观结论、你的推断，**必须显式结合步骤 1 中读取的《研究概述》**，说明本文的方法或缺陷如何启发用户的特定研究方向。

### 5. 写入本地笔记

在 PDF 所在目录的 `notes/` 子文件夹中生成或更新笔记，文件严格命名为 `<paper_name>.paper-note.md`：

- 首次阅读默认生成新笔记。
- 已存在同题或同路径笔记时，先展示已有笔记路径、将被修改的章节和可能覆盖的内容；只有用户确认后才更新既有笔记。
- 只有用户明确要求保留旧版时，才另存新副本。

写完后校验：

```bash
& ".\py.cmd" scripts/paper_lark_cli.py note-check <paper_dir>/notes/<paper_name>.paper-note.md
```

聊天输出只作为笔记完成后的简短回报，不得用聊天输出替代 Markdown 文件的生成。

## 停止条件

- `Title` 或 `Abstract` 低置信度且无法人工确认时，不上传。
- 中文标题或中文摘要缺失时，不上传。
- 出版或年份冲突且未确认时，不上传。

## 验收

- 本地笔记及 JSON 伴生文件正确存放在 `notes/` 子目录下。
- 笔记通过了 `note-check` 校验。
- 元数据表只包含：`Title、出版、年份、标签、评分、Abstract、标题、摘要`。
- `摘要` 是英文 Abstract 的中文翻译，不是总结。
- 若已有笔记被更新，更新前已获得用户确认。

## 反例

- 不要把 AI 总结写进 `摘要` 字段。
- 不要从文件名猜出版和年份后直接写入。
- 不要在首次给出 PDF 并要求阅读时只给聊天摘要；必须按本流程生成并校验本地笔记。
- **不要把笔记文件和 JSON 生成在与 PDF 平级的目录下，必须放入 `notes/`。**
