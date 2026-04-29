import re
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QScrollArea, QWidget, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QDragEnterEvent, QDropEvent

from src.modules.library.definitions import LIBRARY_FUNCTIONS


class BlankTextBox(QLineEdit):
    """Custom QLineEdit with drag-and-drop support for game lessons."""
    text_changed_signal = pyqtSignal()

    def __init__(self, expected_answers, indentation="", is_small=False, parent=None):
        super().__init__(parent)
        self.expected_answers = expected_answers
        self.indentation = indentation
        self._is_small = is_small
        self.setAcceptDrops(True)
        
        self.setPlaceholderText("Drop function here..." if is_small else "Drop function here or type...")
        
        _fs = 7 if is_small else 10
        self.setFont(QFont("Consolas", _fs))
        
        # Style
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px dashed #f59e0b;
                border-radius: 6px;
                padding: {4 if is_small else 8}px;
                background-color: rgba(245, 158, 11, 0.05);
                color: #1e293b;
            }}
            QLineEdit:focus {{
                border: 2px solid #3b82f6;
                background-color: #ffffff;
            }}
        """)
        
        self.textChanged.connect(lambda: self.text_changed_signal.emit())

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        func_id = event.mimeData().text().strip()
        usage_snippet = self._find_usage_snippet(func_id)
        
        if usage_snippet:
            snippet_cleaned = usage_snippet.strip()
            self.setText(snippet_cleaned)
            event.acceptProposedAction()
        else:
            self.setText(func_id)
            event.acceptProposedAction()

    def _find_usage_snippet(self, func_id):
        for category, data in LIBRARY_FUNCTIONS.items():
            if func_id in data["functions"]:
                return data["functions"][func_id]["usage"]
            for f_name, f_info in data["functions"].items():
                if f_name.lower() == func_id.lower():
                    return f_info["usage"]
        return None

    def set_feedback(self, is_correct):
        _pad = 6 if self._is_small else 10
        if is_correct:
            self.setStyleSheet(f"""
                QLineEdit {{
                    border: 2px solid #22c55e;
                    border-radius: 6px;
                    padding: {_pad}px;
                    background-color: rgba(34, 197, 94, 0.1);
                    color: #166534;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QLineEdit {{
                    border: 2px solid #ef4444;
                    border-radius: 6px;
                    padding: {_pad}px;
                    background-color: rgba(239, 68, 68, 0.1);
                    color: #991b1b;
                }}
            """)

    def clear_feedback(self):
        _pad = 5 if self._is_small else 8
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px dashed #f59e0b;
                border-radius: 6px;
                padding: {_pad}px;
                background-color: rgba(245, 158, 11, 0.05);
                color: #1e293b;
            }}
            QLineEdit:focus {{
                border: 2px solid #3b82f6;
                background-color: #ffffff;
            }}
        """)


