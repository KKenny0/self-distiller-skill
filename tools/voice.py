#!/usr/bin/env python3
"""
ListenHub Voice API 封装

官方文档：https://listenhub.ai/docs/en/openapi
API Base: https://api.marswave.ai/openapi/v1

功能：
  list    — 列出可用声音（含克隆声音）
  speak   — 文本转语音（OpenAI 兼容接口）
  test    — 用指定声音生成测试语音

注意：
  声音克隆在 ListenHub 网页端完成（https://listenhub.ai/app/voice-cloning），
  克隆完成后声音会自动出现在 list 结果中，可直接通过 speakerId 使用。
"""

import argparse
import json
import os
import sys
import requests

BASE_URL = os.environ.get("LISTENHUB_BASE_URL", "https://api.marswave.ai/openapi/v1")
API_KEY = os.environ.get("LISTENHUB_API_KEY", "")


def _headers():
    """构建 API 请求头。"""
    if not API_KEY:
        print("ERROR: LISTENHUB_API_KEY not set.", file=sys.stderr)
        return None
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def list_voices(language=None, gender=None, keyword=None):
    """列出可用声音（含用户在网页端克隆的声音）。

    API: GET /v1/speakers
    文档: https://listenhub.ai/docs/en/openapi/api-reference/speakers
    """
    headers = _headers()
    if not headers:
        return None

    url = f"{BASE_URL}/v1/speakers"

    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out.", file=sys.stderr)
        return None
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to {BASE_URL}.", file=sys.stderr)
        return None

    if resp.status_code != 200:
        print(f"ERROR: List voices failed ({resp.status_code}): {resp.text[:500]}", file=sys.stderr)
        return None

    try:
        data = resp.json()
    except ValueError:
        print(f"ERROR: Invalid JSON response.", file=sys.stderr)
        return None

    # 解析响应 — 格式: {"code": 0, "data": {"items": [...]}}
    items = []
    if isinstance(data, dict):
        inner = data.get("data", {})
        if isinstance(inner, dict):
            items = inner.get("items", [])
        elif isinstance(inner, list):
            items = inner
    elif isinstance(data, list):
        items = data

    # 客户端过滤
    filtered = items
    if language:
        filtered = [v for v in filtered if language.lower() in v.get("language", "").lower()]
    if gender:
        filtered = [v for v in filtered if gender.lower() in v.get("gender", "").lower()]
    if keyword:
        kw = keyword.lower()
        filtered = [
            v for v in filtered
            if kw in v.get("name", "").lower()
            or kw in json.dumps(v.get("profile", {}), ensure_ascii=False).lower()
        ]

    # 输出
    if not filtered:
        print(f"No voices found. (Total available: {len(items)})", file=sys.stderr)
        return {"total": len(items), "filtered": 0, "items": []}

    print(f"Available voices: {len(filtered)} (total: {len(items)})\n")
    for v in filtered:
        name = v.get("name", "?")
        sid = v.get("speakerId", "?")
        g = v.get("gender", "?")
        lang = v.get("language", "?")
        demo = v.get("demoAudioUrl", "")
        profile = v.get("profile", {})
        traits = ", ".join(profile.get("traits", []))
        accent = profile.get("accent", "")
        print(f"  {name}  ({sid})")
        print(f"    Gender: {g} | Language: {lang} | Accent: {accent}")
        if traits:
            print(f"    Traits: {traits}")
        if demo:
            print(f"    Demo: {demo}")
        print()

    return {"total": len(items), "filtered": len(filtered), "items": filtered}


