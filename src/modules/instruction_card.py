"""
Floating Instruction Card Widget for AI Coding Lab.
Displays paginated tutorial instructions as a modern card overlay on the editor.
"""

import os
import re
from PyQt5.QtWidgets import (
    QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect, QWidget, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QColor, QFont


# Gradient color rotation for pages
GRADIENT_COLORS = [
    ("#10b981", "#059669"),  # Green
    ("#06b6d4", "#0891b2"),  # Cyan
    ("#8b5cf6", "#7c3aed"),  # Purple
    ("#f59e0b", "#d97706"),  # Amber
]

# Icon mapping for page titles
ICON_MAP = {
    "task": "⚡",
    "nhiệm vụ": "⚡",
    "instructions": "📋",
    "hướng dẫn": "📋",
    "required functions": "🧩",
    "functions cần dùng": "🧩",
    "functions": "🧩",
    "hints": "💡",
    "tips": "💡",
    "gợi ý": "💡",
}


def _get_icon_for_title(title: str) -> str:
    """Return an emoji icon based on the page title."""
    title_lower = title.lower().strip()
    for key, icon in ICON_MAP.items():
        if key in title_lower:
            return icon
    return "📖"


def _strip_markdown(text: str) -> str:
    """Strip basic markdown formatting for plain display."""
    # Remove inline code backticks but keep content
    text = re.sub(r'`([^`]*)`', r'\1', text)
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]*)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]*)\*', r'\1', text)
    # Remove link syntax [text](url) -> text
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    return text.strip()


