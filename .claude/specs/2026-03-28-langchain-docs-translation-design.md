# LangChain 文档中文化方案

## 概述

将 langchain-docs 仓库中的英文文档翻译为中文，通过独立域名部署中文版本。翻译触发为半自动模式（上游同步自动执行，翻译由人工手动触发）。

## 核心架构

```
atlasman/langchain-docs
│
├── main (上游镜像分支)
│   └── 与 upstream/main 保持同步，不做自主修改
│
├── zh_CN (翻译主分支，中文文档主分支)
│   ├── src/zh/              ← 中文文档输出目录
│   │   ├── docs.json        ← 中文导航配置（独立配置）
│   │   ├── GLOSSARY.md      ← 术语表（动态读取）
│   │   ├── concepts/        ← 概念文档
│   │   ├── langchain/       ← LangChain 文档
│   │   ├── langgraph/       ← LangGraph 文档
│   │   ├── javascript/      ← JavaScript 文档
│   │   ├── python/          ← Python 文档
│   │   └── integrations/    ← 集成文档
│   └── ❌ 不与上游同步
│
└── feat/translate-xxx (临时翻译分支)
    └── PR 合并后自动删除
```

**部署方式：** `zh_CN` 分支通过 Vercel/Netlify 独立部署，绑定独立域名。

## 分支策略

| 分支 | 用途 | 同步上游 | 自主修改 |
|------|------|----------|----------|
| `main` | 上游镜像 | ✅ 自动同步 | ❌ |
| `zh_CN` | 中文文档主分支 | ❌ | ✅ |
| `feat/translate-*` | 翻译任务分支 | 基于 main | ✅ |

## GitHub Actions 工作流

### 1. sync-upstream.yml — 上游同步

**触发条件：**
- `schedule`: 每天 3 AM UTC
- `workflow_dispatch`: 手动触发

**执行步骤：**
1. 添加 upstream remote（如果不存在）
2. Fetch upstream
3. Merge `upstream/main` → `main`（ff-only，失败则退出）
4. 检测 `src/oss/` 下的变更文件（相对于上一次同步的 commit）
5. 无变更 → 结束
6. 有变更 → 创建 GitHub Issue，说明变更内容，通知相关人员

**变更检测逻辑：**
```bash
LAST_SYNC=$(git log --oneline -1 --format="%H" origin/main~10..origin/main | tail -1)
CHANGED=$(git diff --name-only $LAST_SYNC..HEAD -- src/oss/ 2>/dev/null || echo "")
```

### 2. translate.yml — 翻译任务

**触发条件：**
- `workflow_dispatch`: 手动触发（带输入参数）

**输入参数：**
- `files`: 要翻译的文件列表（逗号分隔），可选
- `all`: 是否翻译全部未翻译文件，布尔值

**执行步骤：**
1. 基于 `main` 创建 `feat/translate-{timestamp}` 分支
2. 运行 `translate.py`
3. 如果有翻译产物 → 创建 PR 到 `zh_CN`
4. 如果无产物 → 结束

**环境变量（GitHub Secrets）：**
| 变量 | 说明 |
|------|------|
| `ANTHROPIC_BASE_URL` | API 端点（如 `https://api.anthropic.com`） |
| `ANTHROPIC_MODEL` | 模型名称（如 `claude-opus-4-6`） |
| `ANTHROPIC_API_KEY` | API Key |
| `ANTHROPIC_AUTH_TOKEN` | 替代认证 Token（二选一） |

## translate.py — 翻译脚本

### 文件路径

```
.github/scripts/translate.py
```

### 核心功能

1. **动态读取术语表**：启动时读取 `src/zh/GLOSSARY.md`，解析术语映射
2. **灵活认证**：支持 `base_url`、`model`、`api_key`、`auth_token`
3. **批量翻译**：支持单文件、文件列表、全部未翻译文件
4. **路径映射**：`src/oss/{path}/*.mdx` → `src/zh/{path}/*.mdx`

### SYSTEM_PROMPT — 优化版

```text
You are a professional technical translator specializing in AI/LLM documentation.
Translate Mintlify markdown to Simplified Chinese while preserving all technical precision.

## 保留不翻译的内容（精确列表）

### MDX 组件（原文保留）
<Card>, <CardGroup>, <Tabs>, <Tab>, <Steps>, <Step>,
<Accordion>, <AccordionGroup>, <Note>, <Tip>, <Warning>, <Info>,
<CodeGroup>, <Snippet>, <Images>, <Callout>

### 代码相关（原文保留）
- 所有代码块内容（```内的代码）
- 代码内的注释（如 # [!code highlight]）
- 文件路径（src/oss/..., src/zh/...）
- 环境变量名（$ANTHROPIC_API_KEY 等）
- 命令行命令（python translate.py 等）