def speak(text, speaker_id, language="zh", speed=1.0, output_path=None, model="flowtts"):
    """文本转语音（OpenAI 兼容接口）。

    API: POST /audio/speech
    文档: https://listenhub.ai/docs/en/openapi/openclaw/tts

    返回: 成功时返回文件路径或 True，失败返回 None。
    """
    if not API_KEY:
        print("ERROR: LISTENHUB_API_KEY not set.", file=sys.stderr)
        return None
    if not text or not text.strip():
        print("ERROR: Text cannot be empty.", file=sys.stderr)
        return None
    if not speaker_id:
        print("ERROR: speaker_id is required.", file=sys.stderr)
        return None

    url = f"{BASE_URL}/audio/speech"
    payload = {
        "input": text,
        "voice": speaker_id,
        "model": model,
        "response_format": "mp3",
    }

    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=120,
        )
    except requests.exceptions.Timeout:
        print("ERROR: TTS request timed out (120s).", file=sys.stderr)
        return None
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to {BASE_URL}.", file=sys.stderr)
        return None

    if resp.status_code != 200:
        print(f"ERROR: TTS failed ({resp.status_code}): {resp.text[:500]}", file=sys.stderr)
        return None

    # OpenAI 兼容接口直接返回音频二进制流
    content_type = resp.headers.get("Content-Type", "")
    if "audio" in content_type or "octet-stream" in content_type:
        if output_path:
            with open(output_path, "wb") as f:
                f.write(resp.content)
            print(f"✅ Audio saved to: {output_path}")
            return output_path
        else:
            # 保存到默认路径
            default_path = os.path.join(
                os.path.expanduser("~/Downloads"),
                f"self-distiller-{os.urandom(4).hex()}.mp3",
            )
            with open(default_path, "wb") as f:
                f.write(resp.content)
            print(f"✅ Audio saved to: {default_path}")
            return default_path

    # 如果返回的是 JSON（可能是错误或异步任务）
    try:
        result = resp.json()
        print(f"INFO: Unexpected JSON response: {json.dumps(result, ensure_ascii=False)[:500]}", file=sys.stderr)
        return result
    except ValueError:
        print(f"ERROR: Unknown response type: {content_type}", file=sys.stderr)
        return None


def test_voice(speaker_id, language="zh", output_path=None):
    """用指定声音生成测试语音。"""
    test_texts = {
        "zh": "你好，这是你的声音。听起来自然的话，说明配置正确。新的一天开始了，准备好了吗？",
        "en": "Hello, this is your voice. If it sounds natural, the setup is correct.",
    }
    text = test_texts.get(language, test_texts["en"])
    return speak(text, speaker_id, language=language, output_path=output_path)


def main():
    parser = argparse.ArgumentParser(
        description="ListenHub Voice API — speak, list, test",
        epilog="Voice cloning is done on https://listenhub.ai/app/voice-cloning — "
               "cloned voices appear automatically in the voice list.",
    )
    sub = parser.add_subparsers(dest="action")

    # speak
    p_speak = sub.add_parser("speak", help="Text to speech")
    p_speak.add_argument("--text", required=True, help="Text to speak")
    p_speak.add_argument("--speaker-id", required=True, help="Speaker ID (from list)")
    p_speak.add_argument("--language", default="zh")
    p_speak.add_argument("--speed", type=float, default=1.0)
    p_speak.add_argument("--model", default="flowtts", help="TTS model (default: flowtts)")
    p_speak.add_argument("--output", help="Save audio to file path")

    # test
    p_test = sub.add_parser("test", help="Generate a test sample")
    p_test.add_argument("--speaker-id", required=True, help="Speaker ID")
    p_test.add_argument("--language", default="zh")
    p_test.add_argument("--output", help="Save to file path")

    # list
    p_list = sub.add_parser("list", help="List available voices (including cloned)")
    p_list.add_argument("--language", help="Filter by language (e.g. zh, en)")
    p_list.add_argument("--gender", help="Filter by gender (male/female)")
    p_list.add_argument("--keyword", help="Filter by keyword in name or traits")

    args = parser.parse_args()

    if args.action == "speak":
        speak(args.text, args.speaker_id, args.language, args.speed, args.output, args.model)
    elif args.action == "test":
        test_voice(args.speaker_id, args.language, args.output)
    elif args.action == "list":
        list_voices(args.language, args.gender, args.keyword)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
