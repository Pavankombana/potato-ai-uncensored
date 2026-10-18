# ⚡ Antigravity Mini — Uncensored Local AI Coding Studio

An ultra-lightweight (<70MB RAM), fast, desktop AI Coding Agent application modeled after Antigravity. Powered locally by **Qwen-2.5-Coder-7B-Instruct-Abliterated** (GGUF format, `Q4_K_M` or `Q5_K_M` quant) with real-time DuckDuckGo web search, workspace tool execution, and live RTX 4060 VRAM / Gaming multitasking monitoring.

---

## 🌟 Key Features

1. **Uncensored & Direct Coding Agent**:
   - Zero moralizing, no lecturing, no refusal boilerplate, and no preachy disclaimers.
   - Writes clean, complete, production-ready code immediately.
2. **1-Click Model Hub & Downloader**:
   - Built-in catalog to install `Qwen-2.5-Coder-7B-Instruct-Abliterated` (`Q4_K_M` ~4.68GB or `Q5_K_M` ~5.43GB) with a single click.
   - Option to download any custom GGUF model from Hugging Face with download resume support.
   - 1-Click Ollama Modelfile generator (`ollama create ...`).
3. **DuckDuckGo Web Search Integration**:
   - Live web search scraper (zero API keys required) with toggle switch `[🌐 Web Search: ON/OFF]`.
   - Injects fresh documentation, syntax, and error solutions directly into the model context.
4. **Antigravity-Style Agentic Tools**:
   - Autonomous ReAct loop capable of reading files, writing code, applying surgical diffs, browsing project trees, and executing PowerShell/CMD commands.
5. **Ultra-Low Memory Footprint (<70MB RAM)**:
   - Native PyQt5 desktop interface engineered for speed, low CPU overhead, and zero browser bloat.
6. **Live Hardware Telemetry & Gaming Headroom**:
   - Status bar monitors RTX 4060 VRAM used/total, GPU load %, and system RAM in real-time.
   - Shows multitasking headroom status so your games run smoothly while the AI codes.

---

## 🚀 Quick Start

### 1. Launch the App
Double-click `run.bat` or run in terminal:
```bash
python main.py
```

### 2. Install the Uncensored Model (1-Click)
1. In the app toolbar, click **`⚡ 1-Click Model Hub`**.
2. Click **`⚡ 1-Click Install`** next to **Qwen-2.5-Coder-7B-Instruct-Abliterated (Q4_K_M)**.
3. Once downloaded, switch to the **💾 Installed Models** tab and click **`⚡ Register in Ollama (1-Click)`**.

---

## 🎮 Gaming & Multitasking Tuning (RTX 4060 Laptop 8GB + 24GB RAM)

To game smoothly without FPS drops while running the model:
- **Recommended Model**: `Q4_K_M` (~4.68 GB VRAM).
- **GPU Layer Offload**:
  - In Ollama / llama-server, offload **20 to 22 layers** to the GPU (`-ngl 22`).
  - This offloads ~4.0 GB to your 8GB VRAM and places the remaining layers in your 24GB system RAM, leaving **~4.0 GB of dedicated VRAM completely free for video games** (GTA V, CS2, Cyberpunk, etc.).

---

## 📂 Project Architecture

```text
p:\Antigravity\Uncencored ai agent\
│── main.py                     # App entry point
│── run.bat                     # 1-Click Windows launcher
│── requirements.txt            # Minimal dependencies (PyQt5, requests, bs4, psutil)
│── README.md                   # Documentation & guide
│── core/
│   ├── agent.py                # Autonomous agent ReAct loop with streaming
│   ├── model_client.py         # Universal OpenAI-compatible streaming client
│   ├── prompt_templates.py     # Uncensored coding prompt & system directives
│   ├── search.py               # Zero-key DuckDuckGo web search scraper
│   ├── tools.py                # Workspace file operations and command runner
│   ├── downloader.py           # 1-Click multi-threaded Hugging Face GGUF downloader
│   └── system_monitor.py       # Live VRAM, GPU, and RAM telemetry
└── ui/
    ├── main_window.py          # Primary IDE layout with resizable splitters
    ├── theme.py                # Antigravity dark QSS theme
    └── components/
        ├── chat_view.py        # Chat messages, code blocks, copy & apply buttons
        ├── file_tree.py        # Workspace directory browser
        ├── terminal_view.py    # Collapsible agent action log & terminal
        └── model_hub_dialog.py # 1-Click Model Downloader, Selector & Modelfile Creator
```
