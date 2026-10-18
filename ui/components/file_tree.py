"""
Minimalist Workspace File Tree Explorer.
Clean hierarchy, subtle hover states, and uncluttered file actions.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeView,
    QFileSystemModel, QMenu, QAction, QInputDialog, QMessageBox, QPushButton
)
from PyQt5.QtCore import Qt, QDir, pyqtSignal

class WorkspaceFileTree(QWidget):
    file_selected = pyqtSignal(str)

    def __init__(self, root_dir: str, parent=None):
        super().__init__(parent)
        self.root_dir = os.path.abspath(root_dir)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Minimal header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(6, 4, 6, 0)
        self.label_title = QLabel("FILES")
        self.label_title.setStyleSheet("font-weight: 700; color: #475569; font-size: 10px; letter-spacing: 0.8px;")
        header_layout.addWidget(self.label_title)

        header_layout.addStretch()

        self.btn_refresh = QPushButton("⟳")
        self.btn_refresh.setToolTip("Refresh files")
        self.btn_refresh.setFixedSize(22, 22)
        self.btn_refresh.setStyleSheet("background: transparent; border: none; color: #64748b; font-size: 13px;")
        self.btn_refresh.clicked.connect(self.refresh)
        header_layout.addWidget(self.btn_refresh)

        layout.addLayout(header_layout)

        # File system model
        self.model = QFileSystemModel()
        self.model.setRootPath(self.root_dir)
        self.model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        # Tree view
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.root_dir))
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(14)
        for col in range(1, 4):
            self.tree.setColumnHidden(col, True)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._open_context_menu)
        self.tree.doubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.tree)

    def set_root_dir(self, new_dir: str):
        self.root_dir = os.path.abspath(new_dir)
        self.model.setRootPath(self.root_dir)
        self.tree.setRootIndex(self.model.index(self.root_dir))

    def refresh(self):
        self.model.setRootPath(self.root_dir)
        self.tree.setRootIndex(self.model.index(self.root_dir))

    def _on_item_double_clicked(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            self.file_selected.emit(file_path)

    def _open_context_menu(self, point):
        index = self.tree.indexAt(point)
        target_path = self.model.filePath(index) if index.isValid() else self.root_dir
        is_dir = os.path.isdir(target_path)
        parent_dir = target_path if is_dir else os.path.dirname(target_path)

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #121622;
                border: 1px solid #1e2638;
                border-radius: 8px;
                padding: 4px;
                color: #e2e8f0;
            }
            QMenu::item {
                padding: 6px 14px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0284c7;
                color: #ffffff;
            }
        """)

        act_new_file = QAction("New File...", self)
        act_new_file.triggered.connect(lambda: self._create_new_file(parent_dir))
        menu.addAction(act_new_file)

        act_new_folder = QAction("New Folder...", self)
        act_new_folder.triggered.connect(lambda: self._create_new_folder(parent_dir))
        menu.addAction(act_new_folder)

        if index.isValid():
            menu.addSeparator()
            act_delete = QAction("Delete", self)
            act_delete.triggered.connect(lambda: self._delete_item(target_path))
            menu.addAction(act_delete)

        menu.exec_(self.tree.viewport().mapToGlobal(point))

    def _create_new_file(self, folder: str):
        name, ok = QInputDialog.getText(self, "New File", "File name:")
        if ok and name.strip():
            path = os.path.join(folder, name.strip())
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("")
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _create_new_folder(self, folder: str):
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name.strip():
            path = os.path.join(folder, name.strip())
            try:
                os.makedirs(path, exist_ok=True)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _delete_item(self, path: str):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete '{os.path.basename(path)}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
