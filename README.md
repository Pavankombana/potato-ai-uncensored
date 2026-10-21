# Potato AI — Local & Uncensored

<p align="center">
  <img src="https://github.com/Pavankombana/potato-ai-uncensored/blob/main/Potato%20ai%20uncensored%20logo.png" alt="Potato AI Logo" width="120" onerror="this.style.display='none'"/>
</p>

<p align="center">
  <b>Fast local AI coding for developers — no cloud, no lecture, Uncensored,Code Anything.</b>
</p>

---

## What
Potato AI is a lightweight, local coding agent that runs on your Windows machine and supports multiple local models (GGUF/Ollama-compatible). It gives direct, production-ready coding help without refusal boilerplate.

---

## Why
- 100% local & private
- Model‑agnostic: use community models or your own.
- Uncensored: focused on solutions, not lectures.
- Works well on systems with 6+ GB VRAM and low memory overhead.

---

## Features
- Install or paste any local model (GGUF/Ollama)
- One‑click model hub and engine Auto‑Fix
- Real‑time DuckDuckGo search for docs & fixes
- Project-aware edits, diffs, and persistent chats
- GPU tuning for balanced local performance

---

## Quick Start
Double‑click `PotatoAI.exe` or run:
```powershell
python main.py
# or
run.bat
```
Install a model via the Model Hub or paste a GGUF/Ollama link. Use Auto‑Fix if the runtime is offline.

---

## Tuning (6+ GB VRAM systems)
| Mode | GPU Layers | Best For |
|---|---:|---|
| Performance Headroom | 20–22 | Running other apps alongside coding tasks |
| Balanced | 24 | Daily work |
| Max Speed | 28 | Dedicated coding session |

---

## Project layout
```text
potato-ai-uncensored/
├── PotatoAI.exe
├── main.py
├── core/
│   ├── model_client.py   # model-agnostic runtime adapters
│   └── agent.py
└── ui/
    └── main_window.py
```

---

## License
MIT — use responsibly. Potato AI empowers local, uncensored development; users remain responsible for following laws and licenses.
