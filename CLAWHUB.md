# 🪞 self-distiller

**Version:** 1.0.0
**Author:** Kenny Wu
**License:** MIT
**Repository:** https://github.com/KKenny0/self-distiller-skill
**Runtime:** OpenClaw Agent
**Category:** Self-Improvement / Psychology

---

## Description

Distill yourself into an AI persona and talk to yourself in your own voice. Import chat history, notes, and social media to generate your Persona, then achieve deep self-reflection through daily mirror sessions and emotion observation.

### What Makes It Different

Unlike ex-skill (distill your ex) or colleague-skill (distill your coworker), self-distiller focuses on **self-reflection and personal growth** — with **voice cloning** as the core differentiator. Hearing your own thoughts spoken back to you in your own voice creates a powerful cognitive defusion effect based on ACT (Acceptance and Commitment Therapy) research.

### Core Scenes

- **🌅 Daily Mirror** — Morning self-dialogue with your Persona
- **🔥 Emotion Observer** — Cognitive defusion when you're emotionally charged
- **⚖️ Inner Debate** — Your impulsive self vs. rational self (v2)
- **📦 Time Capsule** — Write letters to past/future self (v2)

### Requirements

- OpenClaw runtime
- Python 3.9+ with `requests` package
- ListenHub API key (for voice features)
- Microphone or audio samples (for voice cloning)

### Install

```bash
# Option 1: Clone to OpenClaw workspace
cd ~/.openclaw/workspace/skills/
git clone https://github.com/KKenny0/self-distiller-skill.git self-distiller

# Option 2: Via ClawHub (coming soon)
openclaw skills install self-distiller
```

### Quick Start

1. Set your ListenHub API key:
   ```bash
   export LISTENHUB_API_KEY="your-key-here"
   ```

2. Start a distillation session:
   ```
   /create-self
   ```

3. Answer 3 questions (name, background, personality)

4. Import your data (OpenClaw memory, chat exports, or social media)

5. Upload voice samples (1-5 min of natural speech)

6. Start your first mirror session:
   ```
   /mirror
   ```

### Voice Providers

| Provider | Clone Support | Quality | Cost |
|----------|:------------:|:-------:|:----:|
| ListenHub (preset) | ❌ | ⭐⭐⭐⭐ | Free tier |
| ListenHub (cloned) | ✅ | ⭐⭐⭐⭐⭐ | Paid |
| ElevenLabs | ✅ | ⭐⭐⭐⭐⭐ | Paid |
| OpenAI TTS | ❌ | ⭐⭐⭐ | Pay-per-use |

### Safety

- **Personal growth only** — not for manipulation or impersonation
- **Local data storage** — Persona and conversation logs stay on your machine
- **Not a therapist** — suggests professional help when needed
- **Anti-addiction** — warns against over-dependence

### Tags

`self-reflection`, `voice-clone`, `cognitive-defusion`, `persona`, `psychology`, `daily-mirror`, `emotion-tracking`, `act-therapy`, `self-awareness`, `tts`
