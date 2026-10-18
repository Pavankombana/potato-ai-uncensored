"""
1-Click Model Downloader and Hub Dialog.
Provides one-click installation for Qwen-2.5-Coder-7B-Instruct-Abliterated (Q4_K_M / Q5_K_M),
custom Hugging Face GGUF downloads, and automated Ollama / LM Studio registration.
"""

import os
import subprocess
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QProgressBar, QLineEdit, QListWidget,
    QListWidgetItem, QMessageBox, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from core.downloader import ModelDownloader, MODELS_CATALOG

class DownloadSignals(QObject):
    progress = pyqtSignal(float, float, float, float)  # downloaded, total, speed, percent
    completed = pyqtSignal(bool, str)

class ModelHubDialog(QDialog):
    model_installed = pyqtSignal(str)

    def __init__(self, models_dir: str = "models", parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚡ 1-Click Model Hub — Antigravity Mini")
        self.resize(750, 580)
        self.models_dir = os.path.abspath(models_dir)
        self.downloader = ModelDownloader(self.models_dir)
        self.signals = DownloadSignals()

        self.signals.progress.connect(self._on_download_progress)
        self.signals.completed.connect(self._on_download_completed)

        self._init_ui()
        self._refresh_installed()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Header
        header = QLabel("⚡ 1-Click Model Manager & Hub")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        main_layout.addWidget(header)

        sub = QLabel(f"Download uncensored GGUF coding models directly to: <code>{self.models_dir}</code>")
        sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        main_layout.addWidget(sub)

        # Tabs
        self.tabs = QTabWidget()

        # Tab 1: Catalog
        tab_catalog = self._build_catalog_tab()
        self.tabs.addTab(tab_catalog, "🌟 Curated Models")

        # Tab 2: Custom URL
        tab_custom = self._build_custom_tab()
        self.tabs.addTab(tab_custom, "🌐 Custom HuggingFace GGUF")

        # Tab 3: Installed Models
        tab_installed = self._build_installed_tab()
        self.tabs.addTab(tab_installed, "💾 Installed Models")

        main_layout.addWidget(self.tabs)

        # Download Status Box (Persistent at bottom)
        self.download_box = QFrame()
        self.download_box.setStyleSheet("background-color: #12151d; border: 1px solid #262b3a; border-radius: 6px; padding: 8px;")
        dl_layout = QVBoxLayout(self.download_box)
        dl_layout.setSpacing(6)

        self.lbl_dl_status = QLabel("Ready. Select a model to install.")
        self.lbl_dl_status.setStyleSheet("color: #94a3b8; font-size: 12px;")
        dl_layout.addWidget(self.lbl_dl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)
        dl_layout.addWidget(self.progress_bar)

        btn_cancel_layout = QHBoxLayout()
        btn_cancel_layout.addStretch()
        self.btn_cancel_dl = QPushButton("Cancel Download")
        self.btn_cancel_dl.setEnabled(False)
        self.btn_cancel_dl.clicked.connect(self._cancel_download)
        btn_cancel_layout.addWidget(self.btn_cancel_dl)
        dl_layout.addLayout(btn_cancel_layout)

        main_layout.addWidget(self.download_box)

    def _build_catalog_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)

        for model in MODELS_CATALOG:
            card = QFrame()
            card.setStyleSheet("background-color: #161922; border: 1px solid #262b3a; border-radius: 8px; padding: 10px;")
            card_layout = QHBoxLayout(card)

            info_layout = QVBoxLayout()
            title = QLabel(model["name"])
            title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 13px;")
            info_layout.addWidget(title)

            desc = QLabel(model["desc"])
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
            info_layout.addWidget(desc)

            meta = QLabel(f"Size: ~{model['size_gb']} GB  |  File: {model['filename']}")
            meta.setStyleSheet("color: #64748b; font-size: 11px;")
            info_layout.addWidget(meta)

            card_layout.addLayout(info_layout, stretch=1)

            btn_dl = QPushButton("⚡ 1-Click Install")
            btn_dl.setObjectName("primaryButton")
            btn_dl.setFixedWidth(130)
            btn_dl.clicked.connect(lambda checked, m=model: self._start_download(m["url"], m["filename"], m["name"]))
            card_layout.addWidget(btn_dl)

            scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        return widget

    def _build_custom_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        lbl = QLabel("Paste any direct Hugging Face GGUF resolve link:")
        lbl.setStyleSheet("color: #cbd5e1; font-weight: bold;")
        layout.addWidget(lbl)

        self.input_custom_url = QLineEdit()
        self.input_custom_url.setPlaceholderText("https://huggingface.co/.../resolve/main/model-name-Q4_K_M.gguf")
        layout.addWidget(self.input_custom_url)

        lbl_fn = QLabel("Target Filename:")
        lbl_fn.setStyleSheet("color: #cbd5e1;")
        layout.addWidget(lbl_fn)

        self.input_custom_filename = QLineEdit()
        self.input_custom_filename.setPlaceholderText("custom-model-Q4_K_M.gguf")
        layout.addWidget(self.input_custom_filename)

        self.btn_download_custom = QPushButton("Download Custom Model")
        self.btn_download_custom.setObjectName("primaryButton")
        self.btn_download_custom.clicked.connect(self._start_custom_download)
        layout.addWidget(self.btn_download_custom)

        layout.addStretch()
        return widget

    def _build_installed_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.list_installed = QListWidget()
        self.list_installed.setStyleSheet("background-color: #12151d; border: 1px solid #262b3a;")
        layout.addWidget(self.list_installed)

        btn_row = QHBoxLayout()
        self.btn_refresh_installed = QPushButton("⟳ Refresh")
        self.btn_refresh_installed.clicked.connect(self._refresh_installed)
        btn_row.addWidget(self.btn_refresh_installed)

        self.btn_register_ollama = QPushButton("⚡ Register in Ollama (1-Click)")
        self.btn_register_ollama.setObjectName("primaryButton")
        self.btn_register_ollama.clicked.connect(self._register_selected_in_ollama)
        btn_row.addWidget(self.btn_register_ollama)

        self.btn_delete_model = QPushButton("🗑️ Delete")
        self.btn_delete_model.clicked.connect(self._delete_selected_model)
        btn_row.addWidget(self.btn_delete_model)

        layout.addLayout(btn_row)
        return widget

    def _refresh_installed(self):
        self.list_installed.clear()
        models = self.downloader.list_installed_models()
        if not models:
            item = QListWidgetItem("No GGUF models downloaded yet. Use the 'Curated Models' tab to install one.")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.list_installed.addItem(item)
            return

        for m in models:
            item = QListWidgetItem(f"💾 {m['filename']}  ({m['size_gb']} GB)  —  Path: {m['path']}")
            item.setData(Qt.UserRole, m)
            self.list_installed.addItem(item)

    def _start_download(self, url: str, filename: str, friendly_name: str):
        dest_path = os.path.join(self.models_dir, filename)
        if os.path.exists(dest_path):
            QMessageBox.information(self, "Model Already Exists", f"'{filename}' is already downloaded in:\n{self.models_dir}")
            return

        self.lbl_dl_status.setText(f"Connecting to Hugging Face for '{friendly_name}'...")
        self.progress_bar.setValue(0)
        self.btn_cancel_dl.setEnabled(True)

        def _prog(cur, tot, spd, pct):
            self.signals.progress.emit(cur, tot, spd, pct)

        def _done(success, msg):
            self.signals.completed.emit(success, msg)

        self.downloader.download_file(url, filename, _prog, _done)

    def _start_custom_download(self):
        url = self.input_custom_url.text().strip()
        filename = self.input_custom_filename.text().strip()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Please enter a valid Hugging Face GGUF URL.")
            return
        if not filename:
            filename = url.split("/")[-1].split("?")[0]
            if not filename.endswith(".gguf"):
                filename += ".gguf"
            self.input_custom_filename.setText(filename)

        self._start_download(url, filename, filename)

    def _cancel_download(self):
        self.downloader.cancel()
        self.lbl_dl_status.setText("Cancelling download...")
        self.btn_cancel_dl.setEnabled(False)

    def _on_download_progress(self, cur, tot, spd, pct):
        cur_gb = cur / (1024 ** 3)
        tot_gb = tot / (1024 ** 3)
        self.progress_bar.setValue(int(pct))
        self.lbl_dl_status.setText(f"Downloading: {cur_gb:.2f} GB / {tot_gb:.2f} GB ({pct:.1f}%) | Speed: {spd:.1f} MB/s")

    def _on_download_completed(self, success: bool, msg: str):
        self.btn_cancel_dl.setEnabled(False)
        if success:
            self.progress_bar.setValue(100)
            self.lbl_dl_status.setText(f"✅ Download complete! Saved to {os.path.basename(msg)}")
            self._refresh_installed()
            self.model_installed.emit(msg)
            QMessageBox.information(self, "Download Complete", f"Successfully installed model:\n{msg}")
        else:
            self.lbl_dl_status.setText(f"❌ {msg}")
            QMessageBox.warning(self, "Download Interrupted", msg)

    def _register_selected_in_ollama(self):
        curr = self.list_installed.currentItem()
        if not curr:
            QMessageBox.information(self, "Select Model", "Please select an installed model from the list.")
            return

        data = curr.data(Qt.UserRole)
        if not data:
            return

        filename = data["filename"]
        tag_name = filename.lower().replace(".gguf", "").replace("-instruct", "").replace("-abliterated", "-uncensored")

        # Generate Modelfile
        modelfile_path = self.downloader.generate_ollama_modelfile(filename, tag_name)

        # Run ollama create
        cmd = f"ollama create {tag_name} -f \"{modelfile_path}\""
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
            if res.returncode == 0:
                QMessageBox.information(self, "Ollama Registration Complete", f"Successfully registered model in Ollama:\nTag: {tag_name}\n\nCommand output:\n{res.stdout}")
            else:
                QMessageBox.warning(self, "Ollama Registration Notice", f"Modelfile created at:\n{modelfile_path}\n\nOllama command:\n{cmd}\n\nDetails: {res.stderr or res.stdout}\n(Make sure Ollama is installed and running)")
        except Exception as err:
            QMessageBox.warning(self, "Modelfile Created", f"Modelfile successfully generated at:\n{modelfile_path}\n\nTo import into Ollama manually, run:\nollama create {tag_name} -f \"{modelfile_path}\"")

    def _delete_selected_model(self):
        curr = self.list_installed.currentItem()
        if not curr:
            return
        data = curr.data(Qt.UserRole)
        if not data:
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{data['filename']}' ({data['size_gb']} GB)?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                os.remove(data["path"])
                self._refresh_installed()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete: {str(e)}")
