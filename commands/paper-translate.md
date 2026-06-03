# 论文全文翻译与精读

## 触发条件
当用户明确要求“全文翻译”、“逐节翻译这篇论文”、“把这篇论文完整翻译为中文”时触发。

## 目标
将外文 PDF 论文按原有章节结构，完整翻译为中文，生成符合飞书规范的 Markdown 文档。需保留原始排版层级、表格，并使用飞书兼容的纯文本视觉强调（替代不可用的 HTML 锚点）。

## 执行前读取
执行翻译前，必须先完整读取并严格遵循以下指南：
- `references/translation-guide.md`
- `references/command-pitfalls.md`

## 前置检查
禁止直接在聊天窗口内一次性输出全部翻译，因为超出 Token 限制会导致中断或省略。必须先调用本地 Python 脚本解析 PDF，并将产生的所有中间文件输出到 `translation/` 子目录中。

```bash
& ".\py.cmd" scripts/paper_lark_cli.py full-extract \
  --pdf <paper_dir>/<paper_name>.pdf \
  --output <paper_dir>/translation/<paper_name>.full_content.json \
  --extract-images true
```

## 翻译与生成步骤
全文翻译必须**分批次、按章节（Section）**进行。

### 1. 严格遵循翻译指南
翻译时，所有的术语映射、数学公式渲染、表格插入以及参考文献的 **[x]** 加粗处理，必须绝对服从 references/translation-guide.md。

### 2. 分批循环写入（防截断与防乱码）
 - 读取 <paper_dir>/translation/<paper_name>.full_content.json 的目录结构。
 - 在本地创建目标文件：<paper_dir>/translation/<paper_name>_translated.md。如果该文件已存在，必须先暂停向用户提示“文件已存在，是否清空并重新翻译覆盖？”，获得明确同意后才能清空该文件。
 - 逐个 Section 进行翻译。
 - 每翻译完一个 Section 并追加写入（Append）到本地文件时，绝对禁止使用 ```markdown 和 ``` 代码块语法进行包裹！必须以纯文本形式追加 Markdown 内容，否则最终文件会出现大量割裂的代码块背景。
 - 在聊天窗口中向用户简短汇报进度（例如：“第一章 Introduction 翻译完成，正在翻译第二章...”），然后自动触发工具调用继续翻译下一节，直至全文完成。

## 验收条件
 - 在本地正确生成了 <paper_dir>/translation/<paper_name>_translated.md 文件。
 - 正文的引用数字全部转为了 **[x]** 的飞书兼容加粗格式，全文绝不存在 <span id="..."> 或 [1](#ref-1) 等 HTML 标签。
 - 最终翻译文件内没有冗余的 ```markdown 语法残留。
 - 全文未出现因 Token 超限导致的“翻译未完成”或强行总结。
 - 最终翻译文件末尾必须包含完整的参考文献（References）章节，绝对不允许遗漏或只写个标题。