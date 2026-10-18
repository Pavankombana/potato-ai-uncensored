"""
Potato AI Chat View Component.
Matches the screenshot layout: cute potato hero avatar, bold Potato AI title,
"100% Local Offline AI" subtitle, and "Get started - Install a model" pill.
"""

import re
import html
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import pyqtSignal

POTATO_SVG_DATA = """<svg width="64" height="46" viewBox="0 0 64 46" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 24C10 14 19 6 32 6C47 6 56 12 54 24C52 36 44 41 30 41C16 41 14 34 12 24Z" fill="#E6D3B3"/>
  <ellipse cx="26" cy="20" rx="2" ry="2.5" fill="#3D2D1D"/>
  <ellipse cx="38" cy="20" rx="2" ry="2.5" fill="#3D2D1D"/>
  <path d="M29 26C30.5 28 33.5 28 35 26" stroke="#3D2D1D" stroke-width="1.8" stroke-linecap="round"/>
  <circle cx="20" cy="24" r="1.5" fill="#D4B68A" opacity="0.6"/>
  <circle cx="45" cy="27" r="1.8" fill="#D4B68A" opacity="0.6"/>
</svg>"""

class ChatView(QWidget):
    install_model_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.raw_stream_markdown = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet("""
            QTextBrowser {
                background-color: transparent;
                color: #e2e8f0;
                border: none;
                padding: 20px 40px;
                font-family: 'Segoe UI', -apple-system, sans-serif;
                font-size: 13.5px;
                line-height: 1.6;
            }
        """)
        self.browser.anchorClicked.connect(self._handle_anchor_click)

        layout.addWidget(self.browser)
        self.show_hero()

    def show_hero(self):
        hero_html = f"""
        <div style="text-align: center; padding-top: 100px;">
            <div style="margin-bottom: 14px;">
                {POTATO_SVG_DATA}
            </div>
            <h1 style="font-size: 24px; font-weight: 700; color: #ffffff; margin: 0 0 6px 0; letter-spacing: -0.2px;">
                Potato AI
            </h1>
            <p style="font-size: 13px; color: #64748b; margin: 0 0 240px 0;">
                100% Local Offline AI &bull; Uncensored Coding Agent
            </p>

            <div>
                <a href="#action:install_model" style="text-decoration: none;">
                    <span style="display: inline-block; padding: 8px 18px; background-color: #121526; color: #cbd5e1; border: 1px solid #202742; border-radius: 20px; font-size: 12px; font-weight: 500;">
                        📥 Get started - Install a model
                    </span>
                </a>
            </div>
        </div>
        """
        self.browser.setHtml(hero_html)

    def _handle_anchor_click(self, url):
        url_str = url.toString()
        if url_str == "#action:install_model":
            self.install_model_clicked.emit()

    def append_user_message(self, text: str):
        escaped_text = html.escape(text).replace("\n", "<br>")
        user_card = f"""
        <div style="margin: 20px 0 14px 0; text-align: right;">
            <div style="display: inline-block; text-align: left; max-width: 80%; background-color: #191f38; border: 1px solid #262f54; border-radius: 16px; padding: 12px 18px; color: #ffffff; font-size: 13.5px;">
                {escaped_text}
            </div>
        </div>
        """
        self.browser.append(user_card)
        self._scroll_to_bottom()

    def start_assistant_stream(self):
        self.raw_stream_markdown = ""
        agent_start = """
        <div style="margin: 16px 0 4px 0; color: #818cf8; font-size: 12px; font-weight: 600; letter-spacing: 0.3px;">
            🥔 Potato AI
        </div>
        """
        self.browser.append(agent_start)
        self._scroll_to_bottom()

    def append_stream_token(self, token: str):
        self.raw_stream_markdown += token
        cursor = self.browser.textCursor()
        cursor.movePosition(cursor.End)
        self.browser.setTextCursor(cursor)
        self.browser.insertPlainText(token)
        self._scroll_to_bottom()

    def finish_assistant_stream(self, full_markdown: str):
        formatted_html = self.markdown_to_html(full_markdown)
        agent_card = f"""
        <div style="margin: 4px 0 20px 0; color: #e2e8f0; font-size: 13.5px; line-height: 1.6;">
            {formatted_html}
        </div>
        """
        self.browser.append(agent_card)
        self._scroll_to_bottom()

    def append_tool_notice(self, tool_name: str, status: str):
        notice_html = f"""
        <div style="margin: 6px 0; font-size: 11px; font-family: monospace; color: #818cf8;">
            <span style="background-color: #13172a; border: 1px solid #1f2545; border-radius: 12px; padding: 3px 10px;">
                ⚙️ {html.escape(tool_name)} &bull; {html.escape(status)}
            </span>
        </div>
        """
        self.browser.append(notice_html)
        self._scroll_to_bottom()

    def clear(self):
        self.show_hero()

    def _scroll_to_bottom(self):
        sb = self.browser.verticalScrollBar()
        sb.setValue(sb.maximum())

    @staticmethod
    def markdown_to_html(text: str) -> str:
        """Lightweight parser for markdown to styled HTML."""
        if not text:
            return ""

        def code_block_sub(match):
            lang = (match.group(1) or "code").upper()
            code = match.group(2)
            escaped_code = html.escape(code)
            return f"""
            <div style="margin: 12px 0; background-color: #080a12; border: 1px solid #1b2038; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #101323; padding: 6px 14px; font-size: 10px; color: #818cf8; font-weight: bold; font-family: monospace; border-bottom: 1px solid #181d33;">
                    {lang}
                </div>
                <pre style="margin: 0; padding: 14px; color: #cbd5e1; font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12.5px; line-height: 1.5; white-space: pre-wrap;">{escaped_code}</pre>
            </div>
            """

        pattern = r"```([a-zA-Z0-9_\-\.]*)\n(.*?)```"
        processed = re.sub(pattern, code_block_sub, text, flags=re.DOTALL)
        processed = re.sub(r"`([^`]+)`", r"<code style='background-color: #14182b; color: #f43f5e; padding: 2px 6px; border-radius: 4px; font-family: Consolas;'>\1</code>", processed)
        processed = re.sub(r"\*\*([^*]+)\*\*", r"<b style='color:#ffffff;'>\1</b>", processed)
        processed = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", processed)
        processed = processed.replace("\n", "<br>")
        return processed
