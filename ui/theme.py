"""
Potato AI Midnight Developer Theme.
Matching the minimalist Potato AI layout: deep midnight navy, rounded pills,
vibrant indigo/purple accents, and floating capsule inputs.
"""

POTATO_AI_THEME_QSS = """
/* Global Reset */
QWidget {
    background-color: #0c0e17;
    color: #e2e8f0;
    font-family: 'Segoe UI Variable Display', 'Segoe UI', -apple-system, sans-serif;
    font-size: 13px;
    outline: none;
}

QMainWindow {
    background-color: #0c0e17;
}

/* Sidebar Styling */
QWidget#sidebarContainer {
    background-color: #090a12;
    border-right: 1px solid #161928;
}

/* Toolbars / Top Bar */
QWidget#topNavBar {
    background-color: #0c0e17;
    border-bottom: 1px solid #151828;
    padding: 6px 16px;
}

/* Splitters */
QSplitter::handle {
    background-color: #141726;
}
QSplitter::handle:horizontal {
    width: 1px;
}
QSplitter::handle:vertical {
    height: 1px;
}

/* Buttons - Rounded Pills */
QPushButton {
    background-color: #141829;
    color: #cbd5e1;
    border: 1px solid #1e243d;
    border-radius: 12px;
    padding: 6px 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #1b2138;
    border-color: #2e375c;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #101321;
}

/* New Chat Button */
QPushButton#btnNewChat {
    background-color: #13172b;
    color: #ffffff;
    border: 1px solid #232a4e;
    border-radius: 10px;
    padding: 10px 16px;
    font-weight: 600;
    font-size: 13px;
    text-align: center;
}
QPushButton#btnNewChat:hover {
    background-color: #1e2444;
    border-color: #3b4580;
}

/* Pill / Action Buttons */
QPushButton#pillButton {
    background-color: #131729;
    color: #e2e8f0;
    border: 1px solid #202642;
    border-radius: 14px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#pillButton:hover {
    background-color: #1b2038;
    border-color: #313b63;
}

/* Send Button - Purple Capsule */
QPushButton#sendButton {
    background-color: #5558f6;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton#sendButton:hover {
    background-color: #4346eb;
}
QPushButton#sendButton:pressed {
    background-color: #3538c9;
}
QPushButton#sendButton:disabled {
    background-color: #212445;
    color: #505580;
}

/* Stop Button */
QPushButton#stopButton {
    background-color: #7f1d1d;
    color: #fecaca;
    border: 1px solid #dc2626;
    border-radius: 10px;
    font-size: 13px;
}
QPushButton#stopButton:hover {
    background-color: #991b1b;
}

/* Web Search Pill */
QPushButton#webSearchActive {
    background-color: #0d2822;
    color: #34d399;
    border: 1px solid #059669;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#webSearchInactive {
    background-color: #131729;
    color: #64748b;
    border: 1px solid #1e243d;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 12px;
}
QPushButton#webSearchInactive:hover {
    color: #94a3b8;
    border-color: #2e375c;
}

/* Status Badges */
QLabel#statusOnline {
    background-color: #0c201a;
    color: #34d399;
    border: 1px solid #065f46;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#statusOffline {
    background-color: #241116;
    color: #f87171;
    border: 1px solid #7f1d1d;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton#btnAutoFix {
    background-color: #1f1418;
    color: #f87171;
    border: 1px solid #991b1b;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton#btnAutoFix:hover {
    background-color: #36171e;
}

/* Floating Input Box Capsule */
QFrame#floatingInputContainer {
    background-color: #101323;
    border: 1px solid #202642;
    border-radius: 20px;
    padding: 4px 8px;
}
QFrame#floatingInputContainer:focus-within {
    border: 1px solid #4f46e5;
    background-color: #121528;
}

/* Text Areas */
QPlainTextEdit#promptInput {
    background-color: transparent;
    color: #f8fafc;
    border: none;
    font-size: 13.5px;
    padding: 8px 12px;
}
QPlainTextEdit#promptInput:focus {
    border: none;
    background-color: transparent;
}

/* ComboBoxes */
QComboBox {
    background-color: #131729;
    color: #f1f5f9;
    border: 1px solid #202642;
    border-radius: 12px;
    padding: 5px 12px;
    min-width: 130px;
    font-size: 12px;
}
QComboBox:hover {
    border-color: #313b63;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 0px;
}
QComboBox QAbstractItemView {
    background-color: #101323;
    border: 1px solid #242c4c;
    selection-background-color: #4f46e5;
    color: #ffffff;
    padding: 6px;
    border-radius: 8px;
}

/* List Widgets (Chat list) */
QListWidget#chatList {
    background-color: transparent;
    border: none;
    color: #cbd5e1;
}
QListWidget#chatList::item {
    background-color: transparent;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 2px;
    font-size: 13px;
}
QListWidget#chatList::item:hover {
    background-color: #15192e;
    color: #ffffff;
}
QListWidget#chatList::item:selected {
    background-color: #1c2240;
    color: #ffffff;
    border-left: 2px solid #6366f1;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #1b2038;
    min-height: 24px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #2b335c;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
