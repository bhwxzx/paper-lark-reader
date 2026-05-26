# 上传笔记和翻译到飞书

## 触发条件

用户要求上传、归档、写入论文索引、同步到飞书论文库时使用。

执行前读取：

- `references/lark-workflows.md`
- `references/note-writing-guide.md`
- `references/command-pitfalls.md`
- `templates/upload-preview.md`

## 硬性规则

- `Title`、`Abstract`、`标题`、`摘要` 只能从 Markdown 笔记 `## 元数据` 表复制。
- 主 PDF 只上传到 Base 附件字段一次，命名为 `paper.pdf`。
- `笔记` 和 `翻译` 字段必须是 URL 样式，链接到对应的飞书子文档。
- 子文档创建后标题绝对不能是 `Untitled`。

## 前置检查

定位 skill 根目录：包含 `SKILL.md` 的 `paper-lark-reader/` 目录。读取 `<SKILL_ROOT>/config/defaults.json`，不要读取当前项目目录下的同名文件。

确认配置中存在：
- `space_id`、`app_token`、`table_id`
- `note_parent_doc_token`、`note_parent_node_token`
- `trans_parent_doc_token`、`trans_parent_node_token`（可选，若存在则支持翻译上传）

运行：
```bash
python scripts/paper_lark_cli.py check
```
若字段缺失、目标库不可访问或权限不足，停止并提示用户先执行建库流程或修复飞书 CLI/权限。

### 0. 智能探测上传物料
在用户指定的 PDF 同级目录下寻找 `notes/*.paper-note.md` 作为主笔记文件。
同时探测是否存在 `translation/*_translated.md`。若存在，标记为**【双轨上传模式】**。

## 步骤

### 1. 校验本地笔记

```bash
python scripts/paper_lark_cli.py note-check <paper_dir>/notes/<NOTE.md>
```
若输出 `ok: false`，修正后再继续。

### 2. 重复检测

在 Base 中搜索同 Title 记录。`+record-search.keyword` 最长 50 字符；长标题截取稳定短关键词，命中后必须人工比对完整 `Title`。
```bash
lark-cli base +record-search \
  --base-token <app_token> \
  --table-id <table_id> \
  --json '{"keyword":"<Title 前 50 字符或稳定短关键词>","search_fields":["Title"]}'
```

命中重复时，展示已有记录；用户确认后走更新分支。只有用户明确要求新增时才创建重复记录。

### 3. 更新已有记录（针对云端已存在的情况）
若用户确认更新已有云端记录，先展示将覆盖或保留的内容。
1. 解析已有的笔记或翻译子文档 token，执行 `docs +update` 覆盖正文内容。
2. 同步并回读验证标题（见步骤 6 的标题修正逻辑）。
3. 只有用户明确确认具体字段或附件变更时，才更新 Base 其他字段或重新上传附件。

### 4. 上传前预览（关键防御）
按 `templates/upload-preview.md` 展示上传规划（如果是双轨上传，必须明示两个文档将被创建）。
若 `出版`、`年份` 或 `标签` 缺少待写选项，先展示新增理由、当前已有选项和完整更新后的选项列表，获得确认后再用 `+field-update` 串行追加。

### 5. 创建子文档（单轨或双轨）

**创建笔记文档（必需）：**
```bash
lark-cli wiki +node-create \
  --space-id <space_id> \
  --parent-node-token <note_parent_node_token> \
  --obj-type docx \
  --title "<论文 Title>"
```
记录 `child_note_token` 和对应的 Wiki URL。

**创建翻译文档（若探测到翻译文件）：**
```bash
lark-cli wiki +node-create \
  --space-id <space_id> \
  --parent-node-token <trans_parent_node_token> \
  --obj-type docx \
  --title "<论文 Title>" 
```
记录 `child_trans_token` 和对应的 Wiki URL。

### 6. 写入文档并修正标题

分别对笔记（和翻译）执行以下操作。为节省 Token，这里将冗长的成功日志静默输出到临时文件，AI 只需关注是否报错：
1. 写入内容（直接传入文件路径）：
```bash
# 写入笔记 (使用 npx 防止路径错位，并静默输出)
npx lark-cli docs +update \
  --api-version v2 \
  --doc <child_note_token> \
  --command overwrite \
  --doc-format markdown \
  --content @<paper_dir>/notes/<NOTE_MD的文件名> > .lark_temp.log

# 如果是双轨模式，再写入翻译
npx lark-cli docs +update \
  --api-version v2 \
  --doc <child_trans_token> \
  --command overwrite \
  --doc-format markdown \
  --content @<paper_dir>/translation/<TRANS_MD的文件名> > .lark_temp.log
```

2. 同步标题并回读验证（每次 overwrite 后必须执行）：
```bash
npx lark-cli drive files patch \
  --params '{"file_token":"<child_doc_token>","type":"docx"}' \
  --data '{"new_title":"<目标标题>"}' > .lark_temp.log

npx lark-cli wiki spaces get_node --params '{"token":"<对应的_node_token>"}'
```
若仍为 `Untitled`，不得继续后续步骤。

### 7. 创建 Base 记录

字段值严格来自笔记 `## 元数据` 表，`状态` 固定为 `待读`。如果是【双轨模式】，留空 `笔记` 和 `翻译`，由下一步统一更新；若是新增则一并写入。
*(注意：此步需要获取 record_id，绝对不能加静默输出！)*
```bash
npx lark-cli base +record-batch-create \
  --base-token <app_token> \
  --table-id <table_id> \
  --json '{"fields":["Title","出版","年份","状态","标签","评分","Abstract","标题","摘要"],"rows":[["<Title>","<出版>","<年份>","待读",["<标签>"],3,"<Abstract>","<标题>","<摘要>"]]}'
```
记录返回的 `record_id`。

### 8. 上传 PDF 附件

`--file` 使用相对路径。附件上传的返回日志极大，必须静默输出。
```bash
npx lark-cli base +record-upload-attachment \
  --base-token <app_token> \
  --table-id <table_id> \
  --record-id <record_id> \
  --field-id "附件" \
  --file <PDF路径> \
  --name "paper.pdf" > .lark_temp.log
```

### 9. 回写飞书链接

根据步骤 5 记录的 URL，回写文档链接到 Base 中。更新日志必须静默输出：
若是双轨模式：
```bash
npx lark-cli base +record-batch-update \
  --base-token <app_token> \
  --table-id <table_id> \
  --json '{"record_id_list":["<record_id>"],"patch":{"笔记":"[笔记](<child_note_url>)","翻译":"[全文翻译](<child_trans_url>)"}}' > .lark_temp.log
```
若仅上传笔记，则只 patch `笔记` 字段。

### 10. 清理临时文件

任务完成后，务必清理产生的静默输出日志和其他可能生成的传参临时文件：
```bash
Remove-Item -Path .lark_temp.log -Force -ErrorAction SilentlyContinue
```

## 验收

- 笔记子文档在 `论文笔记` 下，翻译子文档（若有）在 `全文翻译` 下；标题绝不能为 `Untitled`。
- Base 记录存在，`状态 = 待读`，`评分 = 3`（除非用户修改）。
- `笔记` 和 `翻译` 字段正确填入了带 URL 格式的超链接。
- 附件里只有一个主文件 `paper.pdf`。
- `Title`、`Abstract`、`标题`、`摘要` 与笔记元数据表逐字一致。
- 确认临时文件已经清理干净。
