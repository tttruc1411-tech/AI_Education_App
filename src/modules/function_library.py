# src/modules/function_library.py

import inspect
import importlib

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea,
    QPlainTextEdit, QSizePolicy,
)
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag, QFont, QColor

from .library.definitions import LIBRARY_FUNCTIONS


def _darken_hex(hex_color, factor=0.82):
    """Return a solid darker shade of a hex color (no alpha tricks)."""
    h = hex_color.lstrip("#")
    r = int(int(h[0:2], 16) * factor)
    g = int(int(h[2:4], 16) * factor)
    b = int(int(h[4:6], 16) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"



# ────────────────────────────────────────────────────────────
#  Inline Info Panel  —  simplified flat design
# ────────────────────────────────────────────────────────────

class FunctionInfoPanel(QFrame):
    """
    Expandable panel shown below the function block row.
    Flat design: Snippet → Parameters → Returns → Source Code.
    """

    def __init__(self, func_id, info, category_color):
        super().__init__()
        self.setObjectName("InfoPanel")
        self.setStyleSheet(f"""
            QFrame#InfoPanel {{
                background: #fafafa;
                border: 1px solid #e2e8f0;
                border-top: 2px solid {category_color};
                border-radius: 0 0 10px 10px;
                margin: 0 12px 6px 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)

        usage  = info.get("usage", "")
        params = info.get("params", [])
        returns = info.get("returns")

        # 1. Snippet (dragged)
        if usage:
            layout.addWidget(self._bold_label("Snippet (Dragged):"))
            # Estimate if content exceeds 1 row (contains newlines or long text that will wrap)
            lines_estimate = usage.count('\n') + 1 + (len(usage) // 50)
            h = 84 if lines_estimate > 1 else 42
            layout.addWidget(self._code_block(usage, height=h))

        # 2. Parameters
        if params:
            layout.addWidget(self._bold_label("Parameters:"))
            for p in params:
                name = p.get("name", "")
                ptype = p.get("type", "")
                desc  = p.get("desc", "")
                line = QLabel(f"  <b style='color:#7c3aed;'>{name}</b>"
                              f" <span style='color:#64748b;'>({ptype})</span>"
                              f" – {desc}")
                line.setWordWrap(True)
                line.setTextFormat(Qt.RichText)
                line.setStyleSheet(
                    "color: #334155; font-size: 16px; background: transparent;"
                )
                layout.addWidget(line)

        # 3. Returns
        if returns:
            layout.addWidget(self._bold_label("Returns:"))
            rtype = returns.get("type", "")
            rdesc = returns.get("desc", "")
            ret_line = QLabel(
                f"  <b style='color:#059669;'>{rtype}</b> – {rdesc}"
            )
            ret_line.setWordWrap(True)
            ret_line.setTextFormat(Qt.RichText)
            ret_line.setStyleSheet(
                "color: #334155; font-size: 16px; background: transparent;"
            )
            layout.addWidget(ret_line)

        # 4. Source Code
        layout.addWidget(self._bold_label("Source Code:"))
        source_text = self._load_source(info)
        if source_text:
            layout.addWidget(self._code_block(source_text, height=200, dark=True, font_size=7))
        else:
            no_src = QLabel("Source code not available.")
            no_src.setStyleSheet("color: #94a3b8; font-size: 13px; background: transparent;")
            layout.addWidget(no_src)

    # ── Helpers ────────────────────────────────────────────

    def _bold_label(self, text):
        lbl = QLabel(text)
        lbl.setWordWrap(True)  # CRITICAL: Prevent long bold strings from locking layout widths
        lbl.setStyleSheet(
            "color: #1e293b; font-size: 14px; font-weight: 700; background: transparent;"
        )
        return lbl

    def _code_block(self, text, height=42, dark=False, font_size=8):
        box = QPlainTextEdit(text)
        box.setReadOnly(True)
        box.setFont(QFont("JetBrains Mono, Consolas, Courier New", font_size))
        box.setFixedHeight(height)
        box.setMinimumWidth(50)  # Bypass NoWrap enforcing wide columns
        box.setLineWrapMode(
            QPlainTextEdit.NoWrap if dark
            else QPlainTextEdit.WidgetWidth
        )
        if dark:
            box.setStyleSheet("""
                QPlainTextEdit {
                    background: #0f172a;
                    color: #e2e8f0;
                    border: 1px solid #1e293b;
                    border-radius: 6px;
                    padding: 8px;
                    selection-background-color: #3b82f6;
                }
                QScrollBar:vertical { background:#1e293b; width:5px; border-radius:3px; }
                QScrollBar::handle:vertical { background:#334155; border-radius:3px; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
            """)
        else:
            box.setStyleSheet("""
                QPlainTextEdit {
                    background: #ede9fe;
                    color: #5b21b6;
                    border: 1px solid #ddd6fe;
                    border-radius: 6px;
                    padding: 6px 10px;
                }
            """)
        return box

    def _load_source(self, info):
        module_path = info.get("source_module")
        func_name   = info.get("source_func")
        if not module_path or not func_name:
            return None
        try:
            mod  = importlib.import_module(module_path)
            func = getattr(mod, func_name)
            return inspect.getsource(func)
        except Exception:
            return None


# ────────────────────────────────────────────────────────────
#  Toggle Arrow  —  gray, direction-only, darker bg on hover
# ────────────────────────────────────────────────────────────

class ToggleLabel(QLabel):
    """
    A QLabel arrow toggle (▼ / ▲).
    Gray at rest; slightly darker background on hover.
    Uses enterEvent/leaveEvent to avoid Qt platform hover override.
    """
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("▼", parent)
        self.setFixedSize(26, 26)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Show / hide details")
        self._expanded = False
        self._refresh(hovered=False)

    def set_expanded(self, expanded):
        self._expanded = expanded
        self.setText("▲" if expanded else "▼")
        self._refresh(hovered=False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self._refresh(hovered=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._refresh(hovered=False)
        super().leaveEvent(event)

    def _refresh(self, hovered):
        bg = "rgba(0,0,0,0.10)" if hovered else "transparent"
        self.setStyleSheet(f"""
            background: {bg};
            color: #94a3b8;
            border-radius: 5px;
            font-size: 11px;
        """)


# ────────────────────────────────────────────────────────────
#  Draggable Function Block  (header row + dropdown)
# ────────────────────────────────────────────────────────────

class DraggableFunctionBlock(QFrame):
    expandRequested = pyqtSignal(object)

    def __init__(self, func_id, info, category_color, category_icon="🌣"):
        super().__init__()
        self.func_id        = func_id
        self.info           = info
        self.category_color = category_color
        self.category_icon  = category_icon
        self._expanded      = False

        self.setObjectName("FunctionCard")
        self.setStyleSheet("""
            QFrame#FunctionCard { background: transparent; margin: 2px 8px; }
        """)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        # ── Header row ──────────────────────────────────────
        self._header = QFrame()
        self._header.setObjectName("FunctionBlock")
        self._set_header_style(expanded=False)
        self._header.setCursor(Qt.PointingHandCursor)

        row = QHBoxLayout(self._header)
        row.setContentsMargins(10, 12, 10, 12)
        row.setSpacing(8)
        row.setAlignment(Qt.AlignTop)

        # Icon badge
        icon_lbl = QLabel(self.category_icon)
        icon_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background-color: {category_color};
            color: #ffffff;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
        """)
        row.addWidget(icon_lbl, 0, Qt.AlignTop)

        # Name + desc
        text_box = QVBoxLayout()
        text_box.setSpacing(1)
        name_lbl = QLabel(func_id)
        name_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        name_lbl.setStyleSheet(
            "font-weight: 700; color: #1e293b; font-size: 16px; background: transparent;"
        )
        short_desc = QLabel(info.get("desc", ""))
        short_desc.setAttribute(Qt.WA_TransparentForMouseEvents)
        short_desc.setStyleSheet(
            "color: #94a3b8; font-size: 14px; background: transparent;"
        )
        short_desc.setWordWrap(True)
        text_box.addWidget(name_lbl)
        text_box.addWidget(short_desc)
        row.addLayout(text_box, stretch=1)

        self._arrow = ToggleLabel()
        self._arrow.setAttribute(Qt.WA_TransparentForMouseEvents)
        row.addWidget(self._arrow, 0, Qt.AlignTop)

        # 🖱️ Make the whole header clickable for smooth interaction
        self._header.mousePressEvent = self._on_header_pressed
        self._header.mouseReleaseEvent = self._on_header_released

        self._root.addWidget(self._header)

        # ── Info panel (hidden) ──────────────────────────────
        self._panel = FunctionInfoPanel(func_id, info, category_color)
        self._panel.setVisible(False)
        self._root.addWidget(self._panel)

    def _on_header_pressed(self, event):
        self._drag_start_pos = event.pos()

    def _on_header_released(self, event):
        if hasattr(self, '_drag_start_pos'):
            # Only toggle if the mouse didn't move much (distinguishing click from drag)
            if (event.pos() - self._drag_start_pos).manhattanLength() < 5:
                self._toggle()

    # ── Toggle ──────────────────────────────────────────────

    def collapse(self):
        """Force-close this block if it's expanded."""
        if self._expanded:
            self._expanded = False
            self._panel.setVisible(False)
            self._arrow.set_expanded(False)
            self._set_header_style(False)

    def _toggle(self):
        # If we are about to expand, notify others to collapse
        if not self._expanded:
            self.expandRequested.emit(self)

        self._expanded = not self._expanded
        self._panel.setVisible(self._expanded)
        self._arrow.set_expanded(self._expanded)
        self._set_header_style(self._expanded)

    def _set_header_style(self, expanded):
        c = self.category_color
        if expanded:
            self._header.setStyleSheet(f"""
                QFrame#FunctionBlock {{
                    background: white;
                    border: 1px solid {c};
                    border-bottom: none;
                    border-radius: 10px 10px 0 0;
                }}
            """)
        else:
            self._header.setStyleSheet("""
                QFrame#FunctionBlock {
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                }
                QFrame#FunctionBlock:hover {
                    border-color: #c4b5fd;
                    background: #f3f0ff;
                }
            """)

    # ── Drag ────────────────────────────────────────────────

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.func_id)
        drag.setMimeData(mime)
        drag.setPixmap(self._header.grab())
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.CopyAction)


# ────────────────────────────────────────────────────────────
#  Category Header
# ────────────────────────────────────────────────────────────

class CategoryHeader(QPushButton):
    def __init__(self, title, count, color, icon="📂"):
        super().__init__()
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedHeight(52)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                padding-right: 0px;
                margin: 4px 8px 2px 8px;
            }}
            QPushButton:hover {{ background-color: {_darken_hex(color)}; }}
            QPushButton:checked:hover {{ background-color: {_darken_hex(color)}; }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 4, 0)
        layout.setSpacing(12)

        # 🚀 Icon Block (Left Side Tab)
        icon_box = QLabel(icon)
        icon_box.setFixedSize(50, 52)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setStyleSheet(f"""
            background: rgba(0, 0, 0, 0); 
            border-top-left-radius: 8px; 
            border-bottom-left-radius: 8px;
            font-size: 24px;
        """)
        icon_box.setAttribute(Qt.WA_TransparentForMouseEvents)

        # 🏞️ Title Label
        title_lbl = QLabel(title)
        title_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        title_lbl.setStyleSheet(
            "color: white; background: transparent; font-weight: 900; font-size: 18px; letter-spacing: 1px;"
        )
        title_lbl.setAlignment(Qt.AlignVCenter)

        # Count badge
        count_lbl = QLabel(str(count))
        count_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        count_lbl.setStyleSheet("""
            background: rgba(255,255,255,0.25);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        """)

        layout.addWidget(icon_box)
        layout.addWidget(title_lbl)
        layout.addStretch()
        layout.addWidget(count_lbl)


