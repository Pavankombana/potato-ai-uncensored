"""
Potato AI Artifacts & Workspace Files Viewer Dialog.
Antigravity-style artifact viewer allowing users to inspect generated code files,
scripts, and project assets with syntax highlighting and quick-copy actions.
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPlainTextEdit, QPushButton, QSplitter,
    QMessageBox, QApplication
)
from PyQt5.QtCore import Qt

class ArtifactsDialog(QDialog):
    def __init__(self, workspace_dir: str, parent=None):
        super().__init__(parent)
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.setWindowTitle("📄 Project Artifacts & Files — Potato AI")
        self.resize(880, 560)
        self._init_ui()
        self._load_files()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # Header
        top_row = QHBoxLayout()
        lbl_head = QLabel("📄 Project Artifacts & Code Viewer")
        lbl_head.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        top_row.addWidget(lbl_head)

        top_row.addStretch()

        btn_refresh = QPushButton("⟳ Refresh")
        btn_refresh.clicked.connect(self._load_files)
        top_row.addWidget(btn_refresh)
        main_layout.addLayout(top_row)

        # Splitter: Left (List of files) / Right (Code Content)
        splitter = QSplitter(Qt.Horizontal)

        # Left List
        self.list_files = QListWidget()
        self.list_files.setStyleSheet("background-color: #0d101d; border: 1px solid #1a2038; border-radius: 6px;")
        self.list_files.currentItemChanged.connect(self._on_file_selected)
        splitter.addWidget(self.list_files)

        # Right Viewer
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self.lbl_selected_file = QLabel("Select a file to inspect")
        self.lbl_selected_file.setStyleSheet("color: #818cf8; font-weight: 600; font-size: 13px;")
        right_layout.addWidget(self.lbl_selected_file)

        self.text_preview = QPlainTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setStyleSheet("""
            QPlainTextEdit {
                background-color: #070912;
                color: #e2e8f0;
                border: 1px solid #1a2038;
                border-radius: 6px;
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.text_preview)

        # Action row
        action_row = QHBoxLayout()
        action_row.addStretch()

        self.btn_copy = QPushButton("📋 Copy Code")
        self.btn_copy.clicked.connect(self._copy_code)
        action_row.addWidget(self.btn_copy)

        right_layout.addLayout(action_row)

        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

    def _load_files(self):
        self.list_files.clear()
        ignored = {".git", "__pycache__", "venv", ".venv", ".idea", ".vscode", "models"}
        for root, dirs, files in os.walk(self.workspace_dir):
            dirs[:] = [d for d in dirs if d not in ignored]
            for f in sorted(files):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, self.workspace_dir)
                item = QListWidgetItem(f"📄 {rel_path}")
                item.setData(Qt.UserRole, full_path)
                self.list_files.addItem(item)

        if self.list_files.count() > 0:
            self.list_files.setCurrentRow(0)

    def _on_file_selected(self, current, previous):
        if not current:
            return
        full_path = current.data(Qt.UserRole)
        if not full_path or not os.path.exists(full_path):
            return

        rel_path = os.path.relpath(full_path, self.workspace_dir)
        self.lbl_selected_file.setText(f"📄 {rel_path}")

        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.text_preview.setPlainText(content)
        except Exception as e:
            self.text_preview.setPlainText(f"Error reading file: {str(e)}")

    def _copy_code(self):
        text = self.text_preview.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", "File contents copied to clipboard!")
