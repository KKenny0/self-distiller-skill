#!/usr/bin/env python3
"""Twitter/X 解析器 — 从推文/书签中提取说话风格"""

import json
import re
import sys
from collections import Counter
from pathlib import Path


def parse_json(filepath):
    """解析 Twitter JSON 导出（tweets.js, bookmarks.js 等）"""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        return None

    text = filepath.read_text(encoding="utf-8")
    # Twitter exports wrap JSON in variable assignment
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        print("ERROR: No JSON array found in file", file=sys.stderr)
        return None

    data = json.loads(match.group())
    tweets = []
    for item in data:
        tweet = item.get("tweet", item)
        full_text = tweet.get("full_text", tweet.get("text", ""))
        if not full_text or full_text.startswith("RT @"):
            continue
        tweets.append({
            "content": full_text,
            "timestamp": tweet.get("created_at", ""),
            "lang": tweet.get("lang", ""),
        })
    return analyze(tweets)


def parse_txt(filepath):
    """解析纯文本格式的推文列表"""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        return None

    tweets = []
    lines = filepath.read_text(encoding="utf-8").split("\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("http"):
            continue
        if len(line) > 280 or len(line) < 5:
            continue
        tweets.append({"content": line, "timestamp": "", "lang": ""})

    return analyze(tweets)


def analyze(tweets):
    if not tweets:
        return {"tweets": [], "analysis": {}}

    all_text = " ".join(t["content"] for t in tweets)
    total = len(tweets)

    en_stopwords = set("i me my we our you your he his she her it its they their this that the a an is are was were be been have has had do does did will would shall should can could may might must to of in for on with at by from as into about like through after over between out against during without before under around among and or but if then so than too very just also only".split())
    cn_stopwords = set("的 了 是 在 我 有 和 就 不 人 都 一 个 上 也 很 到 说 要 去 你 会 着 没有 看 好 自己 这 他 她 它 们 那 里 为 什么 与 而 但 如果 因为 所以 虽然 可以 已经 还是 这个 那些 怎么 啊 吧 呢 吗 哦 嗯 哈 嘛 呀 被 把 让 从 对".split())

    freq = Counter()
    for w in all_text.split():
        if w.lower() in en_stopwords or w in cn_stopwords:
            continue
        # 去掉 URL 和 @mention
        if w.startswith("http") or w.startswith("@"):
            continue
        freq[w] += 1

    # 推文长度分布
    lengths = [len(t["content"]) for t in tweets]
    avg_len = sum(lengths) / total if total else 0

    # 常用话题标签
    hashtags = re.findall(r"#(\w+)", all_text)
    tag_freq = Counter(hashtags).most_common(10)

    # 语言分布
    lang_dist = Counter(t["lang"] for t in tweets if t["lang"]).most_common(3)

    return {
        "total_tweets": total,
        "avg_tweet_length": round(avg_len, 1),
        "top_words": freq.most_common(30),
        "top_hashtags": tag_freq,
        "language_distribution": lang_dist,
        "sample_tweets": [t["content"] for t in tweets[-20:]],
    }


def parse(filepath):
    filepath = Path(filepath)
    ext = filepath.suffix.lower()
    if ext == ".json" or filepath.name.endswith(".js"):
        return parse_json(filepath)
    elif ext == ".txt":
        return parse_txt(filepath)
    else:
        print(f"ERROR: Unsupported format: {ext}", file=sys.stderr)
        return None


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("file", help="Twitter export file (.json, .js, .txt)")
    args = p.parse_args()
    result = parse(args.file)
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
