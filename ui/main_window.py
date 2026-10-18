"""
Main Application Window for Potato AI Uncensored.
Faithfully recreates the sleek Potato AI minimalist interface while packing all of
Antigravity's core features:
- Project Workspaces Manager
- Persistent Chat Sessions
- Artifacts & Workspace Code Viewer
- Full Settings & RTX 4060 Gaming GPU Tuner
- 1-Click Model Hub (Qwen-2.5-Coder-7B-Instruct-Abliterated)
- Live DuckDuckGo Web Search
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QPushButton, QComboBox, QLabel, QFileDialog,
    QListWidget, QListWidgetItem, QFrame, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer

from core.model_client import ModelClient, DEFAULT_PRESETS
from core.agent import Agent
from core.system_monitor import SystemMonitor
from core.session_manager import SessionManager
from ui.theme import POTATO_AI_THEME_QSS
from ui.components.chat_view import ChatView
from ui.components.terminal_view import AgentTerminalView
from ui.components.model_hub_dialog import ModelHubDialog
from ui.components.settings_dialog import SettingsDialog
from ui.components.artifacts_dialog import ArtifactsDialog
from ui.components.autofix_dialog import AutoFixDialog

class AgentStreamSignals(QObject):
    token_received = pyqtSignal(str)
    tool_started = pyqtSignal(str, dict)
    tool_finished = pyqtSignal(str, str)
    task_done = pyqtSignal(str)
    task_error = pyqtSignal(str)

class CapsulePromptEdit(QPlainTextEdit):
    send_requested = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.send_requested.emit()
                event.accept()
        else:
            super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self, workspace_dir: str = "."):
        super().__init__()
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.web_search_enabled = True
        self.sidebar_visible = True

        # Configuration dictionary
        self.settings = {
            "backend_url": "http://localhost:11434/v1",
            "model": "qwen2.5-coder-uncensored:7b-q4",
            "temperature": 0.2,
            "gpu_layers": 22,
            "web_search_enabled": True,
            "file_tools_enabled": True,
            "terminal_enabled": True,
            "workspace_dir": self.workspace_dir
        }

        # Core logic components
        self.session_manager = SessionManager(os.path.join(self.workspace_dir, ".potato_ai"))
        self.model_client = ModelClient(base_url=self.settings["backend_url"], model=self.settings["model"])
        self.agent = Agent(self.model_client, self.workspace_dir)
        self.system_monitor = SystemMonitor(interval_seconds=2.0)
        self.stream_signals = AgentStreamSignals()

        self.current_session_id = None

        # Connect signals
        self.stream_signals.token_received.connect(self._on_token)
        self.stream_signals.tool_started.connect(self._on_tool_started)
        self.stream_signals.tool_finished.connect(self._on_tool_finished)
        self.stream_signals.task_done.connect(self._on_task_done)
        self.stream_signals.task_error.connect(self._on_task_error)

        self._init_ui()
        self.setStyleSheet(POTATO_AI_THEME_QSS)
        self._start_hardware_monitor()
        self._init_sessions()
        self._check_backend_connection()

    def _init_ui(self):
        self.setWindowTitle("Potato AI — 100% Local Offline AI")
        self.resize(1260, 820)
        self.setMinimumSize(850, 550)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        # 1. Left Sidebar
        self.sidebar_widget = self._create_sidebar()
        main_h_layout.addWidget(self.sidebar_widget)

        # 2. Right Main Content Area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        self.top_bar = self._create_top_bar()
        content_layout.addWidget(self.top_bar)

        # Chat View
        self.chat_view = ChatView()
        self.chat_view.install_model_clicked.connect(self._open_model_hub)
        content_layout.addWidget(self.chat_view, stretch=1)

        # Floating Bottom Input Area
        input_dock = self._create_floating_input()
        content_layout.addWidget(input_dock)

        # Collapsible Console / Action Drawer
        self.terminal_view = AgentTerminalView(self.workspace_dir)
        self.terminal_view.setFixedHeight(160)
        self.terminal_view.setVisible(False)
        content_layout.addWidget(self.terminal_view)

        main_h_layout.addWidget(content_container, stretch=1)

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebarContainer")
        sidebar.setFixedWidth(230)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 16, 14, 14)
        layout.setSpacing(12)

        # Brand row
        top_row = QHBoxLayout()
        lbl_brand = QLabel("🥔 Potato AI")
        lbl_brand.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff;")
        top_row.addWidget(lbl_brand)

        top_row.addStretch()

        btn_collapse = QPushButton("‹")
        btn_collapse.setFixedSize(24, 24)
        btn_collapse.setStyleSheet("background: transparent; border: none; color: #64748b; font-size: 18px;")
        btn_collapse.clicked.connect(self._toggle_sidebar)
        top_row.addWidget(btn_collapse)
        layout.addLayout(top_row)

        # "+ New chat" Button
        self.btn_new_chat = QPushButton("+ New chat")
        self.btn_new_chat.setObjectName("btnNewChat")
        self.btn_new_chat.clicked.connect(self._start_new_chat)
        layout.addWidget(self.btn_new_chat)

        # Section: PROJECT WORKSPACE
        lbl_proj = QLabel("PROJECT")
        lbl_proj.setStyleSheet("font-size: 10px; font-weight: 700; color: #475569; letter-spacing: 0.8px; margin-top: 4px;")
        layout.addWidget(lbl_proj)

        self.btn_project_pill = QPushButton(f"📁 {os.path.basename(self.workspace_dir)}")
        self.btn_project_pill.setObjectName("pillButton")
        self.btn_project_pill.setToolTip("Click to switch project workspace")
        self.btn_project_pill.clicked.connect(self._choose_workspace)
        layout.addWidget(self.btn_project_pill)

        # Section: CHATS
        lbl_chats = QLabel("CHATS")
        lbl_chats.setStyleSheet("font-size: 10px; font-weight: 700; color: #475569; letter-spacing: 0.8px; margin-top: 6px;")
        layout.addWidget(lbl_chats)

        self.chat_list = QListWidget()
        self.chat_list.setObjectName("chatList")
        self.chat_list.currentItemChanged.connect(self._on_session_selected)
        layout.addWidget(self.chat_list, stretch=1)

        # Bottom Utilities: Artifacts & Settings
        util_layout = QHBoxLayout()
        btn_artifacts = QPushButton("📄 Files")
        btn_artifacts.setObjectName("pillButton")
        btn_artifacts.clicked.connect(self._open_artifacts)
        util_layout.addWidget(btn_artifacts)

        btn_settings = QPushButton("⚙ Settings")
        btn_settings.setObjectName("pillButton")
        btn_settings.clicked.connect(self._open_settings)
        util_layout.addWidget(btn_settings)

        layout.addLayout(util_layout)
        return sidebar

    def _create_top_bar(self) -> QWidget:
        top_bar = QWidget()
        top_bar.setObjectName("topNavBar")
        top_bar.setFixedHeight(50)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)

        # Hamburger toggle
        self.btn_hamburger = QPushButton("≡")
        self.btn_hamburger.setFixedSize(28, 28)
        self.btn_hamburger.setStyleSheet("background: transparent; border: none; color: #94a3b8; font-size: 18px;")
        self.btn_hamburger.clicked.connect(self._toggle_sidebar)
        layout.addWidget(self.btn_hamburger)

        # Model selector pill
        self.combo_model = QComboBox()
        self.combo_model.setEditable(False)
        self.combo_model.addItem("Install Model ▾")
        self.combo_model.addItem("Qwen-2.5-Coder-7B-Abliterated")
        self.combo_model.addItem("qwen2.5-coder-uncensored:7b-q4")
        self.combo_model.addItem("qwen2.5-coder-uncensored:7b-q5")
        self.combo_model.currentIndexChanged.connect(self._on_model_combo_changed)
        layout.addWidget(self.combo_model)

        # Web Search Toggle Pill
        self.btn_web_search = QPushButton("🌐 Web Search: ON")
        self.btn_web_search.setObjectName("webSearchActive")
        self.btn_web_search.clicked.connect(self._toggle_web_search)
        layout.addWidget(self.btn_web_search)

        # Console Drawer Toggle
        self.btn_toggle_console = QPushButton("💻 Console")
        self.btn_toggle_console.setObjectName("pillButton")
        self.btn_toggle_console.clicked.connect(self._toggle_console)
        layout.addWidget(self.btn_toggle_console)

        # Artifacts Pill
        btn_art = QPushButton("📄 Artifacts")
        btn_art.setObjectName("pillButton")
        btn_art.clicked.connect(self._open_artifacts)
        layout.addWidget(btn_art)

        layout.addStretch()

        # Telemetry badge
        self.lbl_vram = QLabel("🎮 RTX 4060: -- / 8.0 GB")
        self.lbl_vram.setStyleSheet("color: #818cf8; font-size: 11.5px; font-weight: 600; padding: 0 6px;")
        layout.addWidget(self.lbl_vram)

        # Connection status pill
        self.lbl_status = QLabel("● Offline")
        self.lbl_status.setObjectName("statusOffline")
        layout.addWidget(self.lbl_status)

        # Auto-Fix Button
        self.btn_autofix = QPushButton("Auto-Fix")
        self.btn_autofix.setObjectName("btnAutoFix")
        self.btn_autofix.clicked.connect(self._open_autofix)
        layout.addWidget(self.btn_autofix)

        return top_bar

    def _create_floating_input(self) -> QWidget:
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(20, 10, 20, 20)

        container_layout.addStretch(1)

        self.input_card = QFrame()
        self.input_card.setObjectName("floatingInputContainer")
        self.input_card.setFixedWidth(780)

        card_layout = QHBoxLayout(self.input_card)
        card_layout.setContentsMargins(8, 4, 8, 4)
        card_layout.setSpacing(8)

        self.input_prompt = CapsulePromptEdit()
        self.input_prompt.setObjectName("promptInput")
        self.input_prompt.setPlaceholderText("Ask Potato AI to code, debug, search, or edit files...")
        self.input_prompt.setFixedHeight(44)
        self.input_prompt.send_requested.connect(self._send_prompt)
        card_layout.addWidget(self.input_prompt, stretch=1)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setObjectName("stopButton")
        self.btn_stop.setFixedSize(36, 36)
        self.btn_stop.setVisible(False)
        self.btn_stop.clicked.connect(self._stop_agent)
        card_layout.addWidget(self.btn_stop)

        self.btn_send = QPushButton("↑")
        self.btn_send.setObjectName("sendButton")
        self.btn_send.setFixedSize(36, 36)
        self.btn_send.clicked.connect(self._send_prompt)
        card_layout.addWidget(self.btn_send)

        container_layout.addWidget(self.input_card, stretch=4)
        container_layout.addStretch(1)

        return container

    def _init_sessions(self):
        sessions = self.session_manager.list_sessions()
        self.chat_list.blockSignals(True)
        self.chat_list.clear()

        if not sessions:
            self.current_session_id = self.session_manager.create_session("New chat")
            item = QListWidgetItem("New chat")
            item.setData(Qt.UserRole, self.current_session_id)
            self.chat_list.addItem(item)
            self.chat_list.setCurrentRow(0)
        else:
            for s in sessions:
                item = QListWidgetItem(s.get("title", "Chat"))
                item.setData(Qt.UserRole, s["id"])
                self.chat_list.addItem(item)
            self.chat_list.setCurrentRow(0)
            self.current_session_id = sessions[0]["id"]
            self._load_session_messages(self.current_session_id)

        self.chat_list.blockSignals(False)

    def _load_session_messages(self, session_id: str):
        messages = self.session_manager.get_messages(session_id)
        if not messages:
            self.chat_view.show_hero()
        else:
            self.chat_view.browser.clear()
            for m in messages:
                if m.get("role") == "user":
                    self.chat_view.append_user_message(m.get("content", ""))
                else:
                    self.chat_view.finish_assistant_stream(m.get("content", ""))

    def _on_session_selected(self, current, previous):
        if not current:
            return
        session_id = current.data(Qt.UserRole)
        if session_id:
            self.current_session_id = session_id
            self._load_session_messages(session_id)

    def _start_new_chat(self):
        self.current_session_id = self.session_manager.create_session("New chat")
        self.chat_list.blockSignals(True)
        item = QListWidgetItem("New chat")
        item.setData(Qt.UserRole, self.current_session_id)
        self.chat_list.insertItem(0, item)
        self.chat_list.setCurrentRow(0)
        self.chat_list.blockSignals(False)
        self.chat_view.clear()

    def _toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar_widget.setVisible(self.sidebar_visible)

    def _toggle_console(self):
        is_vis = self.terminal_view.isVisible()
        self.terminal_view.setVisible(not is_vis)

    def _toggle_web_search(self):
        self.web_search_enabled = not self.web_search_enabled
        if self.web_search_enabled:
            self.btn_web_search.setText("🌐 Web Search: ON")
            self.btn_web_search.setObjectName("webSearchActive")
        else:
            self.btn_web_search.setText("🌐 Web Search: OFF")
            self.btn_web_search.setObjectName("webSearchInactive")
        self.btn_web_search.style().unpolish(self.btn_web_search)
        self.btn_web_search.style().polish(self.btn_web_search)

    def _choose_workspace(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Workspace", self.workspace_dir)
        if folder:
            self.workspace_dir = os.path.abspath(folder)
            self.settings["workspace_dir"] = self.workspace_dir
            self.btn_project_pill.setText(f"📁 {os.path.basename(self.workspace_dir)}")
            self.terminal_view.set_workspace(self.workspace_dir)
            self.agent.set_workspace(self.workspace_dir)
            self.session_manager = SessionManager(os.path.join(self.workspace_dir, ".potato_ai"))
            self._init_sessions()

    def _open_model_hub(self):
        models_dir = os.path.join(self.workspace_dir, "models")
        dlg = ModelHubDialog(models_dir=models_dir, parent=self)
        dlg.model_installed.connect(lambda path: self._check_backend_connection())
        dlg.exec_()

    def _open_settings(self):
        dlg = SettingsDialog(current_settings=self.settings, parent=self)
        dlg.settings_saved.connect(self._apply_new_settings)
        dlg.exec_()

    def _apply_new_settings(self, new_settings: dict):
        self.settings.update(new_settings)
        self.model_client.base_url = self.settings["backend_url"]
        self.model_client.model = self.settings["model"]
        self.agent.system_prompt = self.settings.get("system_prompt", self.agent.system_prompt)
        if self.settings["workspace_dir"] != self.workspace_dir:
            self.workspace_dir = self.settings["workspace_dir"]
            self.btn_project_pill.setText(f"📁 {os.path.basename(self.workspace_dir)}")
            self.terminal_view.set_workspace(self.workspace_dir)
            self.agent.set_workspace(self.workspace_dir)
        self._check_backend_connection()

    def _open_artifacts(self):
        dlg = ArtifactsDialog(workspace_dir=self.workspace_dir, parent=self)
        dlg.exec_()

    def _on_model_combo_changed(self, idx):
        if idx == 0:
            self._open_model_hub()
        else:
            model_text = self.combo_model.currentText()
            self.model_client.model = model_text
            self.settings["model"] = model_text

    def _start_hardware_monitor(self):
        def _update_telemetry(metrics):
            used_mb = metrics.get("gpu_vram_used_mb", 0)
            tot_mb = metrics.get("gpu_vram_total_mb", 8188)
            headroom = metrics.get("gaming_headroom", "Optimal")
            QTimer.singleShot(0, lambda: self.lbl_vram.setText(f"🎮 RTX 4060: {used_mb / 1024:.1f} / {tot_mb / 1024:.1f} GB ({headroom.split()[0]})"))

        self.system_monitor.start(callback=_update_telemetry)

    def _check_backend_connection(self):
        detected = ModelClient.auto_detect_backend()
        if detected:
            self.model_client.base_url = detected["url"]
            self.lbl_status.setText("● Online")
            self.lbl_status.setObjectName("statusOnline")
            self.btn_autofix.setVisible(False)

            if detected["models"]:
                self.combo_model.blockSignals(True)
                self.combo_model.clear()
                self.combo_model.addItem("Install Model ▾")
                for m in detected["models"]:
                    self.combo_model.addItem(m)
                self.combo_model.setCurrentIndex(1)
                self.model_client.model = detected["models"][0]
                self.combo_model.blockSignals(False)
        else:
            info = self.model_client.check_connection()
            if info["connected"]:
                self.lbl_status.setText("● Online")
                self.lbl_status.setObjectName("statusOnline")
                self.btn_autofix.setVisible(False)
            else:
                self.lbl_status.setText("● Offline")
                self.lbl_status.setObjectName("statusOffline")
                self.btn_autofix.setVisible(True)

        self.lbl_status.style().unpolish(self.lbl_status)
        self.lbl_status.style().polish(self.lbl_status)

    def _open_autofix(self):
        dlg = AutoFixDialog(parent=self)
        dlg.connection_restored.connect(self._on_connection_restored)
        dlg.exec_()

    def _on_connection_restored(self, url: str):
        self.model_client.base_url = url
        self.settings["backend_url"] = url
        self._check_backend_connection()

    def _send_prompt(self):
        prompt = self.input_prompt.toPlainText().strip()
        if not prompt:
            return

        # Check if local engine is online
        info = self.model_client.check_connection()
        if not info["connected"]:
            reply = QMessageBox.question(
                self, "Engine Offline",
                "Potato AI's local inference engine is currently offline.\n\nWould you like to open the Auto-Fix Assistant to start or install Ollama?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._open_autofix()
            return

        self.input_prompt.clear()
        self.btn_send.setEnabled(False)
        self.btn_stop.setVisible(True)

        # Update session title if first message
        if self.current_session_id and self.chat_list.currentItem():
            cur_title = self.chat_list.currentItem().text()
            if cur_title == "New chat":
                short_title = prompt[:24] + "..." if len(prompt) > 24 else prompt
                self.chat_list.currentItem().setText(short_title)
                self.session_manager.update_title(self.current_session_id, short_title)

        # Save user message
        if self.current_session_id:
            self.session_manager.append_message(self.current_session_id, "user", prompt)

        self.chat_view.append_user_message(prompt)
        self.chat_view.start_assistant_stream()

        # Run agent
        def _on_token(tok):
            self.stream_signals.token_received.emit(tok)

        def _on_tool_start(name, args):
            self.stream_signals.tool_started.emit(name, args)

        def _on_tool_end(name, out):
            self.stream_signals.tool_finished.emit(name, out)

        def _on_done(res):
            self.stream_signals.task_done.emit(res)

        def _on_err(err):
            self.stream_signals.task_error.emit(err)

        self.agent.run_query(
            user_prompt=prompt,
            web_search_enabled=self.web_search_enabled,
            on_token=_on_token,
            on_tool_start=_on_tool_start,
            on_tool_end=_on_tool_end,
            on_done=_on_done,
            on_error=_on_err
        )

    def _stop_agent(self):
        self.agent.stop()
        self.btn_stop.setVisible(False)
        self.btn_send.setEnabled(True)

    def _on_token(self, token: str):
        self.chat_view.append_stream_token(token)

    def _on_tool_started(self, name: str, args: dict):
        self.chat_view.append_tool_notice(name, "running...")
        self.terminal_view.log_action(f"TOOL: {name}", str(args))

    def _on_tool_finished(self, name: str, output: str):
        self.chat_view.append_tool_notice(name, "completed")
        self.terminal_view.log_action(f"RESULT: {name}", output)

    def _on_task_done(self, final_text: str):
        self.btn_send.setEnabled(True)
        self.btn_stop.setVisible(False)
        if self.current_session_id and final_text:
            self.session_manager.append_message(self.current_session_id, "assistant", final_text)

    def _on_task_error(self, err_msg: str):
        self.btn_send.setEnabled(True)
        self.btn_stop.setVisible(False)
        self.chat_view.append_tool_notice("Error", err_msg)
        QMessageBox.warning(self, "Potato AI Notice", err_msg)
