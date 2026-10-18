"""
Potato AI Full Settings & Antigravity Configuration Dialog.
Configures models, local engine backends, RTX 4060 gaming offload,
agent tool permissions, workspace directories, and uncensored system prompts.
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QSlider, QCheckBox,
    QComboBox, QTextEdit, QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from core.prompt_templates import UNCENSORED_AGENT_SYSTEM_PROMPT
from core.system_monitor import SystemMonitor

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal(dict)

    def __init__(self, current_settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙ Potato AI Settings")
        self.resize(680, 520)
        self.settings = dict(current_settings)
        self.system_monitor = SystemMonitor()
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        # Header
        lbl_head = QLabel("⚙ Settings & Engine Configuration")
        lbl_head.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(lbl_head)

        self.tabs = QTabWidget()

        # Tab 1: Engine & Model
        tab_engine = self._build_engine_tab()
        self.tabs.addTab(tab_engine, "Model & Engine")

        # Tab 2: RTX 4060 Gaming Optimizer
        tab_gpu = self._build_gpu_tab()
        self.tabs.addTab(tab_gpu, "🎮 Gaming / GPU")

        # Tab 3: Agent & Tools
        tab_tools = self._build_tools_tab()
        self.tabs.addTab(tab_tools, "Agent Tools")

        # Tab 4: System Prompt
        tab_prompt = self._build_prompt_tab()
        self.tabs.addTab(tab_prompt, "System Prompt")

        main_layout.addWidget(self.tabs)

        # Footer Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("primaryButton")
        btn_save.clicked.connect(self._save_settings)
        btn_layout.addWidget(btn_save)

        main_layout.addLayout(btn_layout)

    def _build_engine_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Local Inference Backend URL:"))
        self.input_url = QLineEdit(self.settings.get("backend_url", "http://localhost:11434/v1"))
        layout.addWidget(self.input_url)

        lbl_presets = QLabel("Quick Presets:")
        lbl_presets.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(lbl_presets)

        preset_row = QHBoxLayout()
        btn_ollama = QPushButton("Ollama (11434)")
        btn_ollama.clicked.connect(lambda: self.input_url.setText("http://localhost:11434/v1"))
        preset_row.addWidget(btn_ollama)

        btn_lmstudio = QPushButton("LM Studio (1234)")
        btn_lmstudio.clicked.connect(lambda: self.input_url.setText("http://localhost:1234/v1"))
        preset_row.addWidget(btn_lmstudio)

        btn_llamacpp = QPushButton("llama-server (8080)")
        btn_llamacpp.clicked.connect(lambda: self.input_url.setText("http://localhost:8080/v1"))
        preset_row.addWidget(btn_llamacpp)
        layout.addLayout(preset_row)

        layout.addWidget(QLabel("Active Model Name:"))
        self.input_model = QLineEdit(self.settings.get("model", "qwen2.5-coder-uncensored:7b-q4"))
        layout.addWidget(self.input_model)

        # Temperature
        temp_val = self.settings.get("temperature", 0.2)
        self.lbl_temp = QLabel(f"Temperature: {temp_val:.2f} (Low = more precise code)")
        layout.addWidget(self.lbl_temp)

        self.slider_temp = QSlider(Qt.Horizontal)
        self.slider_temp.setRange(0, 100)
        self.slider_temp.setValue(int(temp_val * 100))
        self.slider_temp.valueChanged.connect(lambda v: self.lbl_temp.setText(f"Temperature: {v/100:.2f} (Low = more precise code)"))
        layout.addWidget(self.slider_temp)

        layout.addStretch()
        return widget

    def _build_gpu_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        card = QFrame()
        card.setStyleSheet("background-color: #101426; border: 1px solid #1f2747; border-radius: 8px; padding: 12px;")
        card_layout = QVBoxLayout(card)

        metrics = self.system_monitor.query_all()
        gpu_name = metrics.get("gpu_name", "NVIDIA GeForce RTX 4060 Laptop GPU")
        vram_mb = metrics.get("gpu_vram_total_mb", 8188)

        card_layout.addWidget(QLabel(f"<b>Detected Hardware:</b> {gpu_name} ({vram_mb/1024:.1f} GB VRAM)"))
        card_layout.addWidget(QLabel(f"<b>System RAM:</b> {metrics.get('ram_total_gb', 24)} GB"))
        layout.addWidget(card)

        layout.addWidget(QLabel("<b>RTX 4060 Gaming Multitasking Optimizer</b>"))
        desc = QLabel("Adjust GPU layers offload so you can play video games while the AI runs in the background:")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(desc)

        layers_val = self.settings.get("gpu_layers", 22)
        self.lbl_layers = QLabel(f"GPU Layers Offloaded: {layers_val} / 28 layers")
        layout.addWidget(self.lbl_layers)

        self.slider_layers = QSlider(Qt.Horizontal)
        self.slider_layers.setRange(0, 28)
        self.slider_layers.setValue(layers_val)
        self.slider_layers.valueChanged.connect(self._on_layers_changed)
        layout.addWidget(self.slider_layers)

        self.lbl_est_headroom = QLabel(self._calc_headroom_text(layers_val))
        self.lbl_est_headroom.setStyleSheet("background-color: #0b241c; color: #34d399; padding: 6px 10px; border-radius: 6px; font-weight: 600;")
        layout.addWidget(self.lbl_est_headroom)

        layout.addStretch()
        return widget

    def _on_layers_changed(self, v):
        self.lbl_layers.setText(f"GPU Layers Offloaded: {v} / 28 layers")
        self.lbl_est_headroom.setText(self._calc_headroom_text(v))

    def _calc_headroom_text(self, layers: int) -> str:
        est_vram_used = (layers / 28.0) * 5.2
        est_free = max(0.0, 8.0 - est_vram_used)
        if est_free >= 3.5:
            return f"Estimated ~{est_free:.1f} GB VRAM Free for Video Games (Optimal Headroom)"
        elif est_free >= 1.5:
            return f"Estimated ~{est_free:.1f} GB VRAM Free (Moderate Gaming Headroom)"
        else:
            return f"Estimated ~{est_free:.1f} GB VRAM Free (High VRAM Load - May cause game stutter)"

    def _build_tools_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        self.cb_web_search = QCheckBox("Enable DuckDuckGo Web Search Tool")
        self.cb_web_search.setChecked(self.settings.get("web_search_enabled", True))
        layout.addWidget(self.cb_web_search)

        self.cb_file_ops = QCheckBox("Enable Workspace File Tools (read, write, edit, list)")
        self.cb_file_ops.setChecked(self.settings.get("file_tools_enabled", True))
        layout.addWidget(self.cb_file_ops)

        self.cb_term = QCheckBox("Enable Terminal Command Execution (PowerShell/CMD)")
        self.cb_term.setChecked(self.settings.get("terminal_enabled", True))
        layout.addWidget(self.cb_term)

        layout.addWidget(QLabel("Active Project Workspace Folder:"))
        ws_layout = QHBoxLayout()
        self.input_ws = QLineEdit(self.settings.get("workspace_dir", os.getcwd()))
        ws_layout.addWidget(self.input_ws)

        btn_browse_ws = QPushButton("Browse...")
        btn_browse_ws.clicked.connect(self._browse_workspace)
        ws_layout.addWidget(btn_browse_ws)
        layout.addLayout(ws_layout)

        layout.addStretch()
        return widget

    def _browse_workspace(self):
        d = QFileDialog.getExistingDirectory(self, "Select Workspace Folder", self.input_ws.text())
        if d:
            self.input_ws.setText(d)

    def _build_prompt_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Uncensored Agent System Prompt Directives:"))
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setPlainText(self.settings.get("system_prompt", UNCENSORED_AGENT_SYSTEM_PROMPT))
        self.txt_prompt.setStyleSheet("background-color: #0b0d17; color: #a5f3fc; font-family: monospace; font-size: 11.5px;")
        layout.addWidget(self.txt_prompt)

        btn_reset_prompt = QPushButton("Reset to Default Uncensored Directives")
        btn_reset_prompt.setFixedWidth(240)
        btn_reset_prompt.clicked.connect(lambda: self.txt_prompt.setPlainText(UNCENSORED_AGENT_SYSTEM_PROMPT))
        layout.addWidget(btn_reset_prompt)

        return widget

    def _save_settings(self):
        self.settings["backend_url"] = self.input_url.text().strip()
        self.settings["model"] = self.input_model.text().strip()
        self.settings["temperature"] = self.slider_temp.value() / 100.0
        self.settings["gpu_layers"] = self.slider_layers.value()
        self.settings["web_search_enabled"] = self.cb_web_search.isChecked()
        self.settings["file_tools_enabled"] = self.cb_file_ops.isChecked()
        self.settings["terminal_enabled"] = self.cb_term.isChecked()
        self.settings["workspace_dir"] = self.input_ws.text().strip()
        self.settings["system_prompt"] = self.txt_prompt.toPlainText().strip()

        self.settings_saved.emit(self.settings)
        self.accept()
