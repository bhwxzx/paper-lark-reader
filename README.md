# Paper Lark Reader

Paper Lark Reader 是一个用于学术论文阅读、结构化笔记生成、飞书论文库归档和用户画像沉淀的 skill。

它面向从 PDF 阅读到知识库沉淀的完整论文处理流程：读取学术论文 PDF，生成结构化中文精读笔记，支持围绕论文继续追问与修订，并将论文笔记、PDF 原件和索引记录归档到飞书论文知识库。随着归档论文积累，也可以用于生成和更新用户画像，为后续阅读提供更贴近研究方向的参考。

适合个人研究、课题组论文管理、长期文献追踪，以及希望把本地论文、阅读笔记和飞书知识库统一维护的场景。

## 亮点

- **自主建库**：辅助初始化飞书论文知识库，建立论文索引、论文笔记和用户画像的基础结构。
- **结构化笔记**：围绕研究问题、方法、数据、实验、结论、局限和启发生成中文精读笔记。
- **论文追问**：支持继续讨论论文的方法细节、实验设置、结论边界和潜在启发。
- **笔记修订**：可将追问中的纠错、补充材料或启发整理后写回已有论文笔记。
- **上传归档**：同步论文笔记、PDF 原件和索引记录到飞书论文知识库，便于后续检索和复盘。
- **用户画像**：基于已归档论文和用户提供的研究关键词，更新研究方向概述和阅读偏好。

## 适用场景

- 初始化或维护飞书论文知识库。
- 阅读、精读或总结学术论文 PDF。
- 生成结构化中文论文笔记。
- 继续追问论文的方法、数据、实验、结论和局限。
- 将讨论中的纠错、补充或启发写回已有笔记。
- 将论文笔记、PDF 和索引记录归档到飞书。
- 基于已归档论文更新用户画像。

## 安装

### Codex / Codex CLI

将 `paper-lark-reader` 放入 Codex 可发现的 skills 目录：

```bash
mkdir -p ~/.codex/skills
cp -R paper-lark-reader ~/.codex/skills/paper-lark-reader
```

也可以将该目录保留在当前项目中，作为项目内 skill 使用。

### Claude Code

安装到当前项目：

```bash
mkdir -p .claude/skills
cp -R paper-lark-reader .claude/skills/paper-lark-reader
```

安装到全局：

```bash
mkdir -p ~/.claude/skills
cp -R paper-lark-reader ~/.claude/skills/paper-lark-reader
```

## 环境要求

- Python 3.9+。
- 已安装并登录 `lark-cli`（推荐 `1.0.19` 版本）。
- 至少一种 PDF 文本抽取能力：`pdftotext`、`pdfplumber` 或 `pypdf`。
- 飞书账号具备 Wiki、Base、Doc、Drive 相关权限。

检查本地环境：

```bash
python3 scripts/paper_lark_cli.py check
lark-cli --version
```

## 使用

推荐流程：

1. 初始化飞书论文知识库。
2. 读取本地论文 PDF，生成中文精读笔记。
3. 围绕论文继续追问，并按需修订笔记。
4. 确认笔记内容后，上传论文笔记、PDF 和索引记录。
5. 论文积累后，更新用户画像。

使用示例：

```text
初始化一个飞书论文知识库，名字叫“论文仓库”。
```

```text
精读 ./papers/example.pdf，并生成中文论文笔记。
```

```text
这篇论文的方法和普通 RAG 的区别是什么？实验里最关键的对比是哪一组？
```

```text
把刚才关于方法差异和实验结论的讨论写回这篇论文笔记。
```

```text
把这篇论文笔记和 PDF 上传到飞书论文库。
```

```text
根据已归档论文和我的研究关键词，更新用户画像。
```

## 常用本地命令

这些命令用于本地检查、PDF 预处理、笔记校验和 skill 结构检查，不直接写入飞书。

```bash
# 检查 Python、PDF 抽取和 lark-cli 环境
python3 scripts/paper_lark_cli.py check

# 预处理论文 PDF，生成统一上下文
python3 scripts/paper_lark_cli.py paper-prep --pdf paper.pdf --output paper.context.json

# 校验论文笔记的元数据表
python3 scripts/paper_lark_cli.py note-check paper.paper-note.md

# 检查 skill 目录结构
python3 scripts/paper_lark_cli.py validate-tree .
```

## 文件树与功能

```text
paper-lark-reader/
├── SKILL.md                  # skill 入口
├── README.md                 # 使用说明
├── config/
│   └── defaults.json         # 本地配置
├── commands/
│   ├── kb-init.md            # 建库初始化
│   ├── paper-read.md         # 论文阅读
│   ├── paper-discuss.md      # 论文追问
│   ├── note-revise.md        # 笔记修订
│   ├── kb-upload.md          # 上传归档
│   └── profile-update.md     # 用户画像
├── references/
│   ├── command-pitfalls.md   # 命令注意事项
│   ├── lark-workflows.md     # 飞书流程
│   ├── note-writing-guide.md # 笔记规范
│   └── publication-policy.md # 出版核验
├── templates/
│   ├── paper-note.md         # 论文笔记模板
│   ├── research-profile.md   # 用户画像模板
│   └── upload-preview.md     # 上传预览模板
└── scripts/
    ├── paper_lark_cli.py     # 本地命令入口
    └── paper_lark/           # 本地处理模块
```

## 待办

- [x] 已跑通飞书论文知识库初始化与复用流程。
- [x] 已跑通论文阅读与本地笔记生成 / 更新流程。
- [x] 已跑通论文笔记与 PDF 上传归档 / 更新流程。
- [x] 已跑通用户画像生成 / 更新流程。
- [ ] 读论文的具体流程有待细化。
- [ ] 用户画像总结有待细化。
- [ ] 各种边界有待迭代。
