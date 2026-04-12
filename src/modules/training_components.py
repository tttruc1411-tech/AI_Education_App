from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QLabel
from PyQt5.QtCore import pyqtSignal, Qt, QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator
import re

class MultiClassTagPanel(QWidget):
    """
    A modular component for Detection Mode that allows defining up to 4 classes
    via colored tags. Validates that at least 1 class is defined and follows
    single-word naming conventions.
    """
    validation_changed = pyqtSignal(bool) # Emits True if at least 1 class is valid
    classes_updated = pyqtSignal(list)   # Emits list of valid class names

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MultiClassTagPanel")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(4)

        # Title / Hint
        self.lbl_hint = QLabel("🏷️ Define Classes (Min 1, Single-word)")
        self.lbl_hint.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold;")
        self.lbl_hint.setWordWrap(True)
        layout.addWidget(self.lbl_hint)

        # 2x2 grid layout instead of 1x4 row — fits narrow columns
        tag_grid = QGridLayout()
        tag_grid.setSpacing(4)

        self.tags = []
        colors = [
            ("#f3e8ff", "#a855f7"), # Purple
            ("#ffe4e6", "#fb7185"), # Rose
            ("#e0f2fe", "#3b82f6"), # Blue
            ("#d1fae5", "#10b981")  # Emerald
        ]

        for i in range(4):
            bg, border = colors[i]
            edit = QLineEdit()
            edit.setPlaceholderText(f"Class {i+1}")
            edit.setStyleSheet(f"""
                QLineEdit {{
                    background: {bg}; border: 1px solid {border};
                    border-radius: 6px; padding: 4px;
                    font-size: 11px; font-weight: 600; color: #1e293b;
                }}
                QLineEdit:focus {{ border: 2px solid {border}; }}
                QLineEdit:disabled {{
                    background: {bg}; border-color: {border}; color: #334155;
                }}
            """)
            valid_regex = QRegularExpression("[a-zA-Z]+")
            edit.setValidator(QRegularExpressionValidator(valid_regex))

            edit.textChanged.connect(self._validate)
            row, col = divmod(i, 2)
            tag_grid.addWidget(edit, row, col)
            self.tags.append(edit)

        layout.addLayout(tag_grid)

    def _validate(self):
        valid_names = []
        for edit in self.tags:
            name = edit.text().strip()
            # Restriction: Letters only, no symbols/numbers/spaces
            if name and re.match(r"^[a-zA-Z]+$", name):
                valid_names.append(name)
                edit.setProperty("invalid", "false")
            elif name:
                edit.setProperty("invalid", "true")
            
            # Simple visual feedback for invalid (red border if text entered but invalid)
            if edit.property("invalid") == "true":
                edit.setStyleSheet(edit.styleSheet() + "QLineEdit { border: 1px solid #ef4444; }")
            else:
                # Reset to default handled by the property if we were using QSS properly, 
                # but for simplicity we keep the original style above.
                pass

        is_valid = len(valid_names) >= 1
        self.validation_changed.emit(is_valid)
        self.classes_updated.emit(valid_names)

        # Update hint text if invalid
        if len(valid_names) < 1:
            self.lbl_hint.setText("⚠️ Please insert at least 1 class name (Single-word)")
            self.lbl_hint.setStyleSheet("color: #ef4444; font-size: 11px; font-weight: bold;")
        else:
            self.lbl_hint.setText("✅ Multi-class configuration valid!")
            self.lbl_hint.setStyleSheet("color: #10b981; font-size: 11px; font-weight: bold;")

    def get_class_names(self):
        return [t.text().strip() for t in self.tags if t.text().strip()]

    def set_class_names(self, names):
        """Programmatically populate tag fields from a list of class names."""
        for i, edit in enumerate(self.tags):
            edit.setText(names[i] if i < len(names) else "")
        self._validate()

    def set_small_mode(self, is_small):
        """Resize tag inputs for 16:9 small screen mode."""
        _fs = 8 if is_small else 11
        _pad = "2px" if is_small else "4px"
        _hint_fs = 8 if is_small else 11
        for edit in self.tags:
            ss = re.sub(r"padding:\s*\d+px", f"padding: {_pad}", edit.styleSheet())
            ss = re.sub(r"font-size:\s*\d+px", f"font-size: {_fs}px", ss)
            edit.setStyleSheet(ss)
        self.lbl_hint.setStyleSheet(re.sub(r"font-size:\s*\d+px", f"font-size: {_hint_fs}px", self.lbl_hint.styleSheet()))

    def lock_classes(self):
        """Permanent lock for tag inputs once collection/labeling begins."""
        for edit in self.tags:
            edit.setEnabled(False)
        self.lbl_hint.setText("🔒 Configuration locked (Data exists)")
        self.lbl_hint.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold;")