class FloatingInstructionCard(QFrame):
    """A floating paginated card that shows tutorial instructions over the editor."""

    def __init__(self, parent=None, is_small=False):
        super().__init__(parent)
        self._is_small = is_small
        self._pages = []  # List of dicts: {title, body, icon, gradient}
        self._current_page = 0
        self._card_visible = False

        self.setObjectName("floatingInstructionCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Card sizing
        self._update_size()

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        # Build UI
        self._build_ui()

        # Initially hidden
        self.hide()

    def _update_size(self):
        """Set card dimensions based on mode."""
        if self._is_small:
            self._card_w = 280
            self._card_h = 160
        else:
            self._card_w = 350
            self._card_h = 220
        self.setFixedSize(self._card_w, self._card_h)

    def _build_ui(self):
        """Construct the card layout."""
        # Main layout - no margins, we handle positioning manually
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header area (top ~40%) ---
        self._header = QFrame()
        self._header.setObjectName("cardHeader")
        self._header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        header_layout = QVBoxLayout(self._header)
        header_layout.setContentsMargins(16, 10, 12, 8)
        header_layout.setSpacing(0)

        # Single row: Icon + Title + Close button
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        self._lbl_icon = QLabel("📋")
        self._lbl_icon.setStyleSheet("font-size: 20px; background: transparent;")
        title_row.addWidget(self._lbl_icon)

        self._lbl_title = QLabel("Instructions")
        self._lbl_title.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        self._lbl_title.setWordWrap(True)
        title_row.addWidget(self._lbl_title, 1)

        self._btn_close = QPushButton("✕")
        self._btn_close.setFixedSize(24, 24)
        self._btn_close.setCursor(Qt.PointingHandCursor)
        self._btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.4);
            }
        """)
        self._btn_close.clicked.connect(self.hide_card)
        title_row.addWidget(self._btn_close)
        header_layout.addLayout(title_row)
        header_layout.addStretch()

        main_layout.addWidget(self._header, 25)

        # --- Body area (bottom ~60%) ---
        self._body = QFrame()
        self._body.setObjectName("cardBody")
        self._body.setStyleSheet("""
            QFrame#cardBody {
                background: white;
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
            }
        """)
        body_layout = QVBoxLayout(self._body)
        body_layout.setContentsMargins(16, 10, 16, 8)
        body_layout.setSpacing(4)

        # Description text
        self._lbl_body = QLabel("Select a lesson to begin.")
        self._lbl_body.setWordWrap(True)
        self._lbl_body.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._lbl_body.setStyleSheet("""
            font-size: 13px;
            color: #374151;
            background: transparent;
            line-height: 1.4;
        """)
        self._lbl_body.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_layout.addWidget(self._lbl_body, 1)

        # Bottom bar: dots (left) + nav buttons (right)
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 4, 0, 0)
        bottom_bar.setSpacing(4)

        # Page dots container
        self._dots_container = QWidget()
        self._dots_layout = QHBoxLayout(self._dots_container)
        self._dots_layout.setContentsMargins(0, 0, 0, 0)
        self._dots_layout.setSpacing(4)
        bottom_bar.addWidget(self._dots_container)

        bottom_bar.addStretch()

        # Navigation buttons
        self._btn_prev = QPushButton("←")
        self._btn_prev.setFixedSize(28, 28)
        self._btn_prev.setCursor(Qt.PointingHandCursor)
        self._btn_prev.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e5e7eb;
                border-color: #9ca3af;
            }
            QPushButton:disabled {
                color: #d1d5db;
                border-color: #e5e7eb;
            }
        """)
        self._btn_prev.clicked.connect(self._prev_page)
        bottom_bar.addWidget(self._btn_prev)

        self._btn_next = QPushButton("→")
        self._btn_next.setFixedSize(28, 28)
        self._btn_next.setCursor(Qt.PointingHandCursor)
        self._btn_next.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e5e7eb;
                border-color: #9ca3af;
            }
            QPushButton:disabled {
                color: #d1d5db;
                border-color: #e5e7eb;
            }
        """)
        self._btn_next.clicked.connect(self._next_page)
        bottom_bar.addWidget(self._btn_next)

        body_layout.addLayout(bottom_bar)

        main_layout.addWidget(self._body, 75)

        # Apply rounded corners to the whole card
        self.setStyleSheet("""
            QFrame#floatingInstructionCard {
                border-radius: 16px;
                background: transparent;
            }
        """)

    def load_tutorial(self, file_path: str):
        """Parse tutorial markdown and set up pages."""
        self._pages = []
        self._current_page = 0

        if not os.path.exists(file_path):
            self._pages = [{
                "title": "Not Found",
                "body": f"Tutorial file not found.",
                "icon": "❌",
                "gradient": GRADIENT_COLORS[0]
            }]
            self._update_display()
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self._pages = [{
                "title": "Error",
                "body": str(e),
                "icon": "❌",
                "gradient": GRADIENT_COLORS[0]
            }]
            self._update_display()
            return

        # Split by ## headers
        sections = re.split(r'^## ', content, flags=re.MULTILINE)

        # First section might contain the # Title line — skip it
        for section in sections[1:]:  # Skip the first split (before first ##)
            lines = section.strip().split('\n', 1)
            title = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""

            # Strip markdown formatting from body
            body = _strip_markdown(body)

            # Get icon and gradient
            icon = _get_icon_for_title(title)
            gradient_idx = len(self._pages) % len(GRADIENT_COLORS)
            gradient = GRADIENT_COLORS[gradient_idx]

            self._pages.append({
                "title": title,
                "body": body,
                "icon": icon,
                "gradient": gradient
            })

        if not self._pages:
            self._pages = [{
                "title": "Empty",
                "body": "No instructions found.",
                "icon": "📖",
                "gradient": GRADIENT_COLORS[0]
            }]

        self._current_page = 0
        self._update_display()

    def show_card(self):
        """Show the card, positioned at top-right of parent."""
        self._card_visible = True
        self._position_card()
        self.show()
        self.raise_()
        # Install event filter on parent to track resizes
        if self.parent():
            self.parent().installEventFilter(self)

    def hide_card(self):
        """Hide the card."""
        self._card_visible = False
        self.hide()
        # Remove event filter
        if self.parent():
            self.parent().removeEventFilter(self)

    def set_small_mode(self, is_small: bool):
        """Update sizing for resolution mode."""
        self._is_small = is_small
        self._update_size()
        self._update_styles()
        if self._card_visible:
            self._position_card()

    def _position_card(self):
        """Position the card at the top-right of the parent widget."""
        if self.parent():
            parent_w = self.parent().width()
            margin = 10
            x = parent_w - self._card_w - margin
            y = margin
            self.move(max(0, x), y)

    def _next_page(self):
        """Go to next page."""
        if self._current_page < len(self._pages) - 1:
            self._current_page += 1
            self._update_display()

    def _prev_page(self):
        """Go to previous page."""
        if self._current_page > 0:
            self._current_page -= 1
            self._update_display()

    def _update_display(self):
        """Refresh the card content for current page."""
        if not self._pages:
            return

        page = self._pages[self._current_page]

        # Update header gradient
        c1, c2 = page["gradient"]
        self._header.setStyleSheet(f"""
            QFrame#cardHeader {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {c1}, stop:1 {c2});
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }}
        """)

        # Update icon and title
        self._lbl_icon.setText(page["icon"])
        self._lbl_title.setText(page["title"])

        # Update body text (truncate if too long for the card)
        body_text = page["body"]
        max_chars = 180 if self._is_small else 250
        if len(body_text) > max_chars:
            body_text = body_text[:max_chars] + "..."
        self._lbl_body.setText(body_text)

        # Update navigation buttons
        self._btn_prev.setEnabled(self._current_page > 0)
        self._btn_next.setEnabled(self._current_page < len(self._pages) - 1)

        # Update page dots
        self._update_dots()

    def _update_dots(self):
        """Rebuild page indicator dots."""
        # Clear existing dots
        while self._dots_layout.count():
            item = self._dots_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i in range(len(self._pages)):
            dot = QLabel()
            dot.setFixedSize(8, 8)
            if i == self._current_page:
                dot.setStyleSheet("""
                    background: #8b5cf6;
                    border-radius: 4px;
                """)
            else:
                dot.setStyleSheet("""
                    background: #d1d5db;
                    border-radius: 4px;
                """)
            self._dots_layout.addWidget(dot)

    def _update_styles(self):
        """Update font sizes and dimensions for current mode."""
        if self._is_small:
            title_fs = 12
            icon_fs = 16
            body_fs = 9
            btn_sz = 22
            btn_fs = 11
            close_sz = 20
            close_fs = 11
            h_margin = (12, 8, 12, 6)
            b_margin = (12, 8, 12, 6)
        else:
            title_fs = 15
            icon_fs = 20
            body_fs = 13
            btn_sz = 28
            btn_fs = 14
            close_sz = 24
            close_fs = 14
            h_margin = (16, 12, 16, 8)
            b_margin = (16, 10, 16, 8)

        self._lbl_icon.setStyleSheet(f"font-size: {icon_fs}px; background: transparent;")
        self._lbl_title.setStyleSheet(f"""
            font-size: {title_fs}px;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        self._lbl_body.setStyleSheet(f"""
            font-size: {body_fs}px;
            color: #374151;
            background: transparent;
            line-height: 1.4;
        """)

        self._btn_close.setFixedSize(close_sz, close_sz)
        self._btn_close.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: {close_sz // 2}px;
                font-size: {close_fs}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.4);
            }}
        """)

        nav_style = f"""
            QPushButton {{
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: {btn_fs}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #e5e7eb;
                border-color: #9ca3af;
            }}
            QPushButton:disabled {{
                color: #d1d5db;
                border-color: #e5e7eb;
            }}
        """
        self._btn_prev.setFixedSize(btn_sz, btn_sz)
        self._btn_prev.setStyleSheet(nav_style)
        self._btn_next.setFixedSize(btn_sz, btn_sz)
        self._btn_next.setStyleSheet(nav_style)

        # Update layout margins
        self._header.layout().setContentsMargins(*h_margin)
        self._body.layout().setContentsMargins(*b_margin)

    def eventFilter(self, obj, event):
        """Track parent resize to reposition the card."""
        if obj == self.parent() and event.type() == QEvent.Resize:
            if self._card_visible:
                self._position_card()
        return super().eventFilter(obj, event)
