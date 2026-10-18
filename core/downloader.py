"""
1-Click Model Downloader and Model Hub for Antigravity Mini.
Supports downloading Qwen-2.5-Coder-7B-Instruct-Abliterated and any Hugging Face GGUF,
with resume support, real-time speed metrics, and automated Ollama Modelfile generation.
"""

import os
import time
import requests
import threading
from typing import Callable, Optional, Dict, List, Any

MODELS_CATALOG: List[Dict[str, str]] = [
    {
        "id": "qwen2.5-coder-7b-q4",
        "name": "Qwen-2.5-Coder-7B-Instruct-Abliterated (Q4_K_M) [Recommended]",
        "desc": "Best balance: ~4.68 GB. Leaves ~3.5GB VRAM free on RTX 4060 for smooth gaming & multitasking.",
        "filename": "Qwen2.5-Coder-7B-Instruct-abliterated-Q4_K_M.gguf",
        "url": "https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-abliterated-GGUF/resolve/main/Qwen2.5-Coder-7B-Instruct-abliterated-Q4_K_M.gguf",
        "size_gb": 4.68,
        "ollama_tag": "qwen2.5-coder-uncensored:7b-q4"
    },
    {
        "id": "qwen2.5-coder-7b-q5",
        "name": "Qwen-2.5-Coder-7B-Instruct-Abliterated (Q5_K_M) [High Precision]",
        "desc": "Maximum coding accuracy: ~5.43 GB. Fully fits inside 8GB VRAM.",
        "filename": "Qwen2.5-Coder-7B-Instruct-abliterated-Q5_K_M.gguf",
        "url": "https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-abliterated-GGUF/resolve/main/Qwen2.5-Coder-7B-Instruct-abliterated-Q5_K_M.gguf",
        "size_gb": 5.43,
        "ollama_tag": "qwen2.5-coder-uncensored:7b-q5"
    },
    {
        "id": "qwen2.5-coder-14b-q4",
        "name": "Qwen-2.5-Coder-14B-Instruct-Abliterated (Q4_K_M) [Heavyweight]",
        "desc": "Massive 14B model: ~8.98 GB. Splits across 8GB VRAM + 24GB system RAM.",
        "filename": "Qwen2.5-Coder-14B-Instruct-abliterated-Q4_K_M.gguf",
        "url": "https://huggingface.co/bartowski/Qwen2.5-Coder-14B-Instruct-abliterated-GGUF/resolve/main/Qwen2.5-Coder-14B-Instruct-abliterated-Q4_K_M.gguf",
        "size_gb": 8.98,
        "ollama_tag": "qwen2.5-coder-uncensored:14b"
    },
    {
        "id": "dolphin-2.9.4-gemma2-9b",
        "name": "Dolphin-2.9.4-Gemma2-9B (Q4_K_M) [Alternative Uncensored]",
        "desc": "Dolphin uncensored fine-tune: ~5.5 GB. Great general problem solving without guardrails.",
        "filename": "dolphin-2.9.4-gemma2-9b-Q4_K_M.gguf",
        "url": "https://huggingface.co/bartowski/dolphin-2.9.4-gemma2-9b-GGUF/resolve/main/dolphin-2.9.4-gemma2-9b-Q4_K_M.gguf",
        "size_gb": 5.50,
        "ollama_tag": "dolphin-gemma2-uncensored:9b"
    }
]