# ────────────────────────────────────────────────────────────
#  Populate the Functions Tab
# ────────────────────────────────────────────────────────────

def populate_functions_tab(running_mode_widget):
    layout = running_mode_widget.findChild(QVBoxLayout, "functionsListLayout")

    # Remove all existing items (widgets + spacers)
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().setParent(None)

    # Pin content to top — critical so collapsed headers sit at top, not center
    layout.setAlignment(Qt.AlignTop)

    # 🤝 ACCORDION MANAGERS
    all_blocks = []
    all_category_containers = []
    all_category_buttons = []

    def collapse_all_blocks(except_block):
        for block in all_blocks:
            if block != except_block:
                block.collapse()

    def on_category_clicked(checked, clicked_header, clicked_container):
        if checked:
            # 1. Collapse all other categories
            for btn, cont in zip(all_category_buttons, all_category_containers):
                if btn != clicked_header:
                    btn.setChecked(False)
                    cont.setVisible(False)
            # 2. Collapse all function blocks for a fresh start
            collapse_all_blocks(None)
            clicked_container.setVisible(True)
        else:
            clicked_container.setVisible(False)

    for cat_name, cat_data in LIBRARY_FUNCTIONS.items():
        color = cat_data["color"]
        icon  = cat_data.get("icon", "📂")
        count = len(cat_data["functions"])

        header = CategoryHeader(cat_name, count, color, icon=icon)
        layout.addWidget(header)
        all_category_buttons.append(header)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 2, 0, 6)
        container_layout.setSpacing(4)
        all_category_containers.append(container)

        header.clicked.connect(lambda chk, h=header, c=container: on_category_clicked(chk, h, c))

        for func_id, info in cat_data["functions"].items():
            block = DraggableFunctionBlock(
                func_id=func_id,
                info=info,
                category_color=color,
                category_icon=icon
            )
            all_blocks.append(block)
            block.expandRequested.connect(collapse_all_blocks)
            container_layout.addWidget(block)

        container.setVisible(False)
        layout.addWidget(container)