class GameLessonWidget(QFrame):
    """Visual drag-and-drop game round layout for fill-in-the-blank lessons."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._blank_boxes = {}  # line_num -> BlankTextBox
        self._parsed_step = None
        self._is_small = False
        
        self.setObjectName("gameLessonWidget")
        self.setStyleSheet("background-color: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;")
        
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.NoFrame)
        self._scroll_area.setStyleSheet("QScrollArea { background: transparent; }")
        
        self._content_widget = QWidget()
        self._content_widget.setStyleSheet("background: transparent;")
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(8, 8, 8, 8)
        self._content_layout.setSpacing(8)
        
        self._scroll_area.setWidget(self._content_widget)
        self._main_layout.addWidget(self._scroll_area)

    def set_small_mode(self, is_small):
        """Update sizing for screen resolutions and redraw content."""
        self._is_small = is_small
        if self._is_small:
            self._content_layout.setContentsMargins(8, 8, 8, 8)
            self._content_layout.setSpacing(8)
        else:
            self._content_layout.setContentsMargins(20, 20, 20, 20)
            self._content_layout.setSpacing(15)
            
        if self._parsed_step:
            self.set_blank_mode(self._parsed_step)

    def set_blank_mode(self, parsed_step):
        self._parsed_step = parsed_step
        self._blank_boxes.clear()
        
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        lines = parsed_step.display_lines
        blank_map = parsed_step.blank_map
        
        current_code_block = []
        
        skip_patterns = [
            r"^#\s*={3,}",
            r"^#\s*LESSON",
            r"^#\s*TITLE",
            r"^#\s*NHIỆM VỤ",
            r"^#\s*TASK",
            r"^#\s*HƯỚNG DẪN",
            r"^#\s*INSTRUCTIONS"
        ]
        
        def should_skip(l):
            return any(re.search(pat, l, re.I) for pat in skip_patterns)

        for line_num, line in enumerate(lines):
            if line_num in blank_map:
                if current_code_block:
                    self._add_code_block(current_code_block)
                    current_code_block = []
                    
                blank_info = blank_map[line_num]
                self._add_blank_block(line_num, blank_info)
            else:
                stripped = line.strip()
                if should_skip(line):
                    continue
                
                if stripped.startswith("#"):
                    if current_code_block:
                        self._add_code_block(current_code_block)
                        current_code_block = []
                        
                    title_text = stripped.lstrip("#").strip()
                    if title_text:
                        self._add_title_block(title_text)
                elif stripped:
                    current_code_block.append(line)
                else:
                    if current_code_block:
                        self._add_code_block(current_code_block)
                        current_code_block = []

        if current_code_block:
            self._add_code_block(current_code_block)

        self._content_layout.addStretch()

    def _add_title_block(self, text):
        label = QLabel(text)
        label.setWordWrap(True)
        _fs = 8 if self._is_small else 10
        label.setFont(QFont("Inter", _fs, QFont.Bold))
        label.setStyleSheet(f"""
            QLabel {{
                color: #4f46e5;
                background-color: #eef2ff;
                border-left: 4px solid #4f46e5;
                padding: {5 if self._is_small else 10}px {8 if self._is_small else 15}px;
                border-radius: 4px;
            }}
        """)
        self._content_layout.addWidget(label)

    def _add_code_block(self, code_lines):
        label = QLabel("\n".join(code_lines))
        _fs = 6 if self._is_small else 9
        label.setFont(QFont("Consolas", _fs))
        label.setStyleSheet(f"""
            QLabel {{
                color: #0f172a;
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                padding: {4 if self._is_small else 10}px;
                border-radius: 6px;
            }}
        """)
        self._content_layout.addWidget(label)

    def _add_blank_block(self, line_num, blank_info):
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        indent_spaces = len(blank_info.indentation)
        if indent_spaces > 0:
            pixel_indent = (indent_spaces // 4) * (15 if self._is_small else 30)
            h_layout.addSpacing(pixel_indent)
            
        textbox = BlankTextBox(blank_info.expected_answers, blank_info.indentation, is_small=self._is_small)
        self._blank_boxes[line_num] = textbox
        
        h_layout.addWidget(textbox)
        
        blank_widget = QWidget()
        blank_widget.setLayout(h_layout)
        self._content_layout.addWidget(blank_widget)

    def get_blank_contents(self):
        contents = {}
        for line_num, textbox in self._blank_boxes.items():
            contents[line_num] = textbox.text().strip()
        return contents

    def set_blank_feedback(self, results):
        for result in results:
            line_num = result.line_number
            if line_num in self._blank_boxes:
                self._blank_boxes[line_num].set_feedback(result.is_correct)

    def clear_blank_feedback(self, line_num):
        if line_num in self._blank_boxes:
            self._blank_boxes[line_num].clear_feedback()

    def fill_blanks_with_answers(self, blank_map):
        for line_num, blank_info in blank_map.items():
            if line_num in self._blank_boxes and blank_info.expected_answers:
                self._blank_boxes[line_num].setText(blank_info.expected_answers[0])

    def toPlainText(self):
        if not self._parsed_step:
            return ""
            
        full_lines = []
        for line_num, line in enumerate(self._parsed_step.display_lines):
            if line_num in self._blank_boxes:
                text_input = self._blank_boxes[line_num].text().strip()
                full_lines.append(self._parsed_step.blank_map[line_num].indentation + text_input)
            else:
                full_lines.append(line)
                
        return "\n".join(full_lines)