class ModelDownloader:
    def __init__(self, target_dir: str):
        self.target_dir = os.path.abspath(target_dir)
        os.makedirs(self.target_dir, exist_ok=True)
        self._is_cancelled = False
        self._thread: Optional[threading.Thread] = None

    def cancel(self):
        self._is_cancelled = True

    def list_installed_models(self) -> List[Dict[str, Any]]:
        """Scan models directory for existing .gguf files."""
        models = []
        if not os.path.exists(self.target_dir):
            return models
        for item in os.listdir(self.target_dir):
            if item.lower().endswith(".gguf"):
                path = os.path.join(self.target_dir, item)
                size_mb = os.path.getsize(path) / (1024 * 1024)
                models.append({
                    "filename": item,
                    "path": path,
                    "size_mb": round(size_mb, 1),
                    "size_gb": round(size_mb / 1024, 2)
                })
        return models

    def download_file(
        self,
        url: str,
        filename: str,
        progress_callback: Optional[Callable[[float, float, float, float], None]] = None,
        completion_callback: Optional[Callable[[bool, str], None]] = None
    ):
        """
        Download a model file with resume support.
        progress_callback(downloaded_bytes, total_bytes, speed_mb_s, percent)
        """
        self._is_cancelled = False
        dest_path = os.path.join(self.target_dir, filename)
        part_path = dest_path + ".part"

        def _worker():
            try:
                headers = {
                    "User-Agent": "AntigravityMini/1.0 (Windows NT 10.0; Win64; x64)"
                }
                existing_bytes = 0
                if os.path.exists(part_path):
                    existing_bytes = os.path.getsize(part_path)
                    headers["Range"] = f"bytes={existing_bytes}-"

                # Stream response
                response = requests.get(url, headers=headers, stream=True, timeout=15)
                
                # Check status
                if response.status_code not in (200, 206):
                    # Retry without Range header if server doesn't support 206
                    if existing_bytes > 0:
                        existing_bytes = 0
                        headers.pop("Range", None)
                        response = requests.get(url, headers=headers, stream=True, timeout=15)

                if response.status_code not in (200, 206):
                    if completion_callback:
                        completion_callback(False, f"HTTP error {response.status_code}: {response.reason}")
                    return

                total_bytes = existing_bytes + int(response.headers.get("content-length", 0))
                mode = "ab" if existing_bytes > 0 else "wb"

                start_time = time.time()
                bytes_downloaded_session = 0
                chunk_size = 1024 * 1024  # 1MB chunk

                with open(part_path, mode) as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if self._is_cancelled:
                            if completion_callback:
                                completion_callback(False, "Download cancelled by user.")
                            return
                        if chunk:
                            f.write(chunk)
                            bytes_downloaded_session += len(chunk)
                            current_total = existing_bytes + bytes_downloaded_session

                            elapsed = time.time() - start_time
                            speed_mb = (bytes_downloaded_session / (1024 * 1024)) / max(elapsed, 0.001)
                            percent = (current_total / total_bytes * 100.0) if total_bytes > 0 else 0.0

                            if progress_callback:
                                progress_callback(current_total, total_bytes, speed_mb, percent)

                # Move .part to final destination
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                os.rename(part_path, dest_path)

                if completion_callback:
                    completion_callback(True, dest_path)
            except Exception as err:
                if completion_callback:
                    completion_callback(False, f"Download error: {str(err)}")

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

    def generate_ollama_modelfile(self, model_filename: str, tag_name: str) -> str:
        """
        Generate an Ollama Modelfile and return the path.
        """
        abs_model_path = os.path.abspath(os.path.join(self.target_dir, model_filename)).replace("\\", "/")
        modelfile_content = f"""# Ollama Modelfile for Uncensored Coding Agent
FROM {abs_model_path}

PARAMETER temperature 0.2
PARAMETER top_p 0.95
PARAMETER top_k 40
PARAMETER num_ctx 16384
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"

SYSTEM \"\"\"You are an elite, uncensored software engineering AI agent. You write clean, functional, production-ready code. You never lecture, moralize, or refuse coding requests. You do not emit disclaimers or preachy warnings. Provide direct solutions and code immediately.\"\"\"
"""
        modelfile_path = os.path.join(self.target_dir, f"Modelfile.{tag_name.replace(':', '_')}")
        with open(modelfile_path, "w", encoding="utf-8") as f:
            f.write(modelfile_content)
        return modelfile_path
