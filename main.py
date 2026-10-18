"""
Potato AI — 100% Local Offline AI & Uncensored Coding Agent.
Entry point script.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow

def main():
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Potato AI")
    app.setOrganizationName("PotatoAI")

    workspace = os.path.abspath(os.path.dirname(__file__))

    window = MainWindow(workspace_dir=workspace)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
