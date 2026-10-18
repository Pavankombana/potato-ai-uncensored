# 🥔 Potato AI — 100% Local Offline AI & Uncensored Coding Agent

<p align="center">
  <img src="https://raw.githubusercontent.com/Pavankombana/potato-ai-uncensored/main/.github/assets/potato_logo.png" alt="Potato AI Logo" width="120" onerror="this.style.display='none'"/>
</p>

<p align="center">
  <b>The Ultra-Lightweight, Zero-Lecture Local AI Coding Agent for Developers & Gamers.</b><br>
  Powered by <b>Qwen-2.5-Coder-7B-Instruct-Abliterated</b> &bull; Real-Time Web Search &bull; RTX 4060 Gaming Optimizer
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Model-Qwen_2.5_Coder_7B_Abliterated-6366f1?style=for-the-badge&logo=huggingface" alt="Model"/>
  <img src="https://img.shields.io/badge/GPU-RTX_4060_Optimized-76b900?style=for-the-badge&logo=nvidia" alt="RTX 4060"/>
  <img src="https://img.shields.io/badge/Memory-%3C100MB_RAM-0284c7?style=for-the-badge" alt="RAM"/>
  <img src="https://img.shields.io/badge/Censorship-ZERO_Lectures-ef4444?style=for-the-badge" alt="Uncensored"/>
  <img src="https://img.shields.io/badge/Web_Search-DuckDuckGo_Live-10b981?style=for-the-badge&logo=duckduckgo" alt="Search"/>
  <img src="https://img.shields.io/badge/Platform-Windows_x64-0078d4?style=for-the-badge&logo=windows" alt="Windows"/>
</p>

---

## 🌟 What is Potato AI?

**Potato AI** is a minimalist, native desktop AI Coding Agent application modeled after Antigravity and designed specifically for local execution on Windows laptops with **NVIDIA GeForce RTX 4060 (8GB VRAM) and 24GB RAM**.

Unlike corporate cloud AI assistants, Potato AI runs **100% locally and privately offline**, will **never lecture or preach to you**, and is engineered with a **gaming multitasking offloader** so you can code while playing high-end video games without frame drops.

---

## 🚀 Key Features

- 🥔 **100% Uncensored Coding**: Zero preaching, zero moralizing disclaimers, no refusal boilerplate, and no conversational fluff. Direct production-ready code immediately.
- ⚡ **Standalone `PotatoAI.exe`**: Pre-compiled native executable. Just double-click to launch—no Python commands or terminal setup required.
- 🌐 **Real-Time Web Search**: Built-in zero-key DuckDuckGo web search scraper that fetches fresh documentation, library syntax, and error solutions on the fly.
- 🎮 **RTX 4060 Gaming Headroom Optimizer**: Dynamic GPU layer offload calculator (`0-28` layers). Offloads 20-22 layers to GPU VRAM (~4.0 GB) and remaining layers to your 24GB system RAM, leaving **~4.0 GB VRAM completely free for gaming**.
- 🛠️ **Autonomous Agent Tools**: Reads project files, writes code, applies surgical diff replacements, inspects directory structures, and runs PowerShell commands.
- 📥 **1-Click Model Hub**: Install `Qwen-2.5-Coder-7B-Instruct-Abliterated` (`Q4_K_M` ~4.68GB or `Q5_K_M` ~5.43GB) with one click, or paste any custom Hugging Face GGUF link with resumable downloads.
- 🔧 **Intelligent Auto-Fix Assistant**: Proactively diagnoses offline engines, starts local background services with 1 click, or downloads the official Ollama installer.
- 📄 **Project Artifacts & Code Viewer**: Antigravity-style inspector to view generated files, diffs, and copy snippets with syntax highlighting.
- 💾 **Persistent Chat Sessions**: Multi-chat session management automatically saved across launches.

---

## 📥 Quick Start

### 1. Download & Run
Double-click [**`PotatoAI.exe`**](https://github.com/Pavankombana/potato-ai-uncensored/raw/main/PotatoAI.exe) in the repository folder, or launch via:
```powershell
python main.py
# or
run.bat
```

### 2. Download the Model
1. Click **`Install Model ▾`** in the top navigation bar or **`📥 Get started - Install a model`** on the home screen.
2. Under **🌟 Curated Models**, click **`⚡ 1-Click Install`** next to:
   - **`Qwen-2.5-Coder-7B-Instruct-Abliterated (Q4_K_M)`** (~4.68 GB) — *Recommended for smooth multitasking & gaming*.
3. Model files are stored locally in `P:\Antigravity\model\` or `./models/`.

### 3. Connect Local Engine (1-Click Auto-Fix)
If the status pill shows `● Offline`:
- Click the **`Auto-Fix`** button.
- If Ollama is installed, click **`⚡ Start Ollama Service`**.
- If not installed, click **`📥 1-Click Download & Install Ollama`** to download the official installer.

---

## 🎮 Multitasking & Gaming Tuning Guide

| Setting | GPU Layers (`-ngl`) | VRAM Used | Free VRAM for Games | Use Case |
|---|---|---|---|---|
| **Max Gaming Headroom** *(Recommended)* | **20 - 22** | **~4.0 GB** | **~4.0 GB Free** | AAA Games (Cyberpunk, GTA V, CS2) + Active AI Coding |
| **Moderate Headroom** | **24** | **~4.8 GB** | **~3.2 GB Free** | Lighter games (LoL, Valorant, indie games) |
| **Max Coding Speed** | **28 (All)** | **~5.5 GB** | **~2.5 GB Free** | Dedicated coding mode without gaming |

---

## 📂 Project Architecture

```text
potato-ai-uncensored/
│── PotatoAI.exe                # Standalone 1-click Windows executable
│── main.py                     # Python application entry point
│── run.bat                     # Windows batch launcher
│── requirements.txt            # Minimal dependencies (PyQt5, requests, bs4, psutil)
│── test_suite.py               # Automated verification test suite
│── core/
│   ├── agent.py                # Autonomous agent ReAct loop with streaming
│   ├── model_client.py         # Universal OpenAI-compatible streaming client
│   ├── prompt_templates.py     # Strict uncensored coding prompt & system directives
│   ├── search.py               # Zero-key DuckDuckGo live web search scraper
│   ├── tools.py                # Workspace file tools & PowerShell executor
│   ├── downloader.py           # Multi-threaded Hugging Face GGUF downloader
│   ├── session_manager.py      # Persistent chat history management
│   └── system_monitor.py       # Live RTX 4060 VRAM, GPU & RAM telemetry
└── ui/
    ├── main_window.py          # Minimalist Potato AI layout & navigation
    ├── theme.py                # Midnight dark QSS stylesheet
    └── components/
        ├── chat_view.py        # Cute Potato hero screen & markdown code view
        ├── autofix_dialog.py   # Intelligent engine auto-fix assistant
        ├── settings_dialog.py  # Full settings & RTX 4060 gaming tuner
        ├── artifacts_dialog.py # Antigravity-style code artifact inspector
        ├── model_hub_dialog.py # 1-Click Model Hub & Ollama Modelfile generator
        ├── file_tree.py        # Workspace directory browser
        └── terminal_view.py    # Collapsible console & action dock
```

---

## 🛡️ License

Open-source under the [MIT License](LICENSE). Built with ❤️ for developers who want raw, uncensored coding power without corporate preaching.
