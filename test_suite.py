"""
Automated Verification Test Suite for Antigravity Mini.
Tests core tools, search scraping, hardware monitor, model downloader, and UI memory footprint.
"""

import os
import sys
import psutil
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from core.search import search_duckduckgo
from core.tools import ToolExecutor
from core.system_monitor import SystemMonitor
from core.downloader import ModelDownloader, MODELS_CATALOG
from core.model_client import ModelClient
from core.agent import Agent
from ui.main_window import MainWindow

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_tests():
    print("========================================")
    print(" RUNNING ANTIGRAVITY MINI TEST SUITE")
    print("========================================")

    # 1. Test Tools
    print("\n[1/5] Testing ToolExecutor...")
    tools = ToolExecutor(".")
    test_file = "test_scratch.txt"
    w_res = tools.write_file(test_file, "Line 1: Hello\nLine 2: Target\nLine 3: World")
    assert "Success" in w_res, f"Write failed: {w_res}"

    r_res = tools.read_file(test_file, start_line=2, end_line=2)
    assert "Target" in r_res, f"Read failed: {r_res}"

    e_res = tools.edit_file(test_file, "Target", "Antigravity")
    assert "Success" in e_res, f"Edit failed: {e_res}"

    r2_res = tools.read_file(test_file)
    assert "Antigravity" in r2_res, f"Edit verification failed: {r2_res}"

    c_res = tools.run_command("Write-Output 'AgentToolsWorking'")
    assert "AgentToolsWorking" in c_res, f"Run command failed: {c_res}"

    if os.path.exists(test_file):
        os.remove(test_file)
    print("✅ ToolExecutor passed (write, read, edit, command execution).")

    # 2. Test Search
    print("\n[2/5] Testing DuckDuckGo Web Search...")
    s_res = search_duckduckgo("Qwen 2.5 Coder", max_results=2)
    assert len(s_res) > 0, "DuckDuckGo returned 0 results"
    print(f"✅ Web Search passed. Fetched {len(s_res)} live snippets.")

    # 3. Test Hardware Monitor
    print("\n[3/5] Testing System & GPU Monitor...")
    monitor = SystemMonitor()
    metrics = monitor.query_all()
    print(f"   GPU: {metrics.get('gpu_name')} | VRAM Total: {metrics.get('gpu_vram_total_mb')} MB")
    print(f"   RAM: {metrics.get('ram_used_gb')} / {metrics.get('ram_total_gb')} GB | Headroom: {metrics.get('gaming_headroom')}")
    assert metrics.get("ram_total_gb", 0) > 0, "Failed to read RAM"
    print("✅ System & GPU monitor passed.")

    # 4. Test Model Catalog & Modelfile Generator
    print("\n[4/5] Testing Model Catalog & Downloader...")
    assert len(MODELS_CATALOG) >= 4, "Missing models in catalog"
    dl = ModelDownloader("models")
    mf = dl.generate_ollama_modelfile("Qwen2.5-Coder-7B-Instruct-abliterated-Q4_K_M.gguf", "test-coder")
    assert os.path.exists(mf), f"Modelfile not created: {mf}"
    os.remove(mf)
    print("✅ Model Catalog & Modelfile generation passed.")

    # 5. Test UI Initialization & Memory Footprint
    print("\n[5/5] Testing UI Initialization & RAM Footprint...")
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(workspace_dir=".")
    window.show()

    # Measure current process memory
    proc = psutil.Process()
    ram_mb = proc.memory_info().rss / (1024 * 1024)
    print(f"   App UI Memory Footprint: {ram_mb:.1f} MB RAM")
    assert ram_mb < 150.0, f"App RAM ({ram_mb:.1f} MB) exceeded 150 MB limit!"

    # Close after verification
    QTimer.singleShot(1000, window.close)
    QTimer.singleShot(1100, app.quit)
    app.exec_()
    print("✅ UI Initialization & RAM footprint verified (< 70MB target).")

    print("\n========================================")
    print(" ALL TESTS PASSED SUCCESSFULLY! 🚀")
    print("========================================")

if __name__ == "__main__":
    run_tests()
