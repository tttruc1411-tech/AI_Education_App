# AI Code Lab — Assistant Chat Panel (PyQt5)

from __future__ import annotations
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QSizePolicy, QScrollArea, QComboBox,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush


# ── Custom-painted bubble container ───────────────────────────────────────────

class _BubbleBox(QWidget):
    """
    Widget that paints its own rounded-rect background via QPainter.
    This CANNOT be overridden by any Qt stylesheet cascade — it bypasses
    the stylesheet system entirely.
    """

    def __init__(self, bg_hex: str, border_hex=None, parent=None):
        super().__init__(parent)
        self._bg = QColor(bg_hex)
        self._border = QColor(border_hex) if border_hex else None
        # Prevent Qt from painting the default white background
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setStyleSheet("background: transparent; border: none;")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        if self._border:
            p.setPen(QPen(self._border, 1.0))
        else:
            p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self._bg))
        p.drawRoundedRect(rect, 8, 8)
        p.end()


# ── Bubble widget ─────────────────────────────────────────────────────────────

class MessageBubble(QFrame):
    """
    Chat bubble that is completely immune to Qt stylesheet cascading.

    • Background colour: painted via QPainter (no stylesheet can override this)
    • Text colour: forced via inline HTML ``<span style="color:…">``
      (no stylesheet can override inline rich-text attributes)
    """

    def __init__(self, text: str, is_user: bool, is_small: bool = False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self._full_text = text
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("background: transparent; border: none;")

        fs = 11 if is_small else 13

        if is_user:
            bg, fg, border_hex = "#6d28d9", "#ffffff", None
        else:
            bg, fg, border_hex = "#1e293b", "#e2e8f0", "#334155"

        self._fg = fg  # stored for _render_html()

        # ── Custom-painted bubble container ──
        self._bubble_box = _BubbleBox(bg, border_hex)
        box_layout = QVBoxLayout(self._bubble_box)
        box_layout.setContentsMargins(8, 5, 8, 5)
        box_layout.setSpacing(0)

        # ── QLabel — RichText with inline color ──
        self._label = QLabel("")
        self._label.setWordWrap(True)
        self._label.setTextFormat(Qt.RichText)
        self._label.setFont(QFont("Segoe UI", fs))
        self._label.setMinimumHeight(20)
        self._label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.MinimumExpanding)
        self._label.setMinimumWidth(50)
        
        # Enable text selection
        self._label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        self._label.setCursor(Qt.IBeamCursor)

        self._label.setStyleSheet(
            "background: transparent; border: none; padding: 0px;"
        )
        box_layout.addWidget(self._label)

        # ── Outer layout (alignment spacing) ──
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 2, 0, 2)
        outer.setSpacing(0)
        if is_user:
            outer.addSpacing(36)
            outer.addWidget(self._bubble_box, stretch=1)
        else:
            outer.addWidget(self._bubble_box, stretch=1)
            outer.addSpacing(36)

        if text:
            self._render_html()

    # ── Internal: build inline-colored HTML ──────────────────────────────
    def _render_html(self):
        import html as _html
        escaped = _html.escape(self._full_text).replace("\n", "<br>")
        self._label.setText(
            f'<span style="color:{self._fg};">{escaped}</span>'
        )

    def append_token(self, token: str):
        self._full_text += token
        self._render_html()

    def set_text(self, text: str):
        self._full_text = text
        self._render_html()


# ── Main chat panel ────────────────────────────────────────────────────────────

