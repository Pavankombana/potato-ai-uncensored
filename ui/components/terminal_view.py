"""
Minimalist Console Dock & Action Log.
Sleek dark monospace terminal with unobtrusive layout.
"""

import subprocess
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPlainTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt5.QtCore import pyqtSignal, QObject

class TerminalWorkerSignals(QObject):
    output_received = pyqtSignal(str)
    command_finished = pyqtSignal(int)

class AgentTerminalView(QWidget):
    def __init__(self, workspace_dir: str, parent=None):
        super().__init__(parent)
        self.workspace_dir = workspace_dir
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()

        # Tab 1: Agent Actions
        tab_log = QWidget()
        layout_log = QVBoxLayout(tab_log)
        layout_log.setContentsMargins(6, 6, 6, 6)
        layout_log.setSpacing(4)

        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #07090e;
                color: #38bdf8;
                border: 1px solid #141926;
                border-radius: 6px;
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 11.5px;
                padding: 6px;
            }
        """)
        layout_log.addWidget(self.log_text)

        log_actions = QHBoxLayout()
        log_actions.addStretch()
        btn_clear = QPushButton("Clear")
        btn_clear.setFixedHeight(22)
        btn_clear.setStyleSheet("padding: 2px 8px; font-size: 11px;")
        btn_clear.clicked.connect(self.log_text.clear)
        log_actions.addWidget(btn_clear)
        layout_log.addLayout(log_actions)

        self.tabs.addTab(tab_log, "Activity")

        # Tab 2: Terminal
        tab_term = QWidget()
        layout_term = QVBoxLayout(tab_term)
        layout_term.setContentsMargins(6, 6, 6, 6)
        layout_term.setSpacing(4)

        self.term_output = QPlainTextEdit()
        self.term_output.setReadOnly(True)
        self.term_output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #07090e;
                color: #e2e8f0;
                border: 1px solid #141926;
                border-radius: 6px;
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 11.5px;
                padding: 6px;
            }
        """)
        layout_term.addWidget(self.term_output)

        cmd_layout = QHBoxLayout()
        cmd_layout.setSpacing(6)

        self.input_cmd = QLineEdit()
        self.input_cmd.setPlaceholderText("Run command (e.g. python main.py)...")
        self.input_cmd.returnPressed.connect(self._run_cmd)
        cmd_layout.addWidget(self.input_cmd)

        self.btn_run = QPushButton("Run")
        self.btn_run.setFixedHeight(28)
        self.btn_run.clicked.connect(self._run_cmd)
        cmd_layout.addWidget(self.btn_run)

        layout_term.addLayout(cmd_layout)

        self.tabs.addTab(tab_term, "Terminal")
        layout.addWidget(self.tabs)

    def set_workspace(self, workspace_dir: str):
        self.workspace_dir = workspace_dir

    def log_action(self, title: str, details: str = ""):
        msg = f"[{title}]\n"
        if details:
            msg += f"{details.strip()}\n"
        msg += "\n"
        self.log_text.appendPlainText(msg)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def _run_cmd(self):
        cmd = self.input_cmd.text().strip()
        if not cmd:
            return
        self.input_cmd.clear()
        self.term_output.appendPlainText(f"\n$ {cmd}\n")

        signals = TerminalWorkerSignals()
        signals.output_received.connect(self.term_output.appendPlainText)
        signals.command_finished.connect(lambda code: self.term_output.appendPlainText(f"[Exit code: {code}]\n"))

        def _exec():
            try:
                proc = subprocess.Popen(
                    ["powershell", "-NoProfile", "-Command", cmd],
                    cwd=self.workspace_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                for line in proc.stdout:
                    signals.output_received.emit(line.rstrip())
                for line in proc.stderr:
                    signals.output_received.emit(f"ERR: {line.rstrip()}")
                proc.wait()
                signals.command_finished.emit(proc.returncode)
            except Exception as e:
                signals.output_received.emit(f"Error: {str(e)}")

        threading.Thread(target=_exec, daemon=True).start()
