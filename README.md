# 🪞 self-distiller

> 把你自己蒸馏成 AI，再用你自己的声音跟自己对话。

Distill yourself into an AI and talk to yourself in your own voice.

---

## ✨ 它是什么

self-distiller 是一个 **自我反思工具**。它从你的聊天记录、笔记、社交媒体中提炼出你的 Persona（人格画像），然后用 **你自己克隆的声音** 跟你对话。

不是聊天机器人，不是日记，不是冥想——是**听到自己的想法被说出来**后的深度自我觉察。

### 心理学依据

研究表明，听到自己的声音能显著增强自我认知和情绪调节能力：
- 自己的声音促进认知解离（cognitive defusion）效果优于他人声音 — [PMC 11274574](https://pmc.ncbi.nlm.nih.gov/articles/PMC11274574/) (2024)
- 自己的声音帮助理解自己的情绪 — [New Scientist](https://www.newscientist.com/article/dn28753-sound-of-your-own-voice-may-help-you-understand-your-emotions/)
- 自己的声音影响自我认知和行为 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0892199722000376)

---

## 🎯 核心场景

### 🌅 晨间独白 (Daily Mirror)
每天早上，AI 用你的语气跟你聊聊昨天的状态，帮你梳理今天的思路。关键反思段落用你的声音朗读。

### 🔥 情绪旁观者 (Emotion Observer)
情绪激动时来找它。AI 不安慰、不评判，用你的声音**原样回放**你的情绪核心，帮你跟自己的想法拉开距离。

### ⚖️ 内心辩论 (Inner Debate) *v2*
面对决策时，AI 用你的声音扮演"冲动版你"和"理性版你"互相辩论，你来当裁判。

### 📦 时间胶囊 (Time Capsule) *v2*
对比不同时期的 Persona 版本，用你的声音给过去/未来的自己写一封信。

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────┐
│                  self-distiller                   │
├────────────┬────────────┬────────────────────────┤
│  Distill   │   Mirror   │      Evolve            │
│  蒸馏层    │   镜像层    │      进化层            │
├────────────┼────────────┼────────────────────────┤
│ 原材料采集  │ 晨间独白    │ Persona 偏差修正       │
│ Persona    │ 情绪旁观者  │ 时间线版本管理          │
│ 提炼       │ 内心辩论    │ 数据追加               │
│ SELF.md    │ 时间胶囊    │ 持续学习               │
├────────────┴────────────┴────────────────────────┤
│              语音基础设施                          │
│  ListenHub: Voice Clone + TTS + ASR              │
└─────────────────────────────────────────────────┘
```

---

## 🚀 快速开始（5 分钟上手）

### Step 0: 前置要求

- [OpenClaw](https://openclaw.ai) — AI Agent 运行时
- Python 3.9+ 和 `requests`（`pip install requests`）
- [ListenHub API Key](https://listenhub.ai/settings/api-keys) — 免费注册即可获取

### Step 1: 安装

```bash
# 克隆到 OpenClaw workspace/skills/ 目录
cd ~/.openclaw/workspace/skills/
git clone https://github.com/KKenny0/self-distiller-skill.git self-distiller

# 设置 API Key
export LISTENHUB_API_KEY="your-key-here"
```

### Step 2: 创建你的 Persona

在 OpenClaw 中输入：

```
/create-self
```

回答 3 个问题：
1. **代号** — 你想叫什么（不是真名）
2. **一句话介绍自己** — 你的背景和兴趣
3. **一句话描述性格** — 你的性格特点

选择数据导入方式：
- **[A] 自动采集**（推荐）— 直接用你已有的 OpenClaw 记忆数据
- **[B] 手动导入** — 导入微信/Discord/Twitter 聊天记录
- **[C] 快速启动** — 先用已有数据生成，后续补充

### Step 3: 选择声音

self-distiller 会列出可用的预设声音，选择一个最接近你自己的：

```
可用声音（中文）：
  CN-Man-Beijing-V2      — 北京男声，沉稳
  CN-Woman-General-01    — 通用女声，自然
  CN-Man-General-01      — 通用男声，清晰

选择一个，或者上传你的语音样本进行克隆（需要付费）。
```

### Step 4: 开始你的第一次独白

```
/mirror
```

AI 会用你的语气跟你对话。关键的反思段落会用你选择的声音朗读出来。

### 所有命令

| 命令 | 功能 |
|------|------|
| `/create-self` | 创建新的自我蒸馏 |
| `/mirror` | 晨间独白 — 每日自我对话 |
| `/observe` | 情绪旁观者 — 情绪觉察 |
| `/update-self` | 更新/修正 Persona |
| `/list-selves` | 列出所有 Persona 版本 |

---

## 📂 文件结构

```
self-distiller/
├── SKILL.md              # Skill 定义（OpenClaw 读取）
├── DESIGN.md             # 设计文档
├── README.md             # 本文件
├── tools/                # 工具脚本
│   ├── voice.py          # ListenHub 语音 API 封装
│   ├── parsers/          # 数据解析器
│   │   ├── discord.py    # Discord 聊天记录
│   │   ├── wechat.py     # 微信导出格式
│   │   ├── twitter.py    # Twitter/X
│   │   └── markdown.py   # Markdown/笔记
│   └── persona.py        # Persona 提炼引擎
├── prompts/              # 提示词模板
│   ├── intake.md         # 基础信息采集
│   ├── distill.md        # Persona 提炼
│   ├── mirror.md         # 晨间独白
│   ├── observe.md        # 情绪旁观者
│   ├── debate.md         # 内心辩论
│   └── capsule.md        # 时间胶囊
└── references/           # 参考资料
    └── psychology.md     # 心理学研究摘要
```

---

## 🔄 与 ex-skill / colleague-skill 的区别

| | ex-skill | colleague-skill | **self-distiller** |
|--|---------|----------------|-------------------|
| 蒸馏对象 | 前任 | 同事 | **你自己** |
| 目的 | 怀念/疗愈 | 工作效率 | **自我反思/成长** |
| 互动模式 | 跟 ta 聊天 | 模拟 ta 的反馈 | **跟自己对话** |
| 声音 | 不需要 | 不需要 | **自己的声音（核心）** |
| 心理学基础 | 怀旧疗法 | 组织行为学 | **认知解离 + 自我觉察** |

---

## 🛡️ 安全边界

- 仅用于个人成长，不用于操控、欺骗或冒充他人
- 所有数据仅本地存储，不上传第三方（ListenHub API 除外）
- 不替代专业心理治疗
- 不鼓励自恋或沉迷

---

## 📄 License

MIT

---

## 🙏 致谢

灵感来源：
- [ex-skill](https://github.com/therealXiaomanChu/ex-skill) — 前任蒸馏
- [colleague-skill](https://github.com/titanwings/colleague-skill) — 同事蒸馏
- [ListenHub Skills](https://listenhub.ai/docs/en/skills) — 语音基础设施
- Stuart McGill's *Back Mechanic* — "听到自己的声音"概念启发
