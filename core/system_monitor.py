"""
Hardware Telemetry & Gaming Multitasking Monitor.
Continuously queries NVIDIA GPU VRAM/Load and System RAM/CPU to provide real-time
headroom metrics so the user can verify gaming performance while the AI model runs.
"""

import time
import psutil
import threading
import subprocess
from typing import Dict, Any, Optional, Callable

class SystemMonitor:
    def __init__(self, interval_seconds: float = 2.0):
        self.interval = interval_seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self.last_metrics: Dict[str, Any] = {
            "gpu_name": "Detecting...",
            "gpu_vram_used_mb": 0,
            "gpu_vram_total_mb": 8188,
            "gpu_vram_free_mb": 8188,
            "gpu_vram_percent": 0.0,
            "gpu_util_percent": 0,
            "ram_used_gb": 0.0,
            "ram_total_gb": 24.0,
            "ram_percent": 0.0,
            "cpu_percent": 0.0,
            "gaming_headroom": "Optimal"
        }

    def start(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self._callback = callback
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def query_gpu(self) -> Dict[str, Any]:
        """Query GPU memory and load via nvidia-smi."""
        try:
            startupinfo = None
            if hasattr(subprocess, "STARTUPINFO"):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu,name", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=2,
                startupinfo=startupinfo
            )
            if res.returncode == 0 and res.stdout.strip():
                parts = [p.strip() for p in res.stdout.strip().split(",")]
                if len(parts) >= 4:
                    used_mb = float(parts[0])
                    total_mb = float(parts[1])
                    util_pct = int(parts[2])
                    gpu_name = parts[3]
                    free_mb = max(0.0, total_mb - used_mb)
                    pct = (used_mb / total_mb * 100.0) if total_mb > 0 else 0.0

                    return {
                        "gpu_name": gpu_name,
                        "gpu_vram_used_mb": used_mb,
                        "gpu_vram_total_mb": total_mb,
                        "gpu_vram_free_mb": free_mb,
                        "gpu_vram_percent": round(pct, 1),
                        "gpu_util_percent": util_pct
                    }
        except Exception:
            pass
        return {}

    def query_all(self) -> Dict[str, Any]:
        """Fetch current snapshot of system resources."""
        gpu_stats = self.query_gpu()
        
        # System RAM & CPU via psutil
        vmem = psutil.virtual_memory()
        cpu_pct = psutil.cpu_percent(interval=None)

        metrics = dict(self.last_metrics)
        metrics.update(gpu_stats)
        metrics["ram_used_gb"] = round(vmem.used / (1024 ** 3), 1)
        metrics["ram_total_gb"] = round(vmem.total / (1024 ** 3), 1)
        metrics["ram_percent"] = vmem.percent
        metrics["cpu_percent"] = cpu_pct

        free_vram_gb = metrics.get("gpu_vram_free_mb", 0) / 1024.0
        if free_vram_gb >= 3.0:
            metrics["gaming_headroom"] = "Optimal (Smooth Gaming)"
        elif free_vram_gb >= 1.5:
            metrics["gaming_headroom"] = "Moderate Headroom"
        else:
            metrics["gaming_headroom"] = "Low VRAM (Heavy Multitask)"

        self.last_metrics = metrics
        return metrics

    def _loop(self):
        while self._running:
            metrics = self.query_all()
            if self._callback:
                try:
                    self._callback(metrics)
                except Exception:
                    pass
            time.sleep(self.interval)

if __name__ == "__main__":
    monitor = SystemMonitor()
    m = monitor.query_all()
    print("VRAM Used:", m["gpu_vram_used_mb"], "MB /", m["gpu_vram_total_mb"], "MB")
    print("GPU Util:", m["gpu_util_percent"], "%")
    print("System RAM:", m["ram_used_gb"], "GB /", m["ram_total_gb"], "GB")
    print("Gaming Headroom:", m["gaming_headroom"])
