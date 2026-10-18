"""
Potato AI Intelligent Auto-Fix & Engine Diagnostic Assistant.
Diagnoses local inference engine connectivity, detects Ollama installation,
and provides 1-click solutions to start Ollama or download the official installer.
"""

import os
import subprocess
import threading
import requests
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QMessageBox, QFrame, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from core.model_client import ModelClient, DEFAULT_PRESETS

class AutoFixSignals(QObject):
    progress = pyqtSignal(float, float, float)  # downloaded, total, percent
    download_done = pyqtSignal(bool, str)
    engine_started = pyqtSignal(bool, str)

class AutoFixDialog(QDialog):
    connection_restored = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔧 Potato AI Engine Auto-Fix Assistant")
        self.resize(620, 480)
        self.signals = AutoFixSignals()
        self.signals.progress.connect(self._on_download_progress)
        self.signals.download_done.connect(self._on_download_done)
        self.signals.engine_started.connect(self._on_engine_started)
        self._init_ui()
        self._run_diagnostics()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Header
        lbl_head = QLabel("🔧 Local Engine Auto-Fix & Diagnostics")
        lbl_head.setStyleSheet("font-size: 17px; font-weight: bold; color: #ffffff;")
        layout.addWidget(lbl_head)

        lbl_sub = QLabel("Potato AI runs 100% locally and requires a local backend (Ollama, LM Studio, or llama-server).")
        lbl_sub.setWordWrap(True)
        lbl_sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_sub)

        # Diagnostics Card
        self.diag_card = QFrame()
        self.diag_card.setStyleSheet("background-color: #101424; border: 1px solid #1f2747; border-radius: 8px; padding: 12px;")
        diag_layout = QVBoxLayout(self.diag_card)
        diag_layout.setSpacing(8)

        self.lbl_diag_status = QLabel("Checking local ports (11434, 1234, 8080)...")
        self.lbl_diag_status.setStyleSheet("color: #e2e8f0; font-size: 13px; font-weight: 600;")
        diag_layout.addWidget(self.lbl_diag_status)

        self.lbl_ollama_status = QLabel("Detecting Ollama...")
        self.lbl_ollama_status.setStyleSheet("color: #94a3b8; font-size: 12px;")
        diag_layout.addWidget(self.lbl_ollama_status)

        layout.addWidget(self.diag_card)

        # Action Solutions Section
        lbl_actions = QLabel("Recommended Solutions:")
        lbl_actions.setStyleSheet("font-size: 13px; font-weight: bold; color: #818cf8; margin-top: 6px;")
        layout.addWidget(lbl_actions)

        # Solution 1: Start Ollama
        self.btn_start_ollama = QPushButton("⚡ Start Ollama Service (Background)")
        self.btn_start_ollama.setObjectName("primaryButton")
        self.btn_start_ollama.setEnabled(False)
        self.btn_start_ollama.clicked.connect(self._start_ollama_service)
        layout.addWidget(self.btn_start_ollama)

        # Solution 2: Download & Install Ollama
        self.btn_install_ollama = QPushButton("📥 1-Click Download & Install Ollama (Official Installer)")
        self.btn_install_ollama.clicked.connect(self._download_and_install_ollama)
        layout.addWidget(self.btn_install_ollama)

        # Progress bar for installer download
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.lbl_dl_speed = QLabel("")
        self.lbl_dl_speed.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.lbl_dl_speed.setVisible(False)
        layout.addWidget(self.lbl_dl_speed)

        # Solution 3: Custom Port
        custom_layout = QHBoxLayout()
        self.input_custom_url = QLineEdit("http://localhost:1234/v1")
        self.input_custom_url.setPlaceholderText("Enter custom backend URL (e.g. LM Studio port 1234)...")
        custom_layout.addWidget(self.input_custom_url)

        btn_connect_custom = QPushButton("Connect URL")
        btn_connect_custom.clicked.connect(self._connect_custom_url)
        custom_layout.addWidget(btn_connect_custom)
        layout.addLayout(custom_layout)

        layout.addStretch()

        # Footer
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

    def _run_diagnostics(self):
        detected = ModelClient.auto_detect_backend()
        if detected:
            self.lbl_diag_status.setText(f"🟢 Connected to {detected['name']} at {detected['url']}!")
            self.lbl_diag_status.setStyleSheet("color: #34d399; font-size: 13px; font-weight: 600;")
            self.connection_restored.emit(detected["url"])
            return

        self.lbl_diag_status.setText("🔴 All local ports are currently offline (No engine running).")
        self.lbl_diag_status.setStyleSheet("color: #f87171; font-size: 13px; font-weight: 600;")

        # Check if Ollama executable exists in PATH or standard paths
        ollama_path = self._find_ollama_path()
        if ollama_path:
            self.lbl_ollama_status.setText(f"✓ Ollama found on disk at:\n{ollama_path}")
            self.lbl_ollama_status.setStyleSheet("color: #38bdf8; font-size: 12px;")
            self.btn_start_ollama.setEnabled(True)
            self.ollama_bin = ollama_path
        else:
            self.lbl_ollama_status.setText("Ollama is not installed yet. Use the 1-click installer below.")
            self.lbl_ollama_status.setStyleSheet("color: #f59e0b; font-size: 12px;")
            self.btn_install_ollama.setObjectName("primaryButton")

    def _find_ollama_path(self) -> str:
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
            r"C:\Program Files\Ollama\ollama.exe",
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        try:
            res = subprocess.run(["where", "ollama"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip().splitlines()[0]
        except Exception:
            pass
        return ""

    def _start_ollama_service(self):
        self.btn_start_ollama.setEnabled(False)
        self.btn_start_ollama.setText("Starting Ollama Service...")

        def _worker():
            try:
                subprocess.Popen([self.ollama_bin, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import time
                time.sleep(2.5)
                # Test connection
                detected = ModelClient.auto_detect_backend()
                if detected:
                    self.signals.engine_started.emit(True, detected["url"])
                else:
                    self.signals.engine_started.emit(False, "Service started, re-checking...")
            except Exception as e:
                self.signals.engine_started.emit(False, str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_engine_started(self, success: bool, msg: str):
        self.btn_start_ollama.setEnabled(True)
        self.btn_start_ollama.setText("⚡ Start Ollama Service (Background)")
        if success:
            self.connection_restored.emit(msg)
            QMessageBox.information(self, "Connected!", f"Successfully started local engine at:\n{msg}")
            self.accept()
        else:
            self._run_diagnostics()

    def _download_and_install_ollama(self):
        self.btn_install_ollama.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.lbl_dl_speed.setVisible(True)
        self.lbl_dl_speed.setText("Connecting to official Ollama download server...")

        target_dir = os.path.abspath("installer")
        os.makedirs(target_dir, exist_ok=True)
        dest_exe = os.path.join(target_dir, "OllamaSetup.exe")

        def _worker():
            try:
                url = "https://ollama.com/download/OllamaSetup.exe"
                with requests.get(url, stream=True, timeout=15) as r:
                    r.raise_for_status()
                    total_bytes = int(r.headers.get("content-length", 0))
                    downloaded = 0
                    chunk_size = 1024 * 1024
                    with open(dest_exe, "wb") as f:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                pct = (downloaded / total_bytes * 100.0) if total_bytes > 0 else 0
                                self.signals.progress.emit(downloaded, total_bytes, pct)

                self.signals.download_done.emit(True, dest_exe)
            except Exception as e:
                self.signals.download_done.emit(False, str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_download_progress(self, cur, tot, pct):
        cur_mb = cur / (1024 * 1024)
        tot_mb = tot / (1024 * 1024)
        self.progress_bar.setValue(int(pct))
        self.lbl_dl_speed.setText(f"Downloading: {cur_mb:.1f} MB / {tot_mb:.1f} MB ({pct:.1f}%)")

    def _on_download_done(self, success: bool, msg: str):
        self.btn_install_ollama.setEnabled(True)
        if success:
            self.lbl_dl_speed.setText("Download complete! Launching Ollama Setup...")
            try:
                subprocess.Popen([msg])
                QMessageBox.information(self, "Installer Launched", "Ollama installer has launched! Complete the installation, then click 'Auto-Fix' again to connect.")
            except Exception as e:
                QMessageBox.warning(self, "Error Launching Installer", str(e))
        else:
            self.lbl_dl_speed.setText(f"Download failed: {msg}")
            QMessageBox.warning(self, "Download Error", f"Could not download OllamaSetup.exe: {msg}")

    def _connect_custom_url(self):
        url = self.input_custom_url.text().strip()
        if not url:
            return
        client = ModelClient(base_url=url)
        info = client.check_connection()
        if info["connected"]:
            self.connection_restored.emit(url)
            QMessageBox.information(self, "Connected!", f"Successfully connected to backend at:\n{url}")
            self.accept()
        else:
            QMessageBox.warning(self, "Connection Failed", f"Could not reach an OpenAI-compatible backend at:\n{url}\nMake sure the local server is running on that port.")