### 引用和链接（原文保留）
- @[ClassName] 类型的 API 引用链接
- 外部 URL（https://..., http://...）
- Mintlify 组件属性名（icon=, href=, label= 等）

### 特殊语法
- :::python, :::js 等语言标签（保留 :::python ... ::: 整个块）
- --- 在 frontmatter 中（YAML 分隔符）
- # [!code flags]（代码高亮指令）

## 需要翻译的内容

- MDX 文件中的正文文本（中英文混合时，保留英文技术术语）
- Markdown 标题（h1-h4）
- 表格中的描述性文本
- frontmatter 中的 title 和 description
- 链接的内联文本（如 [some text](url) 中的 some text）

## 格式规则

- 标点符号：使用中文标点（，。：；？！""）
- 括号：使用中文括号（（））替代英文括号
- 引号：使用中文引号（「」）
- 代码内联：使用 `code`（反引号）
- 专有名词：首次出现时在中文后加括号标注英文

## 术语翻译标准

优先使用以下标准翻译，术语表见 GLOSSARY.md：

- Chain → 链
- Agent → 智能体
- Prompt → 提示词
- RAG → RAG（检索增强生成）
- Vector Store → 向量数据库
- Tool → 工具
- Memory → 记忆
- LLM → LLM（大型语言模型）
- Hallucination → 幻觉
- Embedding → 嵌入
- Token → Token（标记）
- Prompt Template → 提示词模板
- Output Parser → 输出解析器
- Retrieval → 检索

## 输出格式

只输出翻译后的完整文件内容，不要输出解释、备注或格式说明。
```

### 关键设计决策

1. **术语表动态读取**：每次运行时从 `src/zh/GLOSSARY.md` 读取术语映射，追加到 SYSTEM_PROMPT 末尾
2. **MDX 组件白名单**：明确列出保留的组件，避免遗漏
3. **代码块完整保留**：通过 `:::language` 语言标签整块保留，不拆开翻译
4. **frontmatter 单独处理**：解析 YAML frontmatter，title 和 description 翻译，其余保留

## 目录结构初始化

首次初始化时需创建：

```
src/zh/
├── docs.json              ← 独立的中文导航配置
├── GLOSSARY.md            ← 术语表
├── concepts/
├── langchain/
├── langgraph/
├── javascript/
├── python/
└── integrations/
```

### docs.json 配置策略

Mintlify 不支持多语言内置，方案：

1. `src/docs.json` → 英文文档导航（与上游同步）
2. `src/zh/docs.json` → 中文文档导航（独立维护）

**注意：** 两个 `docs.json` 完全独立，需要分别维护导航结构。

### GLOSSARY.md 格式

```md
# 术语表

本文档使用的标准术语翻译。

## 格式

每行：`英文 | 中文 | 备注（可选）`

## 术语

Chain | 链 | --
Agent | 智能体 | 或保留 "Agent"
Prompt | 提示词 | --
RAG | RAG | 检索增强生成，首次出现时注
...
```

## 翻译优先级

| 优先级 | 目录 | 原因 |
|--------|------|------|
| P0 | `src/oss/concepts/` | 基础概念，所有文档的基础 |
| P1 | `src/oss/langchain/` | 最大用户群体 |
| P1 | `src/oss/langgraph/` | 核心产品 |
| P2 | `src/oss/integrations/` | 按需，热门集成优先 |
| P3 | 其他 | 低频参考 |

## 验证清单

| 验证项 | 操作 |
|--------|------|
| 本地预览 | `npx mintlify dev` |
| 构建检查 | `npx mintlify build` |
| 上游同步状态 | `git log origin/main` |
| 翻译进度 | `ls src/zh/concepts/` |
| 翻译 PR | `gh pr list --state open` |
| 变更检测 | `git diff --name-only <last_sync>..HEAD -- src/oss/` |

## 与原计划的关键差异

| 项目 | 原计划 | 本方案 |
|------|--------|--------|
| 翻译触发 | 全自动 | 半自动（手动触发翻译） |
| 变更通知 | 无 | GitHub Issue |
| PR 创建时机 | 上游同步时自动创建翻译 PR | 上游同步只通知，翻译后创建 PR |
| 认证参数 | 仅 API_KEY | 支持 base_url / model / api_key / auth_token |
| 术语表 | 硬编码 | 动态读取 GLOSSARY.md |
| GitHub Actions | 仅 sync-upstream | 新增 translate.yml |
| 中文配置 | 未提及 | 独立 zh/docs.json |
