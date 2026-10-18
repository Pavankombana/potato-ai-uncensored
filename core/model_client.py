"""
Universal Local Model Client (OpenAI API Compatible).
Connects seamlessly to Ollama, LM Studio, llama-server, and local endpoints.
Provides model discovery, health checks, and token-by-token streaming.
"""

import json
import requests
from typing import List, Dict, Any, Optional, Callable

DEFAULT_PRESETS = {
    "Ollama": "http://localhost:11434/v1",
    "LM Studio": "http://localhost:1234/v1",
    "llama-server": "http://localhost:8080/v1"
}

class ModelClient:
    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "qwen2.5-coder-uncensored:7b-q4"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._is_aborted = False

    def abort(self):
        self._is_aborted = True

    def check_connection(self) -> Dict[str, Any]:
        """Test connection to the model server and discover models."""
        try:
            url = f"{self.base_url}/models"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                models = []
                if "data" in data and isinstance(data["data"], list):
                    models = [m.get("id") for m in data["data"] if m.get("id")]
                return {
                    "connected": True,
                    "models": models,
                    "server": self.base_url
                }
        except Exception:
            pass
        return {
            "connected": False,
            "models": [],
            "server": self.base_url
        }

    @staticmethod
    def auto_detect_backend() -> Optional[Dict[str, Any]]:
        """Scan standard ports to see which local inference engine is currently running."""
        for name, url in DEFAULT_PRESETS.items():
            try:
                resp = requests.get(f"{url}/models", timeout=1.5)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                    return {
                        "name": name,
                        "url": url,
                        "models": models
                    }
            except Exception:
                continue
        return None

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        token_callback: Optional[Callable[[str], None]] = None,
        done_callback: Optional[Callable[[str], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Stream chat response token by token via SSE.
        """
        self._is_aborted = False
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        full_content = []
        try:
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=(5, 60)) as resp:
                if resp.status_code != 200:
                    err_msg = f"Server returned error code {resp.status_code}: {resp.text}"
                    if error_callback:
                        error_callback(err_msg)
                    return

                for line in resp.iter_lines(decode_unicode=True):
                    if self._is_aborted:
                        break
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            choices = chunk.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                token = delta.get("content", "")
                                if token:
                                    full_content.append(token)
                                    if token_callback:
                                        token_callback(token)
                        except json.JSONDecodeError:
                            continue

            complete_text = "".join(full_content)
            if done_callback:
                done_callback(complete_text)

        except Exception as err:
            if error_callback:
                error_callback(f"Inference error: {str(err)}")
