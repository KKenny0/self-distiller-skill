#!/usr/bin/env python3
"""微信聊天记录解析器 — 支持 CSV 和 SQLite 导出格式"""

import csv
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path


def parse_csv(filepath, sender_name=None):
    """解析微信 PC/Mac 导出的 CSV 格式"""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        return None

    messages = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sender = row.get("Sender", row.get("发送者", row.get("sender", "")))
            content = row.get("Content", row.get("内容", row.get("content", "")))
            ts = row.get("Time", row.get("时间", row.get("timestamp", "")))

            if not content or content in ("[图片]", "[语音]", "[视频]", "[文件]", "[表情包]"):
                continue
            if sender_name and sender != sender_name:
                continue

            messages.append({
                "author": sender,
                "content": content.strip(),
                "timestamp": ts,
            })

    return analyze(messages)


def parse_sqlite(filepath, sender_name=None, chat_name=None):
    """解析微信 iOS 备份的 SQLite 格式"""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        return None

    conn = sqlite3.connect(str(filepath))
    cursor = conn.cursor()

    # 尝试常见表名
    tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

    messages = []
    for table in tables:
        try:
            rows = cursor.execute(f"SELECT * FROM {table} LIMIT 10000").fetchall()
            if not rows:
                continue
            cols = [desc[0] for desc in cursor.description]

            for row in rows:
                row_dict = dict(zip(cols, row))
                content = row_dict.get("content", row_dict.get("Content", row_dict.get("message", "")))
                sender = row_dict.get("sender", row_dict.get("Sender", row_dict.get("who", "")))
                ts = str(row_dict.get("createTime", row_dict.get("timestamp", row_dict.get("time", ""))))

                if not content or len(content) < 2:
                    continue
                if sender_name and sender != sender_name:
                    continue

                messages.append({
                    "author": sender,
                    "content": str(content).strip(),
                    "timestamp": ts,
                })
        except Exception:
            continue

    conn.close()
    return analyze(messages)


def parse_txt(filepath, sender_name=None):
    """解析微信 Android 导出的纯文本格式"""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        return None

    # 常见格式: "2024-01-15 10:30:45 sender_name\n  message content"
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)\s+(.+?)\n\s*(.+)")

    messages = []
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    for match in pattern.finditer(text):
        ts, sender, content = match.group(1), match.group(2), match.group(3)
        if not content or content.startswith("["):
            continue
        if sender_name and sender != sender_name:
            continue
        messages.append({"author": sender, "content": content.strip(), "timestamp": ts})

    return analyze(messages)


def analyze(messages):
    if not messages:
        return {"messages": [], "analysis": {}}

    all_text = " ".join(m["content"] for m in messages)
    total = len(messages)
    cn_stopwords = set("的 了 是 在 我 有 和 就 不 人 都 一 个 上 也 很 到 说 要 去 你 会 着 没有 看 好 自己 这 他 她 它 们 那 里 为 什么 与 而 但 如果 因为 所以 虽然 可以 已经 还是 这个 那些 怎么 啊 吧 呢 吗 哦 嗯 哈 嘛 呀 被 把 让 从 对".split())

    freq = Counter()
    for w in all_text.split():
        if w not in cn_stopwords and len(w) > 1:
            freq[w] += 1

    return {
        "total_messages": total,
        "top_words": freq.most_common(30),
        "sample_messages": [m["content"][:200] for m in messages[-20:]],
        "time_range": f"{messages[0]['timestamp']} ~ {messages[-1]['timestamp']}" if messages else "",
    }


def parse(filepath, sender_name=None):
    filepath = Path(filepath)
    ext = filepath.suffix.lower()

    if ext == ".csv":
        return parse_csv(filepath, sender_name)
    elif ext in (".db", ".sqlite", ".sqlite3"):
        return parse_sqlite(filepath, sender_name)
    elif ext == ".txt":
        return parse_txt(filepath, sender_name)
    else:
        print(f"ERROR: Unsupported format: {ext}", file=sys.stderr)
        return None


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("file", help="WeChat export file (.csv, .db, .txt)")
    p.add_argument("--sender", help="Filter by sender name")
    args = p.parse_args()
    result = parse(args.file, args.sender)
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
