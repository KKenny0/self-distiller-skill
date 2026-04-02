#!/usr/bin/env python3
"""ListenHub Voice API 封装 — 语音克隆 + TTS"""

import argparse
import json
import os
import sys
import requests

BASE_URL = os.environ.get("LISTENHUB_BASE_URL", "https://api.listenhub.ai")
API_KEY = os.environ.get("LISTENHUB_API_KEY", "")


def _headers():
    if not API_KEY:
        print("ERROR: LISTENHUB_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def clone(name, files, language="zh"):
    """克隆语音。files 是音频文件路径列表。"""
    if not API_KEY:
        print("ERROR: LISTENHUB_API_KEY not set. Set it via environment variable.", file=sys.stderr)
        return None

    # 校验文件存在
    for f in files:
        if not os.path.exists(f):
            print(f"ERROR: Audio file not found: {f}", file=sys.stderr)
            return None

    print(f"Cloning voice: {name} ({len(files)} files, language={language})")

    url = f"{BASE_URL}/v1/voices/clone"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        files_payload = []
        for f in files:
            files_payload.append(("files", (os.path.basename(f), open(f, "rb"))))
        data = {"name": name, "language": language}

        resp = requests.post(url, headers=headers, files=files_payload, data=data, timeout=120)
    except requests.exceptions.Timeout:
        print("ERROR: Clone request timed out (120s). Audio files may be too large.", file=sys.stderr)
        return None
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to {BASE_URL}. Check network or API URL.", file=sys.stderr)
        return None
    finally:
        for _, (_, fh) in files_payload:
            fh.close()

    if resp.status_code == 401:
        print("ERROR: API key invalid or expired. Check LISTENHUB_API_KEY.", file=sys.stderr)
        return None
    elif resp.status_code == 429:
        print("ERROR: Rate limited. Wait and try again.", file=sys.stderr)
        return None
    elif resp.status_code != 200:
        print(f"ERROR: Clone failed ({resp.status_code}): {resp.text[:500]}", file=sys.stderr)
        return None

    try:
        result = resp.json()
    except ValueError:
        print(f"ERROR: Invalid JSON response: {resp.text[:500]}", file=sys.stderr)
        return None

    # 兼容多种可能的响应字段名
    speaker_id = (
        result.get("speakerId")
        or result.get("id")
        or result.get("voice_id")
        or result.get("voiceId")
    )
    if not speaker_id:
        print(f"WARNING: No speaker_id found in response. Full response:", file=sys.stderr)
        print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
        return None

    print(f"✅ Voice cloned. speaker_id: {speaker_id}")
    return speaker_id


def speak(text, speaker_id, language="zh", speed=1.0, output_path=None):
    """生成语音。返回音频 URL 或保存到文件。"""
    if not API_KEY:
        print("ERROR: LISTENHUB_API_KEY not set.", file=sys.stderr)
        return None
    if not text or not text.strip():
        print("ERROR: Text cannot be empty.", file=sys.stderr)
        return None
    if not speaker_id:
        print("ERROR: speaker_id is required.", file=sys.stderr)
        return None

    # 文本过长时自动分段
    if len(text) > 500:
        print(f"WARNING: Text is {len(text)} chars. Consider splitting for better quality.")

    url = f"{BASE_URL}/v1/tts"
    payload = {
        "text": text,
        "speakerId": speaker_id,
        "language": language,
        "speed": speed,
    }

    try:
        resp = requests.post(url, headers=_headers(), json=payload, timeout=120)
    except requests.exceptions.Timeout:
        print("ERROR: TTS request timed out.", file=sys.stderr)
        return None
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to {BASE_URL}.", file=sys.stderr)
        return None

    if resp.status_code != 200:
        print(f"ERROR: TTS failed ({resp.status_code}): {resp.text[:500]}", file=sys.stderr)
        return None

    try:
        result = resp.json()
    except ValueError:
        print(f"ERROR: Invalid JSON response: {resp.text[:500]}", file=sys.stderr)
        return None

    # 兼容多种响应格式
    audio_url = (
        result.get("url")
        or result.get("audioUrl")
        or result.get("audio_url")
        or result.get("downloadUrl")
    )
    listen_url = result.get("listenUrl") or result.get("listen_url")

    if output_path and audio_url:
        try:
            audio_data = requests.get(audio_url, timeout=60).content
            with open(output_path, "wb") as f:
                f.write(audio_data)
            print(f"✅ Audio saved to: {output_path}")
        except Exception as e:
            print(f"ERROR: Failed to download audio: {e}", file=sys.stderr)
            return None
    else:
        print(f"✅ Audio generated.")
        if listen_url:
            print(f"Listen: {listen_url}")
        if audio_url:
            print(f"Download: {audio_url}")

    return result


def list_voices():
    """列出已克隆的语音。"""
    url = f"{BASE_URL}/v1/voices"
    resp = requests.get(url, headers=_headers(), timeout=30)
    if resp.status_code != 200:
        print(f"ERROR: List voices failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


def test_voice(speaker_id, language="zh"):
    """生成测试语音。"""
    test_texts = {
        "zh": "你好，我是你的克隆声音。如果听起来自然，说明克隆成功。现在时间是清晨，让我们开始新的一天。",
        "en": "Hello, this is your cloned voice. If it sounds natural, the clone was successful.",
    }
    text = test_texts.get(language, test_texts["en"])
    return speak(text, speaker_id, language=language)


def main():
    parser = argparse.ArgumentParser(description="ListenHub Voice API")
    sub = parser.add_subparsers(dest="action")

    # clone
    p_clone = sub.add_parser("clone", help="Clone a voice")
    p_clone.add_argument("--name", required=True, help="Voice name/slug")
    p_clone.add_argument("--files", nargs="+", required=True, help="Audio sample files")
    p_clone.add_argument("--language", default="zh", help="Language (zh/en)")

    # speak
    p_speak = sub.add_parser("speak", help="Generate speech")
    p_speak.add_argument("--text", required=True, help="Text to speak")
    p_speak.add_argument("--speaker-id", required=True, help="Cloned speaker ID")
    p_speak.add_argument("--language", default="zh")
    p_speak.add_argument("--speed", type=float, default=1.0)
    p_speak.add_argument("--output", help="Save audio to file")

    # test
    p_test = sub.add_parser("test", help="Test a cloned voice")
    p_test.add_argument("--speaker-id", required=True, help="Cloned speaker ID")
    p_test.add_argument("--language", default="zh")

    # list
    sub.add_parser("list", help="List cloned voices")

    args = parser.parse_args()

    if args.action == "clone":
        clone(args.name, args.files, args.language)
    elif args.action == "speak":
        speak(args.text, args.speaker_id, args.language, args.speed, args.output)
    elif args.action == "test":
        test_voice(args.speaker_id, args.language)
    elif args.action == "list":
        list_voices()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
