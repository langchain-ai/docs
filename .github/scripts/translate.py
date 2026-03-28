#!/usr/bin/env python3
"""
translate.py — LangChain 文档翻译脚本

用法:
    python translate.py --files "src/oss/concepts/chat-models.mdx,src/oss/concepts/prompts.mdx"
    python translate.py --all
    python translate.py --glossary-only  # 仅输出术语表内容用于测试

环境变量:
    ANTHROPIC_BASE_URL   API 端点（支持第三方兼容服务）
    ANTHROPIC_MODEL      模型名称，默认 claude-opus-4-6
    ANTHROPIC_API_KEY    API Key
    ANTHROPIC_AUTH_TOKEN 替代认证 Token（二选一）
"""

import os
import sys
import argparse
import re
import json
from pathlib import Path
from typing import Optional


def get_client() -> "Anthropic":
    """创建 Anthropic 客户端，支持灵活认证."""
    from anthropic import Anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6")
    if not api_key:
        raise ValueError(
            "请设置 ANTHROPIC_API_KEY 或 ANTHROPIC_AUTH_TOKEN 环境变量"
        )
    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return Anthropic(**kwargs), model


def read_glossary(glossary_path: Path) -> str:
    """读取并解析 GLOSSARY.md，生成术语映射文本."""
    if not glossary_path.exists():
        return ""
    content = glossary_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    terms = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("##"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2 and parts[0] and parts[1]:
            english, chinese = parts[0], parts[1]
            note = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
            if note:
                terms.append(f"- {english} → {chinese}（{note}）")
            else:
                terms.append(f"- {english} → {chinese}")
    if not terms:
        return ""
    return "\n".join(terms)


def build_system_prompt(glossary_path: Path) -> str:
    """构建完整的 SYSTEM PROMPT."""
    glossary_terms = read_glossary(glossary_path)
    prompt_parts = [
        "You are a professional technical translator specializing in AI/LLM documentation. "
        "Translate Mintlify markdown to Simplified Chinese while preserving all technical precision.",
        "",
        "## 保留不翻译的内容（精确列表）",
        "",
        "### MDX 组件（原文原样保留）",
        "<Card>, <CardGroup>, <Tabs>, <Tab>, <Steps>, <Step>, "
        "<Accordion>, <AccordionGroup>, <Note>, <Tip>, <Warning>, <Info>, "
        "<Callout>, <CodeGroup>, <Snippet>, <Images>",
        "",
        "### frontmatter（原文保留，仅翻译 title 和 description）",
        "保留所有 YAML frontmatter 分隔符 ---，保留除 title/description 以外的所有字段",
        "",
        "### 代码块（原文完整保留，不拆开翻译）",
        "- 所有 ```...``` 代码块内容",
        "- 语言标签 :::python, :::js, :::bash 等",
        "- 代码内注释 # [!code highlight], # [!code ++], # [!code --]",
        "- 内联代码 `code`",
        "",
        "### 引用和链接（原文保留）",
        "- @[ClassName] API 引用",
        "- 外部 URL https://..., http://...",
        "- Mintlify 组件属性 icon=, href=, label= 等",
        "",
        "### 特殊语法",
        "- --- 在 frontmatter 中作为 YAML 分隔符",
        "- # [!code flags] 代码高亮指令",
        "- 链接中的 URL 保持不变",
        "",
        "## 需要翻译的内容",
        "",
        "- MDX 正文段落和句子",
        "- Markdown 标题（h1-h6）",
        "- 表格中的描述性单元格文本",
        "- frontmatter 中的 title 和 description 字段",
        "- 链接的内联文本（[some text](url) 中的 some text）",
        "- 图片 alt 文本",
        "",
        "## 格式规则",
        "",
        "- 标点：使用中文标点（，。：；？！""）",
        "- 括号：中文括号（（））替代英文半角括号",
        "- 引号：中文引号（「」）",
        "- 专有名词：首次出现时在中文后加括号标注英文，如 LLM（大型语言模型）",
        "",
        "## 术语翻译标准",
        "",
    ]
    if glossary_terms:
        prompt_parts.extend([
            "以下术语表为最高优先级：",
            glossary_terms,
            "",
            "未在术语表中的术语，参考以下标准：",
        ])
    else:
        prompt_parts.append("参考以下标准翻译：")
    prompt_parts.extend([
        "- Chain → 链",
        "- Agent → 智能体（首次出现时注）",
        "- Prompt → 提示词",
        "- RAG → RAG（检索增强生成，首次出现时注）",
        "- Vector Store → 向量数据库",
        "- Tool → 工具",
        "- Memory → 记忆",
        "- LLM → LLM（大型语言模型，首次出现时注）",
        "- Hallucination → 幻觉",
        "- Embedding → 嵌入",
        "- Token → Token（标记）",
        "- Prompt Template → 提示词模板",
        "- Output Parser → 输出解析器",
        "- Retrieval → 检索",
        "",
        "## 重要提醒",
        "",
        "1. 只输出翻译后的文件内容，不要输出任何解释、备注或前言",
        "2. 保持原文的章节结构、代码块、组件完整",
        "3. frontmatter 中 title 翻译为中文，description 翻译为中文（无 markdown 格式）",
        "4. 内部链接路径保持原样，不要添加 /zh/ 前缀",
    ])
    return "\n".join(prompt_parts)


def split_frontmatter(content: str) -> tuple[Optional[dict], str]:
    """解析 frontmatter，返回 (metadata_dict, body_content)."""
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content
    import yaml
    try:
        metadata = yaml.safe_load(parts[1])
        body = parts[2].strip()
    except yaml.YAMLError:
        return None, content
    return metadata, body


def translate_content(content: str, filename: str, client: "Anthropic", model: str) -> str:
    """调用 AI 翻译单文件内容."""
    response = client.messages.create(
        model=model,
        max_tokens=8192,
        system=(
            "You are a professional technical translator specializing in AI/LLM documentation. "
            "Translate Mintlify markdown to Simplified Chinese while preserving all technical precision. "
            "Only output the translated file content, no explanations or notes."
        ),
        messages=[{
            "role": "user",
            "content": f"Translate this documentation file to Simplified Chinese.\n\nFilename: {filename}\n\nContent:\n{content}\n\nTranslation:"
        }]
    )
    return response.content[0].text


def get_zh_path(src_path: Path) -> Path:
    """src/oss/concepts/chat-models.mdx -> src/zh/concepts/chat-models.mdx."""
    return Path(str(src_path).replace("/oss/", "/zh/", 1))


def translate_file(src_path: Path, glossary_path: Path, dry_run: bool = False) -> bool:
    """翻译单个文件."""
    zh_path = get_zh_path(src_path)
    zh_path.parent.mkdir(parents=True, exist_ok=True)

    content = src_path.read_text(encoding="utf-8")
    print(f"  翻译: {src_path} -> {zh_path}")

    if dry_run:
        print(f"  [dry-run] 跳过实际翻译")
        return True

    try:
        client, model = get_client()
        translated = translate_content(content, src_path.name, client, model)
        zh_path.write_text(translated, encoding="utf-8")
        print(f"  ✓ 完成")
        return True
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="LangChain 文档翻译脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python translate.py --files "src/oss/concepts/chat-models.mdx"
  python translate.py --files "f1.mdx,f2.mdx"
  python translate.py --all
  python translate.py --glossary-only
        """
    )
    parser.add_argument(
        "--files",
        help="逗号分隔的文件路径列表，如 src/oss/concepts/chat-models.mdx",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="翻译 src/oss/ 下所有尚未翻译的 .mdx 文件",
    )
    parser.add_argument(
        "--glossary-only",
        action="store_true",
        help="仅输出 SYSTEM PROMPT 中的术语表部分，用于测试",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅显示要翻译的文件，不实际调用 API",
    )
    parser.add_argument(
        "--src-dir",
        default="src",
        help="src 目录路径，默认 src",
    )
    args = parser.parse_args()

    glossary_path = Path(args.src_dir) / "zh" / "GLOSSARY.md"
    system_prompt = build_system_prompt(glossary_path)

    if args.glossary_only:
        print(system_prompt)
        return

    if args.files:
        files = [Path(p.strip()) for p in args.files.split(",")]
        for f in files:
            if f.exists():
                translate_file(f, glossary_path, args.dry_run)
            else:
                print(f"  ⚠ 文件不存在: {f}")
    elif args.all:
        src_dir = Path(args.src_dir)
        oss_dir = src_dir / "oss"
        count = 0
        for src_path in sorted(oss_dir.rglob("*.mdx")):
            zh_path = get_zh_path(src_path)
            if zh_path.exists():
                continue
            if translate_file(src_path, glossary_path, args.dry_run):
                count += 1
        print(f"\n共翻译 {count} 个文件")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
