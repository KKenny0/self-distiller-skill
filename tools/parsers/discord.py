#!/usr/bin/env python3
"""Discord 聊天记录解析器 — 提取说话风格和内容"""

import json
import sys
from collections import Counter
from pathlib import Path


def parse(filepath, user_id=None, username=None):
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages = []
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        if "messages" in data:
            raw = data["messages"]
        elif "channels" in data:
            raw = []
            for ch in data["channels"]:
                if isinstance(ch, dict) and "messages" in ch:
                    raw.extend(ch["messages"])
        else:
            raw = [data]
    else:
        print("ERROR: Unexpected format", file=sys.stderr)
        return None

    for msg in raw:
        author_id = msg.get("author", {}).get("id", "")
        author_name = msg.get("author", {}).get("username", "")
        content = msg.get("content", "").strip()
        ts = msg.get("timestamp", "")
        if not content:
            continue
        if user_id and author_id != user_id:
            continue
        if username and author_name != username:
            continue
        messages.append({
            "author_id": author_id,
            "author_name": author_name,
            "content": content,
            "timestamp": ts,
        })

    return analyze(messages)


def analyze(messages):
    if not messages:
        return {"messages": [], "analysis": {}}

    all_text = " ".join(m["content"] for m in messages)
    words = [w for w in all_text.split() if len(w) > 1]
    total = len(messages)
    avg_len = len(words) / total if total else 0

    # 高频词
    cn_stopwords = set("的 了 是 在 我 有 和 就 不 人 都 一 个 上 也 很 到 说 要 去 你 会 着 没有 看 好 自己 这 他 她 它 们 那 里 为 什么 与 而 但 如果 因为 所以 虽然 可以 已经 还是 这个 那些 怎么 啊 吧 呢 吗 哦 嗯 哈 嘛 呀 被 把 让 从 对".split())
    en_stopwords = set("i me my we our you your he his she her it its they their this that the a an is are was were be been have has had do does did will would shall should can could may might must to of in for on with at by from as into about like through after over between out against during without before under around among".split())

    freq = Counter()
    for w in words:
        if w in cn_stopwords or w.lower() in en_stopwords:
            continue
        freq[w] += 1

    # 句式特征
    sentences = all_text.replace("\n", " ").split("。") + all_text.split(".") + all_text.split("！") + all_text.split("!") + all_text.split("？") + all_text.split("?")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    short_pct = sum(1 for s in sentences if len(s) <= 20) / len(sentences) * 100 if sentences else 0
    has_emoji = sum(1 for m in messages if any(c in m["content"] for c in "😂🤣💀👍❤️🔥✨💡🤔😤😅👏🙏💪😎")) / total * 100

    # 时间分布
    hours = [int(m["timestamp"].split("T")[1][:2]) if "T" in m["timestamp"] else 0 for m in messages if m["timestamp"]]

    return {
        "total_messages": total,
        "avg_message_length": round(avg_len, 1),
        "top_words": freq.most_common(30),
        "short_sentence_pct": round(short_pct, 1),
        "emoji_usage_pct": round(has_emoji, 1),
        "sample_messages": [m["content"][:200] for m in messages[-20:]],
        "active_hours": Counter(hours).most_common(5) if hours else [],
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("file", help="Discord JSON export file")
    p.add_argument("--user-id")
    p.add_argument("--username")
    args = p.parse_args()
    result = parse(args.file, args.user_id, args.username)
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
