#!/usr/bin/env python3
"""Persona 提炼引擎 — 从原始数据生成 SELF.md"""

import json
import sys
from pathlib import Path


def distill(sources, base_info, output_path="SELF.md"):
    """
    从多个数据源提炼 Persona。

    Args:
        sources: dict of {source_name: parsed_data}
        base_info: dict with name, description, personality
        output_path: output file path
    """
    slug = base_info.get("slug", "self")

    # 收集所有文本
    all_text = []
    sample_messages = []
    word_freq = {}

    for name, data in sources.items():
        if isinstance(data, str):
            all_text.append(data)
        elif isinstance(data, dict):
            if "sample_messages" in data:
                sample_messages.extend(data["sample_messages"][:20])
            if "top_words" in data:
                for word, count in data["top_words"]:
                    word_freq[word] = word_freq.get(word, 0) + count
            if "top_tweets" in data:
                sample_messages.extend(data["sample_tweets"][:10])

    # 排序高频词
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]

    # 生成 SELF.md
    lines = [
        f"# {slug} — Persona\n",
        "## 说话风格\n",
        f"- 常用语言：{base_info.get('language', '待分析')}",
        f"- 口头禅和高频表达：{', '.join(w for w, _ in sorted_words[:10])}",
        f"- 描述：{base_info.get('personality', '待分析')}\n",
        "## 思维模式\n",
        "- 待分析（需要更多交互数据）\n",
        "## 知识边界\n",
        f"- 描述：{base_info.get('description', '待分析')}\n",
        "## 情感模式\n",
        "- 待分析\n",
        "## 行为模式\n",
        "- 待分析\n",
        "## 原始材料摘要\n",
        f"- 数据源数量：{len(sources)}",
        f"- 样本消息数：{len(sample_messages)}",
    ]

    if sample_messages:
        lines.append("\n### 样本消息\n")
        for msg in sample_messages[:15]:
            lines.append(f"- {msg[:200]}")

    content = "\n".join(lines)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"✅ Persona written to {output}")
    return content


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--slug", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--personality", default="")
    p.add_argument("--output", default="SELF.md")
    p.add_argument("--sources", nargs="+", help="JSON files with parsed data")
    args = p.parse_args()

    sources = {}
    for f in (args.sources or []):
        fp = Path(f)
        if fp.exists():
            sources[fp.stem] = json.loads(fp.read_text(encoding="utf-8"))

    distill(sources, {
        "slug": args.slug,
        "description": args.description,
        "personality": args.personality,
    }, args.output)