class AssistantChatPanel(QWidget):
    ask_requested     = pyqtSignal(str)
    fix_requested     = pyqtSignal()
    explain_requested = pyqtSignal()
    close_requested   = pyqtSignal()
    model_changed     = pyqtSignal(str)   # emits model key e.g. "qwen", "phi3"

    # ── Thread-safe signals (emit from ANY thread → delivered on GUI thread) ──
    _token_received   = pyqtSignal(str)
    _streaming_done   = pyqtSignal()
    _error_received   = pyqtSignal(str)
    _fix_done         = pyqtSignal(str)   # post-processed fix text → replace bubble on GUI thread

    def __init__(self, parent=None, is_small: bool = False):
        super().__init__(parent)
        self.is_small = is_small
        self._streaming_bubble = None
        self._token_count = 0
        self._dot_count = 0
        self._setup_ui()
        self.hide()

        # Premium Fade-in Animation using QGraphicsOpacityEffect
        # (windowOpacity only works on top-level windows, not child widgets)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_anim.setDuration(250)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Connect thread-safe signals to their handlers
        self._token_received.connect(self._on_token_signal)
        self._streaming_done.connect(self.finish_streaming)
        self._error_received.connect(self.show_error)
        self._fix_done.connect(self._on_fix_done)

    def _setup_ui(self):
        self.setObjectName("assistantPanel")
        w = 370 if not self.is_small else 300
        self.setFixedWidth(w)
        self.setMinimumHeight(420 if not self.is_small else 320)
        self.setMaximumHeight(600 if not self.is_small else 420)

        # Panel background
        self.setStyleSheet("""
            QWidget#assistantPanel {
                background-color: #0f172a;
                border: 1px solid #7c3aed;
                border-radius: 16px;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ─────────────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(44 if not self.is_small else 36)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #7c3aed, stop:0.6 #6d28d9, stop:1 #3b82f6);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 8, 0)

        fs_h = 12 if not self.is_small else 10

        icon_lbl = QLabel("🤖")
        icon_lbl.setFont(QFont("Segoe UI", 15 if not self.is_small else 12))
        icon_lbl.setStyleSheet("background: transparent; color: white;")

        title_lbl = QLabel("AI Assistant")
        self._title_lbl = title_lbl
        title_lbl.setFont(QFont("Segoe UI", fs_h + 1, QFont.Bold))
        title_lbl.setStyleSheet("background: transparent; color: white;")

        self._status_dot = QLabel("●")
        self._status_dot.setFont(QFont("Segoe UI", 8))
        self._status_dot.setStyleSheet("background: transparent; color: #6b7280;")

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(22, 22)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { background: transparent; color: rgba(255,255,255,0.7);
                border: none; font-size: 12px; border-radius: 11px; }
            QPushButton:hover { background: rgba(255,255,255,0.15); color: white; }
        """)
        btn_close.clicked.connect(self.close_requested)

        h_layout.addWidget(icon_lbl)
        h_layout.addSpacing(4)
        h_layout.addWidget(title_lbl)
        h_layout.addStretch()
        h_layout.addWidget(self._status_dot)
        h_layout.addSpacing(4)
        h_layout.addWidget(btn_close)
        root.addWidget(header)

        # ── Model selector row ─────────────────────────────────────────────────
        model_frame = QFrame()
        model_frame.setStyleSheet("QFrame { background: #1e293b; border: none; }")
        model_layout = QHBoxLayout(model_frame)
        model_layout.setContentsMargins(8, 4, 8, 4)
        model_layout.setSpacing(6)

        fs_m = 10 if not self.is_small else 8
        model_label = QLabel("Model:")
        model_label.setFont(QFont("Segoe UI", fs_m))
        model_label.setStyleSheet("color: #94a3b8; background: transparent;")

        self._model_combo = QComboBox()
        self._model_combo.setFont(QFont("Segoe UI", fs_m))
        self._model_combo.setFixedHeight(26 if not self.is_small else 22)
        self._model_combo.setCursor(Qt.PointingHandCursor)
        self._model_combo.setStyleSheet("""
            QComboBox {
                background: #0f172a; color: #e2e8f0;
                border: 1px solid #334155; border-radius: 6px;
                padding: 1px 6px;
            }
            QComboBox:hover { border: 1px solid #7c3aed; }
            QComboBox::drop-down {
                border: none; width: 16px;
            }
            QComboBox::down-arrow {
                image: none; border: none;
            }
            QComboBox QAbstractItemView {
                background: #1e293b; color: #e2e8f0;
                border: 1px solid #334155; selection-background-color: #7c3aed;
            }
        """)
        self._model_combo.currentIndexChanged.connect(self._on_model_combo_changed)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self._model_combo, 1)
        root.addWidget(model_frame)

        # ── Quick action buttons ───────────────────────────────────────────────
        qa_frame = QFrame()
        qa_frame.setStyleSheet("QFrame { background: #1e293b; border: none; }")
        qa_layout = QHBoxLayout(qa_frame)
        qa_layout.setContentsMargins(8, 5, 8, 5)
        qa_layout.setSpacing(6)

        fs_qa = 10 if not self.is_small else 8
        self._btn_fix     = self._qa_btn("🔧 Fix Error", "#ef4444", fs_qa)
        self._btn_explain = self._qa_btn("💡 Explain",   "#f59e0b", fs_qa)
        self._btn_fix.clicked.connect(self.fix_requested)
        self._btn_explain.clicked.connect(self.explain_requested)
        qa_layout.addWidget(self._btn_fix)
        qa_layout.addWidget(self._btn_explain)
        root.addWidget(qa_frame)

        # ── Chat scroll area ───────────────────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("""
            QScrollArea { border: none; background: #0f172a; }
            QScrollBar:vertical { width: 4px; background: transparent; }
            QScrollBar::handle:vertical { background: #334155; border-radius: 2px; }
        """)

        self._chat_container = QWidget()
        self._chat_container.setObjectName("chatContainer")
        self._chat_container.setStyleSheet(
            "QWidget#chatContainer { background-color: #0f172a; }"
        )

        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(8, 6, 8, 6)
        self._chat_layout.setSpacing(4)
        self._chat_layout.addStretch()

        self._scroll.setWidget(self._chat_container)
        root.addWidget(self._scroll, 1)

        # ── Thinking indicator ─────────────────────────────────────────────────
        self._thinking_lbl = QLabel("● thinking")
        self._thinking_lbl.setFont(QFont("Segoe UI", 11))
        self._thinking_lbl.setStyleSheet(
            "color: #8b5cf6; padding: 2px 10px; background: #0f172a;"
        )
        self._thinking_lbl.hide()
        root.addWidget(self._thinking_lbl)

        self._dot_timer = QTimer(self)
        self._dot_timer.setInterval(400)
        self._dot_timer.timeout.connect(self._animate_dots)

        # ── Input row ──────────────────────────────────────────────────────────
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border-top: 1px solid #334155;
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
            }
        """)
        in_layout = QHBoxLayout(input_frame)
        in_layout.setContentsMargins(8, 5, 8, 5)
        in_layout.setSpacing(5)

        fs_in = 11 if not self.is_small else 9
        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask about your code...")
        self._input.setFont(QFont("Segoe UI", fs_in))
        self._input.setFixedHeight(32 if not self.is_small else 26)
        self._input.setStyleSheet("""
            QLineEdit { background: #0f172a; color: #e2e8f0;
                border: 1px solid #334155; border-radius: 10px; padding: 3px 8px; }
            QLineEdit:focus { border: 1px solid #7c3aed; }
        """)
        self._input.returnPressed.connect(self._on_send)

        btn_send = QPushButton("➤")
        btn_send.setFixedSize(28, 28)
        btn_send.setCursor(Qt.PointingHandCursor)
        btn_send.setFont(QFont("Segoe UI", 11))
        btn_send.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #7c3aed, stop:1 #3b82f6);
                color: white; border: none; border-radius: 14px; }
            QPushButton:hover { background: #8b5cf6; }
            QPushButton:pressed { background: #6d28d9; }
        """)
        btn_send.clicked.connect(self._on_send)

        in_layout.addWidget(self._input)
        in_layout.addWidget(btn_send)
        root.addWidget(input_frame)

    def show_animated(self, pos=None):
        """Show the panel with a smooth fade-in animation."""
        if pos:
            self.move(pos)
        
        # Ensure it's not already showing (prevents animation flicker)
        if self.isVisible() and self._opacity_effect.opacity() >= 0.99:
            return

        self._opacity_effect.setOpacity(0.0)
        self.show()
        self.raise_()
        self._fade_anim.start()

    def _qa_btn(self, text: str, color: str, fs: int) -> QPushButton:
        h = color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", fs, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{ background: rgba({r},{g},{b},40); color: {color};
                border: 1px solid {color}; border-radius: 7px;
                padding: 3px 6px; }}
            QPushButton:hover {{ background: rgba({r},{g},{b},80); }}
            QPushButton:disabled {{ opacity: 0.4; }}
        """)
        return btn

    # ── Public API ─────────────────────────────────────────────────────────────

    def set_status(self, state: str):
        colors = {"loading": "#f59e0b", "ready": "#22c55e",
                  "thinking": "#8b5cf6", "error": "#ef4444"}
        self._status_dot.setStyleSheet(
            f"background: transparent; color: {colors.get(state, '#6b7280')};"
        )
        is_thinking = (state == "thinking")
        self._thinking_lbl.setVisible(is_thinking)
        if is_thinking:
            self._dot_count = 0
            self._dot_timer.start()
        else:
            self._dot_timer.stop()
        self._btn_fix.setEnabled(state == "ready")
        self._btn_explain.setEnabled(state == "ready")
        self._input.setEnabled(state in ("ready", "thinking"))
        self._model_combo.setEnabled(state == "ready")

    def _animate_dots(self):
        self._dot_count = (self._dot_count + 1) % 4
        self._thinking_lbl.setText(f"● thinking{'.' * self._dot_count}")

    def add_user_message(self, text: str):
        if not text:
            return
        bubble = MessageBubble(text, is_user=True, is_small=self.is_small)
        self._insert_bubble(bubble)

    def start_assistant_message(self) -> MessageBubble:
        bubble = MessageBubble("", is_user=False, is_small=self.is_small)
        self._insert_bubble(bubble)
        self._streaming_bubble = bubble
        return bubble

    def append_token(self, token: str):
        if self._streaming_bubble:
            self._streaming_bubble.append_token(token)
            self._token_count += 1
            if self._token_count % 5 == 0:
                self._scroll_to_bottom()

    def _on_token_signal(self, token: str):
        """Slot for _token_received signal — guaranteed to run on GUI thread."""
        self.append_token(token)

    def _on_fix_done(self, text: str):
        """Slot for _fix_done signal — replaces bubble text on GUI thread, then finishes."""
        try:
            if self._streaming_bubble and text:
                self._streaming_bubble.set_text(text)
        except RuntimeError:
            pass  # bubble widget was already destroyed
        self.finish_streaming()

    def finish_streaming(self):
        self._streaming_bubble = None
        self._token_count = 0
        self._scroll_to_bottom()
        self.set_status("ready")

    def show_error(self, msg: str):
        b = MessageBubble(f"⚠️ {msg}", is_user=False, is_small=self.is_small)
        self._insert_bubble(b)
        self.set_status("ready")

    def show_loading_message(self, msg: str = "Loading model..."):
        b = MessageBubble(f"⏳ {msg}", is_user=False, is_small=self.is_small)
        self._insert_bubble(b)

    def set_small_mode(self, is_small: bool):
        self.is_small = is_small
        self.setFixedWidth(300 if is_small else 370)
        self.setMinimumHeight(320 if is_small else 420)
        self.setMaximumHeight(420 if is_small else 600)

    def retranslate(self, strings: dict):
        """Update all UI text from the translation dictionary."""
        self._title_lbl.setText(strings.get("BOT_TITLE", "AI Assistant"))
        self._btn_fix.setText(strings.get("BOT_FIX_BTN", "🔧 Fix Error"))
        self._btn_explain.setText(strings.get("BOT_EXPLAIN_BTN", "💡 Explain"))
        self._input.setPlaceholderText(strings.get("BOT_INPUT_HINT", "Ask about your code..."))

    # ── Model selector ─────────────────────────────────────────────────────────

    def populate_models(self, models: list, active_key: str = ""):
        """
        Populate the model combobox.
        models: list of (key, display_name, is_available) from get_available_models()
        active_key: the currently active model key to pre-select
        """
        self._model_combo.blockSignals(True)
        self._model_combo.clear()
        for key, name, available in models:
            label = name if available else f"{name} (not found)"
            self._model_combo.addItem(label, key)
            idx = self._model_combo.count() - 1
            if not available:
                # Grey out unavailable models
                self._model_combo.model().item(idx).setEnabled(False)
        # Select the active model
        for i in range(self._model_combo.count()):
            if self._model_combo.itemData(i) == active_key:
                self._model_combo.setCurrentIndex(i)
                break
        self._model_combo.blockSignals(False)

    def set_model_combo_enabled(self, enabled: bool):
        """Disable combo during loading/inference, enable when ready."""
        self._model_combo.setEnabled(enabled)

    def _on_model_combo_changed(self, index: int):
        key = self._model_combo.itemData(index)
        if key:
            self.model_changed.emit(key)
    # ── Internal ───────────────────────────────────────────────────────────────

    def _on_send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self.ask_requested.emit(text)

    def _insert_bubble(self, bubble: MessageBubble):
        count = self._chat_layout.count()
        self._chat_layout.insertWidget(count - 1, bubble)
        QTimer.singleShot(30, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        sb = self._scroll.verticalScrollBar()
        sb.setValue(sb.maximum())
