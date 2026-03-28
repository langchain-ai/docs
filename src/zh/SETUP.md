# 中文文档翻译系统 - 设置指南

## 分支状态

| 分支 | 用途 | 状态 |
|------|------|------|
| `main` | 上游镜像 | ✅ 已配置 |
| `zh_CN` | 中文文档主分支 | ✅ 已初始化 |
| `feat/translation-system-design` | 设计文档 | ✅ 已推送 |

## GitHub Secrets 配置（必须）

GitHub Actions 工作流需要以下 Secrets，请在 GitHub 仓库 **Settings → Secrets and variables → Actions** 中添加：

### 必需

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API Key | `sk-ant-...` |

### 可选（根据你的 API 端点选择）

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `ANTHROPIC_BASE_URL` | API 端点（使用第三方服务时） | `https://api.openrouter.ai/v1` |
| `ANTHROPIC_MODEL` | 模型名称 | `claude-opus-4-6` |
| `ANTHROPIC_AUTH_TOKEN` | 替代认证 Token | 与 API_KEY 二选一 |

### 配置示例

**方式 1：使用 Anthropic 官方 API**
```
ANTHROPIC_API_KEY = sk-ant-api03-...
```

**方式 2：使用 OpenRouter（第三方代理）**
```
ANTHROPIC_BASE_URL = https://openrouter.ai/api/v1
ANTHROPIC_API_KEY = sk-or-v1-...
ANTHROPIC_MODEL = anthropic/claude-3.5-sonnet
```

**方式 3：使用 Azure AI Studio**
```
ANTHROPIC_BASE_URL = https://your-resource.cognitiveservices.azure.com/v1
ANTHROPIC_API_KEY = your-api-key
ANTHROPIC_MODEL = claude-3-5-sonnet
```

## 工作流说明

### 1. 上游同步（自动）

**触发：** 每天 3 AM UTC + 手动触发

**流程：**
1. 同步 `upstream/main` → `main`
2. 检测 `src/oss/` 变更文件
3. 有变更 → 创建 GitHub Issue 通知

### 2. 翻译任务（手动）

**触发：** GitHub Actions → Translate Docs → Run workflow

**输入：**
- `files`: 要翻译的文件（留空则翻译全部未翻译文件）
- `dry_run`: 是否仅显示待翻译文件

**流程：**
1. 基于 `main` 创建 `feat/translate-{timestamp}` 分支
2. 调用 Claude API 翻译文件
3. 创建 PR 到 `zh_CN`

## 本地开发

### 初始化中文目录结构

```bash
bash .github/scripts/init-zh-structure.sh
```

### 测试翻译脚本

```bash
# 仅显示待翻译文件（不调用 API）
python .github/scripts/translate.py --all --dry-run

# 翻译指定文件
python .github/scripts/translate.py --files "src/oss/concepts/chat-models.mdx"

# 翻译全部未翻译文件
python .github/scripts/translate.py --all

# 测试术语表输出
python .github/scripts/translate.py --glossary-only
```

### 本地预览文档

```bash
npm install
npx mintlify dev
```

## 目录结构

```
src/
├── zh/                      # 中文文档（部署时使用）
│   ├── docs.json           # 中文导航配置
│   ├── GLOSSARY.md         # 术语表
│   ├── concepts/           # 概念文档
│   ├── langchain/          # LangChain 文档
│   ├── langgraph/          # LangGraph 文档
│   └── ...
└── oss/                    # 英文原文（上游同步）
    ├── concepts/
    ├── langchain/
    └── ...
```

## 翻译流程

```
上游更新 → sync-upstream.yml 自动运行 → GitHub Issue 通知
    ↓
你决定翻译 → 手动触发 translate.yml → 创建翻译 PR
    ↓
Review PR → 合并到 zh_CN → 自动部署
```

## 部署

`zh_CN` 分支配置 Vercel/Netlify：

- **Build Command:** `npm install && npx mintlify build`
- **Output Directory:** `build`
- **Root Directory:** `/`（使用 `src/zh/docs.json`）

注意：需要修改 Mintlify 配置指向中文配置，或使用环境变量 `MINTLIFY_CONFIG=src/zh/docs.json`
