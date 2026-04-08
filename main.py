import sys
import os

# Suppress noisy C-library warnings on Jetson (must be set before imports)
os.environ["ORT_LOG_LEVEL"] = "ERROR"
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

# Pre-import onnxruntime with fd-level stderr silenced to suppress
# the C++ "device_discovery.cc" DRM warning on Jetson Orin Nano
try:
    _devnull = os.open(os.devnull, os.O_WRONLY)
    _old_stderr = os.dup(2)
    os.dup2(_devnull, 2)
    import onnxruntime  # noqa: F401
    os.dup2(_old_stderr, 2)
    os.close(_devnull)
    os.close(_old_stderr)
except Exception:
    pass

import warnings
import subprocess
import base64
import re
from datetime import datetime
from pathlib import Path
from PyQt5.QtCore import Qt, QDir, QProcess, QProcessEnvironment, QTimer, QEvent, QPoint
from PyQt5.QtGui import QColor, QFont, QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QPushButton, QFrame,
                             QTextEdit, QPlainTextEdit, QInputDialog, QMessageBox, QWidget,
                             QHBoxLayout, QTreeView, QLabel, QVBoxLayout, QSplitter, QSizePolicy,
                             QLineEdit, QFileDialog, QScrollArea, QGridLayout, QRubberBand,
                             QProgressBar, QSpinBox, QDoubleSpinBox, QComboBox, QFileSystemModel,
                             QShortcut)
from PyQt5.QtGui import QKeySequence
from PyQt5.uic import loadUi
from src.modules.translations import STRINGS
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.modules.training_components import MultiClassTagPanel
import numpy as np

# ────────────────────────────────────────────────────────────
#  Training Progress Chart Canvas
# ────────────────────────────────────────────────────────────

class TrainingCanvas(FigureCanvas):
    def __init__(self, parent=None, title="", ylabel="", color_train="#3b82f6", color_val="#8b5cf6"):
        fig = Figure(figsize=(5, 4), dpi=90, facecolor="#f8fafc")
        self.axes = fig.add_subplot(111)
        self.axes.set_title(title, fontsize=12, fontweight='bold', color="#1e293b", pad=12)
        self.axes.set_ylabel(ylabel, fontsize=9, color="#475569")
        self.axes.tick_params(labelsize=8, colors="#64748b")
        self.axes.grid(True, linestyle='--', alpha=0.5, color="#cbd5e1")
        
        for spine in self.axes.spines.values():
            spine.set_edgecolor("#e2e8f0")
            
        fig.subplots_adjust(top=0.88, bottom=0.15, left=0.12, right=0.95)
        super().__init__(fig)
        self.setParent(parent)
        
        self.x_data = []
        self.y_train = []
        self.y_val = []
        self.color_train = color_train
        self.color_val = color_val
        self.line_train, = self.axes.plot([], [], color=color_train, lw=2, label="Train")
        self.line_val, = self.axes.plot([], [], color=color_val, lw=2, linestyle='--', label="Val")
        self.axes.legend(fontsize=8, loc='upper right', frameon=False)

    def update_data(self, epoch, train_val, validation_val):
        self.x_data.append(epoch)
        self.y_train.append(train_val)
        self.y_val.append(validation_val)
        
        self.line_train.set_data(self.x_data, self.y_train)
        self.line_val.set_data(self.x_data, self.y_val)
        
        self.axes.relim()
        self.axes.autoscale_view()
        self.draw()

# ────────────────────────────────────────────────────────────
#  Annotation Label for Detection Mode
# ────────────────────────────────────────────────────────────

from PyQt5.QtCore import pyqtSignal, QRect, QPoint, QSize
from PyQt5.QtGui import QPainter, QPen

class AnnotationLabel(QLabel):
    box_drawn = pyqtSignal(object) 
    save_requested = pyqtSignal()
    close_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.is_drawing = False
        self.image_pixmap = None
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.current_mouse_pos = QPoint()
        
        # 📦 Multi-Box State
        self.all_boxes = [] # List of {"norm_box": (cx, cy, w, h), "class_id": int, "class_name": str}
        self.selected_box_idx = -1
        
        # 🔧 Interactive Resizing State
        self.handle_size = 10
        self.active_handle = None # 'tl', 'tr', 'bl', 'br', 'move'
        self.is_resizing = False
        self.drag_start_norm = None
        
        # 🧪 Detection Context
        self.active_class_id = 0
        self.active_class_name = ""
        self.is_capture_mode = False 
        self.class_name = "" # Fallback
        
    def setPixmap(self, pixmap):
        """Override to keep image_pixmap in sync with QLabel's pixmap."""
        super().setPixmap(pixmap)
        self.image_pixmap = pixmap
        self.update()

    def set_image(self, pixmap):
        self.setPixmap(pixmap)
        
    def add_box(self, cx, cy, w, h, class_id, class_name):
        self.all_boxes.append({
            "norm_box": (cx, cy, w, h),
            "class_id": class_id,
            "class_name": class_name
        })
        self.selected_box_idx = len(self.all_boxes) - 1
        self.update()
        
    def clear_all(self):
        self.all_boxes = []
        self.selected_box_idx = -1
        self.update()

    def delete_selected(self):
        if 0 <= self.selected_box_idx < len(self.all_boxes):
            self.all_boxes.pop(self.selected_box_idx)
            self.selected_box_idx = -1
            self.update()

    def _pixel_to_norm(self, pos):
        rect = self._get_image_rect()
        if not rect.isValid(): return None
        nx = (pos.x() - rect.x()) / rect.width()
        ny = (pos.y() - rect.y()) / rect.height()
        return nx, ny

    def _norm_to_pixel(self, cx, cy, w, h):
        rect = self._get_image_rect()
        if not rect.isValid(): return QRect()
        lx = (cx - w/2) * rect.width() + rect.x()
        ly = (cy - h/2) * rect.height() + rect.y()
        lw = w * rect.width()
        lh = h * rect.height()
        return QRect(int(lx), int(ly), int(lw), int(lh))

    def _get_handles(self, pixel_box):
        if pixel_box.isNull(): return {}
        return {
            'tl': pixel_box.topLeft(),
            'tr': pixel_box.topRight(),
            'bl': pixel_box.bottomLeft(),
            'br': pixel_box.bottomRight()
        }

    def _hit_test(self, pos):
        # Priority 1: Check handles of SELECTED box
        if 0 <= self.selected_box_idx < len(self.all_boxes):
            box = self.all_boxes[self.selected_box_idx]
            pb = self._norm_to_pixel(*box["norm_box"])
            handles = self._get_handles(pb)
            for h_type, h_pos in handles.items():
                if (pos - h_pos).manhattanLength() < self.handle_size * 2:
                    return self.selected_box_idx, h_type
        
        # Priority 2: Check all boxes (from top to bottom / reverse list)
        for i in reversed(range(len(self.all_boxes))):
            box = self.all_boxes[i]
            pb = self._norm_to_pixel(*box["norm_box"])
            if pb.contains(pos):
                return i, 'move'
        return None, None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#000"))
        
        rect = self._get_image_rect()
        if self.image_pixmap and not self.image_pixmap.isNull():
            painter.drawPixmap(rect, self.image_pixmap)
        else:
            painter.setPen(QColor("#64748b"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Select an image to annotate")
            
        # Draw Crosshair
        if self.underMouse() and rect.isValid() and rect.contains(self.current_mouse_pos):
            if not self.is_resizing and not self.is_drawing:
                painter.setPen(QPen(QColor(255, 255, 255, 60), 1, Qt.DashLine))
                painter.drawLine(rect.left(), self.current_mouse_pos.y(), rect.right(), self.current_mouse_pos.y())
                painter.drawLine(self.current_mouse_pos.x(), rect.top(), self.current_mouse_pos.x(), rect.bottom())

        # Palette match (Sync with main.py colors)
        palette = ["#a855f7", "#fb7185", "#3b82f6", "#10b981"]

        # 4. Draw ALL Existing Boxes
        for i, box_data in enumerate(self.all_boxes):
            cx, cy, w, h = box_data["norm_box"]
            pixel_box = self._norm_to_pixel(cx, cy, w, h)
            is_selected = (i == self.selected_box_idx)
            
            color_hex = palette[box_data["class_id"] % len(palette)]
            color = QColor(color_hex)
            
            # Box Body
            pen_width = 3 if is_selected else 1
            painter.setPen(QPen(color, pen_width))
            painter.setBrush(QColor(color.red(), color.green(), color.blue(), 40 if is_selected else 20))
            painter.drawRect(pixel_box)
            
            # Label
            name = box_data["class_name"] or f"Tag {box_data['class_id']}"
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            lbl_w = painter.fontMetrics().horizontalAdvance(name) + 12
            label_rect = QRect(pixel_box.left(), pixel_box.top() - 18, lbl_w, 18)
            if label_rect.top() < rect.top(): label_rect.moveTop(pixel_box.top())
            painter.drawRoundedRect(label_rect, 3, 3)
            
            painter.setPen(Qt.white)
            font = painter.font()
            font.setPixelSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(label_rect, Qt.AlignCenter, name)

            # handles for selection
            if is_selected:
                painter.setBrush(color)
                painter.setPen(QPen(Qt.white, 1))
                for h_pos in self._get_handles(pixel_box).values():
                    painter.drawEllipse(h_pos, self.handle_size//2, self.handle_size//2)

        # 5. Draw currently drawing box
        if self.is_drawing:
            color = QColor(palette[self.active_class_id % len(palette)])
            draw_box = QRect(self.start_point, self.end_point).normalized()
            if rect.isValid(): draw_box = draw_box.intersected(rect)
            painter.setPen(QPen(color, 2, Qt.DashLine))
            painter.drawRect(draw_box)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image_pixmap:
            idx, hit = self._hit_test(event.pos())
            if idx is not None:
                self.selected_box_idx = idx
                self.active_handle = hit
                self.is_resizing = True
                self.drag_start_norm = self._pixel_to_norm(event.pos())
                self.update()
            else:
                img_rect = self._get_image_rect()
                if img_rect.contains(event.pos()):
                    self.selected_box_idx = -1
                    self.is_drawing = True
                    self.start_point = event.pos()
                    self.end_point = event.pos()
                    self.update()
        elif event.button() == Qt.RightButton:
            self.delete_selected()

    def mouseMoveEvent(self, event):
        self.current_mouse_pos = event.pos()
        rect = self._get_image_rect()
        
        if self.is_drawing:
            self.end_point = event.pos()
            self.update()
        elif self.is_resizing and 0 <= self.selected_box_idx < len(self.all_boxes):
            curr_norm = self._pixel_to_norm(event.pos())
            if not curr_norm or not self.drag_start_norm: return
            
            box = self.all_boxes[self.selected_box_idx]
            cx, cy, w, h = box["norm_box"]
            dx = curr_norm[0] - self.drag_start_norm[0]
            dy = curr_norm[1] - self.drag_start_norm[1]
            
            if self.active_handle == 'move':
                cx = max(w/2, min(1-w/2, cx + dx))
                cy = max(h/2, min(1-h/2, cy + dy))
            elif self.active_handle == 'tl':
                nx1, ny1 = max(0, min(cx+w/2-0.01, cx-w/2+dx)), max(0, min(cy+h/2-0.01, cy-h/2+dy))
                nx2, ny2 = cx + w/2, cy + h/2
                cx, cy, w, h = (nx1+nx2)/2, (ny1+ny2)/2, nx2-nx1, ny2-ny1
            elif self.active_handle == 'br':
                nx1, ny1 = cx - w/2, cy - h/2
                nx2, ny2 = max(cx-w/2+0.01, min(1, cx+w/2+dx)), max(cy-h/2+0.01, min(1, cy+h/2+dy))
                cx, cy, w, h = (nx1+nx2)/2, (ny1+ny2)/2, nx2-nx1, ny2-ny1
            elif self.active_handle == 'tr':
                nx1, ny1 = cx - w/2, max(0, min(cy+h/2-0.01, cy-h/2+dy))
                nx2, ny2 = max(cx-w/2+0.01, min(1, cx+w/2+dx)), cy + h/2
                cx, cy, w, h = (nx1+nx2)/2, (ny1+ny2)/2, nx2-nx1, ny2-ny1
            elif self.active_handle == 'bl':
                nx1, ny1 = max(0, min(cx+w/2-0.01, cx-w/2+dx)), cy - h/2
                nx2, ny2 = cx + w/2, max(cy-h/2+0.01, min(1, cy+h/2+dy))
                cx, cy, w, h = (nx1+nx2)/2, (ny1+ny2)/2, nx2-nx1, ny2-ny1

            self.all_boxes[self.selected_box_idx]["norm_box"] = (cx, cy, w, h)
            self.drag_start_norm = curr_norm
            self.update()
        else:
            idx, hit = self._hit_test(event.pos())
            if hit == 'move': self.setCursor(Qt.SizeAllCursor)
            elif hit in ('tl', 'br'): self.setCursor(Qt.SizeFDiagCursor)
            elif hit in ('tr', 'bl'): self.setCursor(Qt.SizeBDiagCursor)
            elif rect.contains(event.pos()): self.setCursor(Qt.CrossCursor)
            else: self.setCursor(Qt.ArrowCursor)
            
        self.update()
            
    def mouseReleaseEvent(self, event):
        if self.is_drawing:
            self.is_drawing = False
            pixel_box = QRect(self.start_point, event.pos()).normalized()
            img_rect = self._get_image_rect()
            if img_rect.isValid() and pixel_box.width() > 5 and pixel_box.height() > 5:
                pixel_box = pixel_box.intersected(img_rect)
                cx_norm = (pixel_box.center().x() - img_rect.x()) / img_rect.width()
                cy_norm = (pixel_box.center().y() - img_rect.y()) / img_rect.height()
                w_norm = pixel_box.width() / img_rect.width()
                h_norm = pixel_box.height() / img_rect.height()
                self.add_box(cx_norm, cy_norm, w_norm, h_norm, self.active_class_id, self.active_class_name)
        elif self.is_resizing:
            self.is_resizing = False
            self.active_handle = None
        self.update()
            
    def _get_image_rect(self):
        if not self.image_pixmap or self.image_pixmap.isNull(): return QRect()
        lbl_w, lbl_h, img_w, img_h = self.width(), self.height(), self.image_pixmap.width(), self.image_pixmap.height()
        scale = min(lbl_w / img_w, lbl_h / img_h)
        final_w, final_h = int(img_w * scale), int(img_h * scale)
        return QRect((lbl_w - final_w) // 2, (lbl_h - final_h) // 2, final_w, final_h)

    def get_all_normalized_boxes(self):
        return [tuple(round(x, 6) for x in b["norm_box"]) + (b["class_id"],) for b in self.all_boxes]

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            self.delete_selected()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.save_requested.emit()
        elif event.key() == Qt.Key_Escape:
            if self.selected_box_idx != -1: self.selected_box_idx = -1
            else: self.close_requested.emit()
        super().keyPressEvent(event)


# ────────────────────────────────────────────────────────────
#  Dynamic Curriculum Card Widget
# ────────────────────────────────────────────────────────────


class CurriculumCard(QFrame):
    def __init__(self, filename, title, level, icon, color, desc, on_load_click):
        super().__init__()
        self.filename = filename
        self.setMinimumHeight(90)
        
        # Consistent colorful card design
        self.setObjectName("CurriculumCard")
        # Ensure we have a semi-transparent version for the background
        bg_color = f"rgba({int(color[1:3],16)}, {int(color[3:5],16)}, {int(color[5:7],16)}, 0.08)"
        border_color = f"rgba({int(color[1:3],16)}, {int(color[3:5],16)}, {int(color[5:7],16)}, 0.4)"
        
        self.setStyleSheet(f"""
            QFrame#CurriculumCard {{ 
                border: 1px solid {border_color}; 
                border-radius: 12px; 
                background: {bg_color}; 
            }}
            QFrame#CurriculumCard:hover {{
                border: 2px solid {color};
                background: white;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 1. Icon
        icon_str = icon.strip('"\' ')
        icon_lbl = QLabel()
        from PyQt5.QtGui import QPixmap, QFont
        import os
        
        if icon_str.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
            # Try to load the image
            pixmap = QPixmap(icon_str)
            if not pixmap.isNull():
                # Scale smoothly to fit the icon slot
                pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_lbl.setPixmap(pixmap)
            else:
                icon_lbl.setText("❓")
                icon_lbl.setFont(QFont("Segoe UI", 24))
        else:
            # Render standard emoji
            icon_lbl.setText(icon_str)
            icon_lbl.setFont(QFont("Segoe UI", 24))
            
        icon_lbl.setMinimumWidth(40)
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)
        
        # 2. Body Container (V-Box to hold the two horizontal rows)
        body_vbox = QVBoxLayout()
        body_vbox.setSpacing(4)
        
        # --- ROW 1: Title + Badge ---
        row1 = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet("font-weight: bold; font-size: 15px; color: #1e293b; background: transparent;")
        
        # Level Badge
        badge_colors = {"Beginner": "#08a54f", "Intermediate": "#f6710b", "Advanced": "#b51414"}
        badge_bg = badge_colors.get(level, "#64748b")
        badge = QLabel(level)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(80, 20)
        badge.setStyleSheet(f"background: {badge_bg}; color: white; border-radius: 6px; font-size: 10px; font-weight: bold;")
        
        row1.addWidget(title_lbl, 1)
        row1.addWidget(badge)
        body_vbox.addLayout(row1)
        
        # --- ROW 2: Description + Load Button ---
        row2 = QHBoxLayout()
        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #475569; font-size: 13px; background: transparent;")
        
        # Load Button
        btn_load = QPushButton("Load")
        btn_load.setCursor(Qt.PointingHandCursor)
        btn_load.setFixedSize(80, 28)
        btn_load.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #3b82f6, stop:1 #7c3aed); 
                color: white; 
                border-radius: 12px; 
                font-weight: bold; 
                font-size: 15px; 
                border: none;
                padding: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #2563eb, stop:1 #6d28d9);
            }
        """)
        btn_load.clicked.connect(lambda: on_load_click(filename))
        
        row2.addWidget(desc_lbl, 1)
        row2.addWidget(btn_load)
        body_vbox.addLayout(row2)
        
        layout.addLayout(body_vbox)

# ────────────────────────────────────────────────────────────

from src.modules.file_manager import FileManager
from src.modules.function_library import populate_functions_tab
from src.modules.results_panel import update_results_panel
from src.modules.library.manager import prepare_code_injection

warnings.filterwarnings("ignore", category=DeprecationWarning)


class DarkTooltipFilter(QWidget):
    """Application-level event filter that replaces the native OS tooltip
    with a custom dark QLabel, bypassing Windows' native white renderer."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tip = QLabel(self)
        self._tip.setWindowFlags(
            Qt.ToolTip |
            Qt.BypassGraphicsProxyWidget
        )
        self._tip.setAttribute(Qt.WA_ShowWithoutActivating)
        self._tip.setContentsMargins(0, 0, 0, 0)
        self._tip.setWordWrap(False)
        self._tip.setStyleSheet("""
            QLabel {
                background-color: #1e293b;
                color: #f1f5f9;
                border: 1px solid #334155;
                border-radius: 5px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 3px 8px;
            }
        """)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.ToolTip:
            w = obj
            text = w.toolTip() if hasattr(w, 'toolTip') else ""
            if text:
                self._tip.setText(text)
                self._tip.adjustSize()
                # Show near cursor
                pos = event.globalPos()
                self._tip.move(pos.x() + 12, pos.y() + 18)
                self._tip.show()
            else:
                self._tip.hide()
            return True  # consume the event so native tooltip never shows
        if event.type() in (QEvent.Leave, QEvent.MouseButtonPress,
                            QEvent.KeyPress, QEvent.Wheel):
            self._tip.hide()
        return False


class AICodingLab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(900, 600) # Ensure it CAN shrink to fit small Jetson screens
        
        # 1. Setup Paths
        self.ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "ui")
        
        self.file_manager = FileManager(os.path.dirname(os.path.abspath(__file__)))
        self.current_lang = "en" # Default to English
        self.current_open_file = None
        print(STRINGS[self.current_lang]["HINT_DIR_INITIALIZED"])
        
        # 2. Load the Main Shell
        try:
            loadUi(os.path.join(self.ui_dir, "main_window.ui"), self)
            print("Main shell loaded.")
        except Exception as e:
            print(f"Error loading main shell: {e}")
            return

        self.mainStack = self.findChild(QStackedWidget, "mainStack")
        
        # 4. Load Running Mode
        try:
            self.running_mode_widget = loadUi(os.path.join(self.ui_dir, "running_mode.ui"))
            self.mainStack.addWidget(self.running_mode_widget)
            
            self.training_mode_widget = loadUi(os.path.join(self.ui_dir, "training_mode.ui"))
            self.mainStack.addWidget(self.training_mode_widget)

            # Set 1:1.8:1 initial proportions for training mode splitters
            from PyQt5.QtWidgets import QSplitter
            h_splitter = self.training_mode_widget.findChild(QSplitter, "horizontalSplitter")
            if h_splitter:
                h_splitter.setSizes([100, 260, 100])
            
            v_splitter = self.training_mode_widget.findChild(QSplitter, "midSplitter")
            if v_splitter:
                # 1:1.6 ratio — config compact, progress (graph) gets more space
                v_splitter.setSizes([240, 320])


            # Connect Core Navigation
            self.btnRunMode = self.findChild(QPushButton, "btnRunMode")
            self.btnTrainMode = self.findChild(QPushButton, "btnTrainMode")
            self.btnRunMode.clicked.connect(lambda: self.switch_mode(0))
            self.btnTrainMode.clicked.connect(lambda: self.switch_mode(1))
            
            # Start in Training Mode
            self.switch_mode(1)
            print("Modes loaded and initialized.")
        except Exception as e:
            print(f"Error loading modes: {e}")
            return

        # 5. Connect the App Toggle Buttons (from main_window.ui)
        
        if self.btnRunMode and self.btnTrainMode:
            self.btnRunMode.clicked.connect(self.show_running_mode)
        self.btnLangEN = self.findChild(QPushButton, "btnLangEN")
        self.btnLangVN = self.findChild(QPushButton, "btnLangVN")

        if self.btnLangEN and self.btnLangVN:
            self.btnLangEN.clicked.connect(lambda: self.set_language("en"))
            self.btnLangVN.clicked.connect(lambda: self.set_language("vi"))

        # 6. Wire up Running Mode internal components
        # A) Editor & Basic Buttons
        self.monacoPlaceholder = self.running_mode_widget.findChild(QTextEdit, "monacoPlaceholder")
        self.btnCreateFile = self.running_mode_widget.findChild(QPushButton, "btnCreateFile")
        self.btnRunCode = self.running_mode_widget.findChild(QPushButton, "btnRunCode")
        self.tabPlus = self.running_mode_widget.findChild(QPushButton, "tabPlus")
        self.tabContainer = self.running_mode_widget.findChild(QWidget, "tabContainer")
        
        # DYNAMIC CURRICULUM DISCOVERY
        self.hubContentLayout = self.running_mode_widget.findChild(QVBoxLayout, "hubContentLayout")
        self.populate_curriculum_hub()
        
        if self.btnCreateFile: self.btnCreateFile.clicked.connect(self.create_new_file)
        if self.btnRunCode: 
            self.btnRunCode.clicked.connect(self.save_and_run_code)
            self.btnRunCode.setFixedHeight(40)
            self.btnRunCode.setStyleSheet("""
                QPushButton { 
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
                    color: white; border-radius: 8px; font-weight: bold; font-size: 16px; padding: 0 16px;
                }
                QPushButton:hover { background: #059669; }
                QPushButton:pressed { background: #047857; }
            """)
        if self.tabPlus: self.tabPlus.clicked.connect(self.create_new_tab)

        self.btnSaveFile = self.running_mode_widget.findChild(QPushButton, "btnSaveFile")
        if self.btnSaveFile: 
            self.btnSaveFile.clicked.connect(self.save_current_file)
            self.btnSaveFile.setFixedHeight(40)
            self.btnSaveFile.setStyleSheet("""
                QPushButton { 
                    background: #2D84E0; color: white; border: none;
                    border-radius: 8px; font-weight: bold; font-size: 16px; padding: 0 16px;
                }
                QPushButton:hover { background: #0E5FB5; }
                QPushButton:pressed { background: #094D94; }
            """)

        # Ctrl+S shortcut
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current_file)

        from src.modules.advanced_editor import AdvancedPythonEditor
        from PyQt5.QtWidgets import QSplitter
        
        # --- SWAP EDITORS ---
        # 1) Running Mode
        old_running_editor = self.running_mode_widget.findChild(QWidget, "monacoPlaceholder")
        if old_running_editor:
            parent_widget = old_running_editor.parentWidget()
            idx = -1
            if isinstance(parent_widget, QSplitter):
                idx = parent_widget.indexOf(old_running_editor)
            
            self.monacoPlaceholder = AdvancedPythonEditor()
            self.monacoPlaceholder.setObjectName("monacoPlaceholder")
            
            if idx != -1 and isinstance(parent_widget, QSplitter):
                parent_widget.insertWidget(idx, self.monacoPlaceholder)
                old_running_editor.setParent(None)
                old_running_editor.deleteLater()
            elif parent_widget.layout():
                parent_widget.layout().replaceWidget(old_running_editor, self.monacoPlaceholder)
                old_running_editor.deleteLater()
            else:
                self.monacoPlaceholder.setParent(parent_widget)
                old_running_editor.deleteLater()
            
            self.monacoPlaceholder.setAcceptDrops(True)
            self.monacoPlaceholder.functionDropped.connect(self.on_function_dropped)
            self.monacoPlaceholder.show()

        # 2a) Find Splitters for Styling
        self.mainSplitter = self.running_mode_widget.findChild(QSplitter, "mainSplitter")
        self.runningEditorSplitter = self.running_mode_widget.findChild(QSplitter, "editorSplitter")
        self.rightSplitter = self.running_mode_widget.findChild(QSplitter, "rightSplitter")

        # B) HUB TABS & STACKED WIDGET
        # FIX: We must find these child widgets inside running_mode_widget first!
        self.hubStackedWidget = self.running_mode_widget.findChild(QStackedWidget, "hubStackedWidget")
        self.tabExamples = self.running_mode_widget.findChild(QPushButton, "tabExamples")
        self.tabFunctions = self.running_mode_widget.findChild(QPushButton, "tabFunctions")
        self.tabWorkspace = self.running_mode_widget.findChild(QPushButton, "tabWorkspace")

        if self.hubStackedWidget:
            if self.tabExamples: self.tabExamples.clicked.connect(lambda: self.hubStackedWidget.setCurrentIndex(0))
            if self.tabFunctions: self.tabFunctions.clicked.connect(lambda: self.hubStackedWidget.setCurrentIndex(1))
            if self.tabWorkspace: self.tabWorkspace.clicked.connect(lambda: self.hubStackedWidget.setCurrentIndex(2))

        # C) CONSOLE TERMINAL SETUP
        self.consoleContainer = self.running_mode_widget.findChild(QWidget, "consoleContainer")
        self.collapsedConsoleBar = self.running_mode_widget.findChild(QWidget, "collapsedConsoleBar")
        self.consoleBody = self.running_mode_widget.findChild(QPlainTextEdit, "consoleBody")
        self.btnCollapseConsole = self.running_mode_widget.findChild(QPushButton, "btnCollapseConsole")
        self.btnClearConsole = self.running_mode_widget.findChild(QPushButton, "btnClearConsole")

        if self.btnCollapseConsole: self.btnCollapseConsole.clicked.connect(lambda: self.set_console_expanded(False))
        if self.collapsedConsoleBar: self.collapsedConsoleBar.mousePressEvent = lambda e: self.set_console_expanded(True)
        if self.btnClearConsole: self.btnClearConsole.clicked.connect(self.clear_console)

        # Labels for Translation
        self.hubTitle = self.running_mode_widget.findChild(QLabel, "hubTitle")
        self.editorTitle = self.running_mode_widget.findChild(QLabel, "editorTitle")
        self.lblCT = self.running_mode_widget.findChild(QLabel, "lblCT")
        self.camTitle = self.running_mode_widget.findChild(QLabel, "camTitle")
        self.btnStartCamHeader = self.running_mode_widget.findChild(QPushButton, "btnStartCamHeader")
        self.resTitle = self.running_mode_widget.findChild(QLabel, "resTitle")

        self.lblStatus = self.running_mode_widget.findChild(QLabel, "lblStatus")
        self.lblTimestamp = self.running_mode_widget.findChild(QLabel, "lblTimestamp")
        self.lblVarCount = self.running_mode_widget.findChild(QLabel, "lblVarCount")
        self.resultsListLayout = self.running_mode_widget.findChild(QVBoxLayout, "resultsListLayout")

        # D) WORKSPACE TREE VIEW
        self.fileTreeView = self.running_mode_widget.findChild(QTreeView, "fileTreeView")
        if self.fileTreeView:
            self.setup_file_explorer()

        # E) INITIAL STATE
        self.open_tabs = []
        self.tab_buttons = []
        self._run_process = None          # QProcess for the running script
        self._live_vars = {}              # accumulate VAR: lines during a run
        self.add_tab("main.py", is_code=True)
        self.load_file_by_tab("main.py")
        self.log_to_console(STRINGS[self.current_lang]["TERMINAL_READY"])

        # F) POPULATE FUNCTIONS
        try:
            populate_functions_tab(self.running_mode_widget)
        except Exception as e:
            print(f"Error populating functions tab: {e}")

        self.workspaceStack = self.running_mode_widget.findChild(QStackedWidget, "workspaceStack")
        self.cardCode = self.running_mode_widget.findChild(QFrame, "cardCode")
        self.cardData = self.running_mode_widget.findChild(QFrame, "cardData")
        self.cardModel = self.running_mode_widget.findChild(QFrame, "cardModel")
        self.btnBackToDashboard = self.running_mode_widget.findChild(QPushButton, "btnBackToDashboard")
        self.workspaceFileListLayout = self.running_mode_widget.findChild(QVBoxLayout, "workspaceFileListLayout")
        self.lblCurrentFolder = self.running_mode_widget.findChild(QLabel, "lblCurrentFolder") # FIX: This was missing

        # Connect Dashboard actions
        if self.cardCode: self.cardCode.mousePressEvent = lambda e: self.show_folder_contents("Code")
        if self.cardData: self.cardData.mousePressEvent = lambda e: self.show_folder_contents("Data")
        if self.cardModel: self.cardModel.mousePressEvent = lambda e: self.show_folder_contents("Model")
        if self.btnBackToDashboard: 
            def handle_back_to_dashboard():
                self.update_workspace_counts()
                self.workspaceStack.setCurrentIndex(0)
            self.btnBackToDashboard.clicked.connect(handle_back_to_dashboard)

        self.update_workspace_counts()

        # 7. Set Column Ratios (1:2:1)
        if self.mainSplitter:
            import PyQt5.QtWidgets as qtw
            hubContainer = self.running_mode_widget.findChild(qtw.QFrame, "hubContainer")
            if hubContainer: hubContainer.setMinimumWidth(150)
            
            for btn_name in ["tabExamples", "tabFunctions", "tabWorkspace"]:
                b = self.running_mode_widget.findChild(qtw.QPushButton, btn_name)
                if b: b.setSizePolicy(qtw.QSizePolicy.Ignored, qtw.QSizePolicy.Fixed)

            self.mainSplitter.setStretchFactor(0, 1)
            self.mainSplitter.setStretchFactor(1, 2)
            self.mainSplitter.setStretchFactor(2, 1)
            self.mainSplitter.setSizes([300, 600, 300])

        # Middle Column: Editor (top) vs Console (bottom) -> Ratio 3:1
        if self.runningEditorSplitter:
            self.runningEditorSplitter.setStretchFactor(0, 3)
            self.runningEditorSplitter.setStretchFactor(1, 1)
            self.runningEditorSplitter.setSizes([600, 200])

        # Right Column: Camera (top) vs Results (bottom) -> Ratio 1:1
        if self.rightSplitter:
            self.rightSplitter.setStretchFactor(0, 1)
            self.rightSplitter.setStretchFactor(1, 1)
            self.rightSplitter.setSizes([300, 300])


        # 8. Style all splitter handles — futuristic purple/violet theme
        SPLITTER_STYLE = """
            QSplitter::handle {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0  #6d28d9,
                    stop:0.4 #7c3aed,
                    stop:0.6 #8b5cf6,
                    stop:1  #a78bfa
                );
                border-radius: 3px;
            }
            QSplitter::handle:horizontal {
                width: 6px;
                margin: 4px 0;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0  #6d28d9,
                    stop:0.5 #8b5cf6,
                    stop:1  #6d28d9
                );
            }
            QSplitter::handle:vertical {
                height: 6px;
                margin: 0 4px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0  #6d28d9,
                    stop:0.5 #8b5cf6,
                    stop:1  #6d28d9
                );
            }
            QSplitter::handle:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0  #7c3aed,
                    stop:0.5 #a78bfa,
                    stop:1  #7c3aed
                );
            }
            QSplitter::handle:pressed {
                background: #c4b5fd;
            }
        """
        for splitter in [self.mainSplitter, self.runningEditorSplitter, self.rightSplitter]:
            if splitter:
                splitter.setHandleWidth(3)
                splitter.setStyleSheet(SPLITTER_STYLE)

        # 9. Setup Camera Display in Column 3
        self.camBody = self.running_mode_widget.findChild(QFrame, "camBody")
        if self.camBody:
            # Ensure it has a layout
            if not self.camBody.layout():
                self.camBody.setLayout(QVBoxLayout())
                self.camBody.layout().setContentsMargins(0,0,0,0)
            
            self.camDisplay = QLabel()
            self.camDisplay.setAlignment(Qt.AlignCenter)
            self.camDisplay.setStyleSheet("background-color: black;")
            self.camDisplay.setScaledContents(True)
            # Essential: Ensure the camera label doesn't have a minimum size that locks the splitter
            from PyQt5.QtWidgets import QSizePolicy
            self.camDisplay.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.camBody.layout().addWidget(self.camDisplay)
            self.camDisplay.setText("Camera Ready")
            self.camDisplay.setStyleSheet("color: #4b5563; background: black; font-weight: bold;")

        # 10. ORC Hub Connection Indicator (in resFooter)
        self._setup_orc_indicator()

        # 11. Final Retranslation Initial
        self.retranslate_ui()

        # 12. Deferred ORC Hub check (after UI is visible)
        self._orc_connected = False
        QTimer.singleShot(500, self._check_orc_connection)

    # --- ORC Hub Indicator ---
    def _setup_orc_indicator(self):
        """Inject ORC Hub status widgets into the existing resFooter bar."""
        footer_layout = self.running_mode_widget.findChild(QHBoxLayout, "footerLayout")
        if not footer_layout:
            return

        # Find insertion index (just before lblTimestamp, which is the last widget)
        ts_index = footer_layout.count() - 1  # lblTimestamp position

        # Thin vertical separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet("color: #334155; background: transparent;")

        # Status dot
        self.lblOrcDot = QLabel("\u2B24")  # ⬤
        self.lblOrcDot.setFixedWidth(16)
        self.lblOrcDot.setStyleSheet("color: #6b7280; font-size: 10px; background: transparent;")

        # Label
        self.lblOrcText = QLabel("ORC Hub")
        self.lblOrcText.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")

        # Refresh button
        self.btnOrcRefresh = QPushButton("\u21BB")  # ↻
        self.btnOrcRefresh.setFixedSize(22, 22)
        self.btnOrcRefresh.setCursor(Qt.PointingHandCursor)
        self.btnOrcRefresh.setStyleSheet("""
            QPushButton {
                color: #94a3b8; font-size: 14px; font-weight: bold;
                background: transparent; border: none;
            }
            QPushButton:hover { color: #e2e8f0; }
        """)
        self.btnOrcRefresh.clicked.connect(self._check_orc_connection)

        # Insert: [sep] [dot] [label] [refresh]  before [timestamp]
        footer_layout.insertWidget(ts_index, sep)
        footer_layout.insertWidget(ts_index + 1, self.lblOrcDot)
        footer_layout.insertWidget(ts_index + 2, self.lblOrcText)
        footer_layout.insertWidget(ts_index + 3, self.btnOrcRefresh)

    def _check_orc_connection(self):
        """Probe ORC Hub via I2C and update the indicator."""
        try:
            from src.modules.library.functions.motor_driver_v2 import check_orc_hub
            connected, info = check_orc_hub()
        except Exception:
            connected, info = False, "Driver module unavailable"
        self._orc_connected = connected
        self._update_orc_indicator()

    def _update_orc_indicator(self):
        """Set dot color and tooltip based on connection state."""
        if not hasattr(self, 'lblOrcDot'):
            return
        s = STRINGS[self.current_lang]
        if self._orc_connected:
            self.lblOrcDot.setStyleSheet("color: #22c55e; font-size: 10px; background: transparent;")
            tip = s.get("ORC_CONNECTED", "ORC Hub: Connected")
        else:
            self.lblOrcDot.setStyleSheet("color: #6b7280; font-size: 10px; background: transparent;")
            tip = s.get("ORC_DISCONNECTED", "ORC Hub: Not Connected")
        self.lblOrcDot.setToolTip(tip)
        self.lblOrcText.setToolTip(tip)

    # --- Language Support ---
    def set_language(self, lang_code):
        """Switch application language and refresh UI labels."""
        if self.current_lang == lang_code: return
        self.current_lang = lang_code
        self.retranslate_ui()
        # Full refresh of dynamic content
        self.populate_curriculum_hub()
        self.update_workspace_counts()

    def retranslate_ui(self):
        """Update all core UI strings from the translation dictionary."""
        s = STRINGS[self.current_lang]
        
        # main_window.ui elements
        if hasattr(self, 'appSubtitle'): self.appSubtitle.setText(s["APP_SUBTITLE"])
        if hasattr(self, 'btnRunMode'): self.btnRunMode.setText(s["MODE_RUNNING"])
        if hasattr(self, 'btnTrainMode'): self.btnTrainMode.setText(s["MODE_TRAINING"])
        if hasattr(self, 'footerHints'): self.footerHints.setText(s["FOOTER_HINTS"])
        if hasattr(self, 'footerCredit'): self.footerCredit.setText(s["FOOTER_CREDIT"])
        
        # running_mode.ui elements (tabs)
        if hasattr(self, 'tabExamples'): self.tabExamples.setText(s["TAB_EXAMPLES"])
        if hasattr(self, 'tabFunctions'): self.tabFunctions.setText(s["TAB_FUNCTIONS"])
        if hasattr(self, 'tabWorkspace'): self.tabWorkspace.setText(s["TAB_WORKSPACE"])
        
        # Dynamic labels
        if hasattr(self, 'current_folder_type'):
            self.lblCurrentFolder.setText(s["WORKSPACE_TITLE"].format(self.current_folder_type))
        
        if hasattr(self, 'lblStatus') and self.lblStatus:
            self.lblStatus.setText(s["TERMINAL_READY"])
        
        if hasattr(self, 'btnRunCode') and self.btnRunCode:
            # Check actual process state rather than comparing strings which can mismatch with .ui versions
            is_running = self._run_process is not None
            self.btnRunCode.setText(s["BTN_STOP_CODE"] if is_running else s["BTN_RUN_CODE"])
            
        if hasattr(self, 'btnSaveFile') and self.btnSaveFile:
            self.btnSaveFile.setText(s["BTN_SAVE_FILE"])

        # Camera Start Button
        if hasattr(self, 'btnStartCamHeader') and self.btnStartCamHeader:
            self.btnStartCamHeader.setText(s["BTN_START_CAM"])
            
        # UI Block Headers
        if hasattr(self, 'hubTitle') and self.hubTitle: self.hubTitle.setText(s["HUB_TITLE"])
        if hasattr(self, 'editorTitle') and self.editorTitle: self.editorTitle.setText(s["EDITOR_TITLE"])
        if hasattr(self, 'lblCT') and self.lblCT: self.lblCT.setText(s["CONSOLE_TITLE"])
        if hasattr(self, 'btnClearConsole') and self.btnClearConsole: self.btnClearConsole.setText(s["BTN_CLEAR"])
        if hasattr(self, 'camTitle') and self.camTitle: self.camTitle.setText(s["CAM_TITLE"])
        if hasattr(self, 'resTitle') and self.resTitle: self.resTitle.setText(s["RES_TITLE"])

        # ORC Hub indicator
        if hasattr(self, 'lblOrcText') and self.lblOrcText:
            self.lblOrcText.setText(s.get("ORC_HUB_LABEL", "ORC Hub"))
        if hasattr(self, 'btnOrcRefresh') and self.btnOrcRefresh:
            self.btnOrcRefresh.setToolTip(s.get("ORC_REFRESH_TIP", "Re-check ORC Hub connection"))
        if hasattr(self, '_orc_connected'):
            self._update_orc_indicator()

        # Update variable count immediate display
        if hasattr(self, 'lblVarCount') and self.lblVarCount:
            count = len(self._live_vars) if hasattr(self, '_live_vars') else 0
            self.lblVarCount.setText(s["VAR_COUNT"].format(count))

        # Training Mode UI Elements
        if hasattr(self, 'training_mode_widget'):
            w = self.training_mode_widget
            titles = w.findChildren(QLabel, "panelTitle")
            if len(titles) >= 3:
                titles[0].setText(s["TR_DATA_CLASSES"])
                titles[1].setText(s["TR_CONFIG"])
                titles[2].setText(s["TR_FAST_CHECK"])
            
            btnRec = w.findChild(QPushButton, "btnRecognition")
            if btnRec: btnRec.setText(s["TR_RECOGNITION"])
            btnDet = w.findChild(QPushButton, "btnDetection")
            if btnDet: btnDet.setText(s["TR_DETECTION"])
            btnAdd = w.findChild(QPushButton, "btnAddClass")
            if btnAdd: btnAdd.setText(s["TR_ADD_CLASS"])
            btnStart = w.findChild(QPushButton, "btnStartTraining")
            if btnStart: btnStart.setText(s["TR_START"])
            
            lblDS = w.findChild(QLabel, "dsTitle")
            if lblDS: lblDS.setText(s["TR_DS_SUMMARY"])
            
            lblDSHint = w.findChild(QLabel, "lblImageCount")
            if lblDSHint: lblDSHint.setText(s["TR_DS_HINT"].format(0, 0)) # Reset to 0 for now
            
            lblBk = w.findChild(QLabel, "lblBackbone")
            if lblBk: lblBk.setText(s["TR_MODEL_BACKBONE"])
            
            lblEp = w.findChild(QLabel, "lblEpochs")
            if lblEp: lblEp.setText(s["TR_EPOCHS"])
            
            lblBa = w.findChild(QLabel, "lblBatch")
            if lblBa: lblBa.setText(s["TR_BATCH"])
            
            lblLr = w.findChild(QLabel, "lblLR")
            if lblLr: lblLr.setText(s["TR_LR"])
            
            lblOp = w.findChild(QLabel, "lblOpt")
            if lblOp: lblOp.setText(s["TR_OPT"])
            
            lblIs = w.findChild(QLabel, "lblImgSize")
            if lblIs: lblIs.setText(s["TR_IMG_SIZE"])
            
            lblNotReady = w.findChild(QLabel, "statusMsg")
            if lblNotReady: lblNotReady.setText(s["TR_NOT_READY"])
            lblNRHint = w.findChild(QLabel, "statusHint")
            if lblNRHint: lblNRHint.setText(s["TR_NOT_READY_HINT"])
            lblProg = w.findChild(QLabel, "progressHeader")
            if lblProg: lblProg.setText(s["TR_PROGRESS"])
            
            # Annotation Panel
            bbox_title = w.findChild(QLabel, "bboxTitle")
            if bbox_title: bbox_title.setText(s["TR_ANNOTATE_TITLE"])
            if hasattr(self, '_bbox_hint'):
                self._bbox_hint.setText(s["TR_ANNOTATE_HINT"])
            if hasattr(self, '_bbox_save_btn'):
                self._bbox_save_btn.setText(s["BTN_SAVE_BBOX"])

    # --- Terminal Methods ---
    def set_console_expanded(self, expanded: bool):
        self.consoleContainer.setVisible(expanded)
        self.collapsedConsoleBar.setVisible(not expanded)

    def clear_console(self):
        self.consoleBody.setPlainText(">>> Console cleared.")

    def log_to_console(self, message, is_error=False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = "#dc2626" if is_error else "#16a34a"
        formatted_msg = f"<span style='color:#64748b;'>[{timestamp}]</span> <span style='color:{color};'>{message}</span>"
        self.consoleBody.appendHtml(formatted_msg)
        self.consoleBody.verticalScrollBar().setValue(self.consoleBody.verticalScrollBar().maximum())

    # --- UI Navigation ---
    def show_running_mode(self):
        self.update_workspace_counts()
        self.mainStack.setCurrentIndex(0)

    def show_training_mode(self):
        self.mainStack.setCurrentIndex(1)

    # --- Workspace Logic ---
    def update_workspace_counts(self):
        """Sync card numbers with physical folders."""
        counts = {
            "Code": len(list(self.file_manager.code_dir.glob("*"))),
            "Data": len(list(self.file_manager.data_dir.glob("*"))),
            "Model": len(list(self.file_manager.model_dir.glob("*")))
        }
        self.running_mode_widget.findChild(QLabel, "countCode").setText(str(counts["Code"]))
        self.running_mode_widget.findChild(QLabel, "countData").setText(str(counts["Data"]))
        self.running_mode_widget.findChild(QLabel, "countModel").setText(str(counts["Model"]))

    def show_folder_contents(self, folder_type, subpath=None):
        """Load Open/Rename/Delete list for specific folder with a vibrant, kid-friendly card design."""
        folder_display = STRINGS[self.current_lang].get(folder_type.upper(), folder_type)
        if subpath:
            self.lblCurrentFolder.setText(f"{STRINGS[self.current_lang]['TAB_WORKSPACE']} / {folder_display} / {subpath}")
        else:
            self.lblCurrentFolder.setText(f"{STRINGS[self.current_lang]['TAB_WORKSPACE']} / {folder_display}")
            
        self.workspaceStack.setCurrentIndex(1)
        
        # Clear previous rows
        while self.workspaceFileListLayout.count() > 1:
            child = self.workspaceFileListLayout.takeAt(0)
            widget = child.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        # Theme colors based on folder_type
        themes = {
            "Code":  {"bg": "#eff6ff", "border": "#bfdbfe", "text": "#1e40af", "icon": "</>", "btn": "#3b82f6"},
            "Data":  {"bg": "#f0fdf4", "border": "#bbf7d0", "text": "#166534", "icon": "🗃️", "btn": "#22c55e"},
            "Model": {"bg": "#faf5ff", "border": "#e9d5ff", "text": "#6b21a8", "icon": "📦", "btn": "#a855f7"}
        }
        theme = themes.get(folder_type, themes["Code"])

        base_path = getattr(self.file_manager, f"{folder_type.lower()}_dir")
        path = base_path / subpath if subpath else base_path
        
        # Add 'Back' button if inside a subfolder
        if subpath:
            import pathlib
            sub_p = pathlib.Path(subpath)
            parent_subpath = str(sub_p.parent).replace("\\", "/") if str(sub_p.parent) != "." else None
            btn_back = QPushButton("🔙 Back" if parent_subpath else "🔙 Back to root Data folder")
            btn_back.setStyleSheet(f"background: {theme['btn']}; color: white; border-radius: 6px; padding: 8px; font-weight: bold; font-size: 13px;")
            btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_back.clicked.connect(lambda _, ps=parent_subpath: self.show_folder_contents(folder_type, subpath=ps))
            self.workspaceFileListLayout.insertWidget(self.workspaceFileListLayout.count() - 1, btn_back)
        
        # ─── DATA FOLDER (Image Gallery / Icon Mode) ───
        if folder_type == "Data":
            from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSizePolicy
            from PyQt5.QtCore import QSize
            from PyQt5.QtGui import QIcon
            
            list_widget = QListWidget()
            list_widget.setViewMode(QListWidget.ViewMode.IconMode)
            list_widget.setFlow(QListWidget.Flow.LeftToRight)
            list_widget.setWrapping(True)
            list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
            list_widget.setMovement(QListWidget.Movement.Static)
            list_widget.setIconSize(QSize(90, 90))
            list_widget.setGridSize(QSize(125, 140))
            list_widget.setWordWrap(True)
            list_widget.setSpacing(4)
            list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            list_widget.setStyleSheet(f"""
                QListWidget {{ 
                    background-color: {theme['bg']}; 
                    border: none; outline: none; border-radius: 8px;
                    padding: 4px;
                }}
            """)
            
            # Ensure the gallery takes up all available vertical space
            list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            for file_path in sorted(path.iterdir()):
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, str(file_path))
                
                if file_path.is_file():
                    pixmap = QPixmap(str(file_path))
                    if not pixmap.isNull():
                        # We use 90x90 as the new bounded size to fit 2 across
                        item.setIcon(QIcon(pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
                    else:
                        item.setText("📄") # Fallback for non-images
                elif file_path.is_dir():
                    # Render a standard beautiful directory icon at 1/4 area scale
                    from PyQt5.QtWidgets import QApplication, QStyle
                    from PyQt5.QtGui import QPainter
                    std_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
                    
                    folder_bg = QPixmap(90, 90)
                    folder_bg.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(folder_bg)
                    # Centers a 46x46 folder inside a 90x90 icon box
                    std_icon.paint(painter, 22, 22, 46, 46)
                    painter.end()
                    
                    item.setIcon(QIcon(folder_bg))
                
                # We place the filename at the bottom
                item.setText(file_path.name)
                item.setForeground(QColor(theme['text']))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                list_widget.addItem(item)
            
            # Handle click recursively
            def on_item_clicked(list_item):
                clicked_path = list_item.data(Qt.ItemDataRole.UserRole)
                import pathlib
                p = pathlib.Path(clicked_path)
                if p.is_dir():
                    try:
                        rel_path = p.relative_to(base_path)
                        self.show_folder_contents("Data", subpath=str(rel_path).replace("\\", "/"))
                    except ValueError:
                        self.show_folder_contents("Data", subpath=p.name)
            
            list_widget.itemClicked.connect(on_item_clicked)

            
            # Insert before the spacer and set stretch to 1 to fill space
            idx = self.workspaceFileListLayout.count() - 1
            self.workspaceFileListLayout.insertWidget(idx, list_widget)
            self.workspaceFileListLayout.setStretch(idx, 1)
            return

        # ─── CODE & MODEL FOLDERS (Standard List Cards) ───
        for file_path in sorted(path.iterdir()):
            if file_path.is_file():
                card = QFrame()
                card.setObjectName("FileCard")
                card.setStyleSheet(f"""
                    QFrame#FileCard {{ 
                        background-color: {theme['bg']}; 
                        border: 1px solid {theme['border']}; 
                        border-radius: 8px; 
                        padding: 2px;
                        margin: 0px 2px;
                    }}
                    QFrame#FileCard:hover {{
                        border: 2px solid {theme['btn']};
                        background-color: white;
                    }}
                """)
                
                row_layout = QHBoxLayout(card)
                row_layout.setContentsMargins(8, 2, 8, 2)
                row_layout.setSpacing(6)
                
                # Icon + Name
                icon_lbl = QLabel(theme['icon'])
                icon_lbl.setFont(QFont("Segoe UI", 12))
                icon_lbl.setFixedWidth(24)
                icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                icon_lbl.setStyleSheet(f"color: {theme['text']}; background: transparent;")
                
                name_lbl = QLabel(file_path.name)
                name_lbl.setStyleSheet(f"color: {theme['text']}; font-weight: bold; font-size: 13px; background: transparent;")
                
                # Action Buttons (Icon Only)
                btn_open = self._icon_action_button("📂", "Open",  "#43CF0C")
                btn_rename = self._icon_action_button("🖊", "Rename", "#C23DD9")
                btn_delete = self._icon_action_button("🗑️", "Delete", "#E82727")
                btn_copy = self._icon_action_button("📋", "Copy Path", "#0EA5E9")
                btn_copy.setVisible(folder_type in ["Model", "Code", "Projects"])

                # Smart Permission Layer Mapping
                if folder_type == "Model":
                    btn_open.hide() # Never open binary models in text editor
                    name_lower = file_path.name.lower()
                    
                    # Protect curriculum base models!
                    if "yunet" in name_lower or "yolo" in name_lower:
                        btn_rename.hide()
                        btn_delete.hide()

                btn_open.clicked.connect(lambda _, p=file_path: self.load_file_from_path(p))
                btn_rename.clicked.connect(lambda _, p=file_path, t=folder_type: self.handle_rename(p, t))
                btn_delete.clicked.connect(lambda _, p=file_path, t=folder_type: self.handle_delete(p, t))
                btn_copy.clicked.connect(lambda _, p=file_path, t=folder_type: self.handle_copy_path(p, t))

                # Container for Buttons to keep them tight
                btn_container = QWidget()
                btn_container.setStyleSheet("background: transparent;")
                btn_layout = QHBoxLayout(btn_container)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setSpacing(0) # No space between buttons
                
                btn_layout.addWidget(btn_open)
                btn_layout.addWidget(btn_copy)
                btn_layout.addWidget(btn_rename)
                btn_layout.addWidget(btn_delete)
                
                row_layout.addWidget(icon_lbl)
                row_layout.addWidget(name_lbl)
                row_layout.addStretch()
                row_layout.addWidget(btn_container)
                
                self.workspaceFileListLayout.insertWidget(self.workspaceFileListLayout.count() - 1, card)

    def _icon_action_button(self, icon, tooltip, color):
        """Helper to create vibrant icon-only action buttons."""
        btn = QPushButton(icon)
        btn.setToolTip(tooltip)
        btn.setFixedSize(28, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #E3DEFC;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
                color: {color};
                border: 1px solid #4D0B6E;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: white;
                border: none;
            }}
        """)
        return btn

    def load_file_from_path(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.monacoPlaceholder.setPlainText(f.read())
        self.add_tab(path.name)

    def handle_rename(self, path, folder_type):
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=path.name)
        if ok and new_name:
            path.rename(path.parent / new_name)
            self.show_folder_contents(folder_type)

    def handle_delete(self, path, folder_type):
        if QMessageBox.question(self, "Confirm", f"Delete {path.name}?") == QMessageBox.StandardButton.Yes:
            path.unlink()
            self.show_folder_contents(folder_type)
            self.update_workspace_counts()

    def handle_copy_path(self, path, folder_type):
        # Format: projects/model/file.onnx
        # folder_type is "Model", "Code", etc.
        folder_name = folder_type.lower()
        rel_path = f"projects/{folder_name}/{path.name}"
        
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(rel_path)
        self.log_to_console(f"📋 Copied path: {rel_path}")

    def setup_file_explorer(self):
        self.file_model = QFileSystemModel()
        project_path = str(self.file_manager.files_dir)
        self.file_model.setRootPath(project_path)
        self.file_model.setNameFilters(["*.py", "*.json", "*.txt"])
        self.file_model.setNameFilterDisables(False)
        
        self.fileTreeView.setModel(self.file_model)
        self.fileTreeView.setRootIndex(self.file_model.index(project_path))
        self.fileTreeView.setColumnHidden(1, True)
        self.fileTreeView.setColumnHidden(2, True)
        self.fileTreeView.setColumnHidden(3, True)
        self.fileTreeView.doubleClicked.connect(self.load_selected_file_from_tree)

    def load_selected_file_from_tree(self, index):
        if self.file_model.isDir(index): return
        file_path = self.file_model.filePath(index)
        filename = os.path.basename(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if self.monacoPlaceholder: self.monacoPlaceholder.setPlainText(content)
            self.add_tab(filename)
            self.current_open_file = filename
        except Exception as e:
            self.log_to_console(f"Error loading file: {e}", True)

    # --- Curriculum Discovery ---
    def populate_curriculum_hub(self):
        """Scan curriculum folder and generate cards dynamically."""
        if not self.hubContentLayout: return
        
        # 1. Clear existing items (cards) but keep the spacer at the end
        while self.hubContentLayout.count() > 1:
            child = self.hubContentLayout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        # 2. Find all .py files in curriculum directory
        curr_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "curriculum")
        if not os.path.exists(curr_dir): return
        
        for name in sorted(os.listdir(curr_dir)):
            if name.endswith(".py"):
                file_path = os.path.join(curr_dir, name)
                metadata = self._parse_lesson_metadata(file_path)
                
                # 3. Create a card and insert it before the spacer
                title = metadata.get(f"TITLE_{self.current_lang.upper()}", metadata.get("TITLE", name))
                desc = metadata.get(f"DESC_{self.current_lang.upper()}", metadata.get("DESC", "Custom curriculum script."))
                
                card = CurriculumCard(
                    filename=name,
                    title=title,
                    level=metadata.get("LEVEL", "Beginner"),
                    icon=metadata.get("ICON", "📄"),
                    color=metadata.get("COLOR", "#7c3aed"),
                    desc=desc,
                    on_load_click=self.load_curriculum_example
                )
                self.hubContentLayout.insertWidget(self.hubContentLayout.count() - 1, card)

    def _parse_lesson_metadata(self, path):
        """Extract # TITLE, # LEVEL, # ICON, # COLOR, # DESC from file header."""
        meta = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                # Only read top 20 lines for speed & translations
                for _ in range(20):
                    line = f.readline()
                    if not line: break
                    # Match pattern like: # TITLE: Face Detection or # TITLE_VI: Phát hiện khuôn mặt
                    match = re.search(r"^#\s*(TITLE|LEVEL|ICON|COLOR|DESC|TITLE_VI|DESC_VI)\s*:\s*(.*)$", line, re.I)
                    if match:
                        key = match.group(1).upper()
                        val = match.group(2).strip()
                        meta[key] = val
        except:
            pass
        return meta

    # --- Tab & File Operations ---
    def load_curriculum_example(self, filename: str):
        """Generic loader for curriculum example files."""
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "curriculum", filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
            self.monacoPlaceholder.setPlainText(code_content)
            self.current_open_file = filename
            
                # Clean display name for the console
            display_name = filename.replace(".py", "").replace("_", " ").title()
            self.log_to_console(f"Successfully loaded {display_name} example.")
            
            # Switch to 'main.py' logic for easy tab management if we want it as a new tab?
            # Actually, let's just let it be for now since it works as a direct editor load.
            self.add_tab(filename, is_code=True)
            
        except FileNotFoundError:
            self.log_to_console(f"Example file {filename} not found.", True)
        except Exception as e:
            self.log_to_console(f"Error loading example: {e}", True)

    def create_new_file(self):
        filename, ok = QInputDialog.getText(self, "Create New File", "Enter filename (without .py):")
        if ok and filename:
            result = self.file_manager.create_file(filename, folder='Code')
            if result['success']:
                self.add_tab(filename if filename.endswith('.py') else filename + '.py')
                self.log_to_console(f"File created: {result['path']}")
            else:
                self.log_to_console(f"Error: {result['message']}", True)

    def save_current_file(self):
        """Save the current editor content back to disk."""
        if not self.current_open_file:
            self.log_to_console("Nothing to save — no file is open.", is_error=True)
            return

        code_text = self.monacoPlaceholder.toPlainText()
        result = self.file_manager.save_file(self.current_open_file, code_text, folder='Code')

        if result['success']:
            self.log_to_console(f"💾 Saved: {self.current_open_file}")
            # Brief visual feedback on the save button
            if self.btnSaveFile:
                original = self.btnSaveFile.text()
                self.btnSaveFile.setText("✅ Saved!")
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(1200, lambda: self.btnSaveFile.setText(original))
        else:
            self.log_to_console(f"Save failed: {result['message']}", is_error=True)

    def add_tab(self, filename: str, is_code: bool = False):
        if filename in self.open_tabs:
            self.set_active_tab(filename)
            self.load_file_by_tab(filename)
            return
            
        self.open_tabs.append(filename)
        
        # Composite tab widget
        tab_widget = QFrame()
        tab_widget.setObjectName("TabWidget")
        layout = QHBoxLayout(tab_widget)
        layout.setContentsMargins(2, 1, 2, 1)
        layout.setSpacing(2)
        
        # Title Button
        btn_title = QPushButton(filename)
        btn_title.setObjectName("TabTitle")
        btn_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        btn_title.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_title.clicked.connect(lambda _, n=filename: self.load_file_by_tab(n))
        
        # Close Button
        btn_close = QPushButton("×")
        btn_close.setObjectName("TabClose")
        btn_close.setFixedSize(18, 18)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(lambda _, n=filename: self.close_tab(n))
        
        layout.addWidget(btn_title)
        layout.addWidget(btn_close)
        
        # Insert before the spacer
        self.tabContainer.layout().insertWidget(self.tabContainer.layout().count() - 1, tab_widget)
        self.tab_buttons.append((filename, tab_widget))
        self.set_active_tab(filename)

    def close_tab(self, filename: str):
        if filename not in self.open_tabs: return
        
        # 1. Position management
        idx = self.open_tabs.index(filename)
        self.open_tabs.pop(idx)
        
        # 2. UI destruction
        for name, widget in self.tab_buttons[:]:
            if name == filename:
                widget.setParent(None)
                widget.deleteLater()
                self.tab_buttons.remove((name, widget))
                break
        
        # 3. Switch focus
        if self.open_tabs:
            # Pick neighbor
            new_idx = min(idx, len(self.open_tabs) - 1)
            target = self.open_tabs[new_idx]
            self.load_file_by_tab(target)
        else:
            self.current_open_file = None
            self.monacoPlaceholder.setPlainText("")
            self.log_to_console("All tabs closed.")

    def set_active_tab(self, filename: str):
        self.current_open_file = filename
        for name, widget in self.tab_buttons:
            title = widget.findChild(QPushButton, "TabTitle")
            close = widget.findChild(QPushButton, "TabClose")
            
            if name == filename:
                widget.setStyleSheet("QFrame#TabWidget { background-color: #2563eb; border-radius: 6px; }")
                if title: title.setStyleSheet("color: white; background: transparent; border: none; text-align: left; padding: 2px;")
                if close: close.setStyleSheet("color: white; background: rgba(255,255,255,0.1); border-radius: 9px; border: none; font-size: 14px; font-weight: bold;")
            else:
                widget.setStyleSheet("QFrame#TabWidget { background-color: #374151; border-radius: 6px; }")
                if title: title.setStyleSheet("color: #94a3b8; background: transparent; border: none; text-align: left; padding: 2px;")
                if close: close.setStyleSheet("color: transparent; background: transparent; border: none;") # Hide X on inactive tabs for cleaner look? No, user might want to close them
                # Let's keep it visible but subtle
                if close: close.setStyleSheet("color: #64748b; background: transparent; border: none; font-size: 14px;")

    def create_new_tab(self):
        filename, ok = QInputDialog.getText(self, "New Python Tab", "Enter script name (without .py):")
        if ok and filename:
            # Ensure we have the .py extension for consistent lookups
            full_name = filename if filename.endswith('.py') else filename + '.py'
            
            result = self.file_manager.create_file(filename, folder='Code')
            if result['success']:
                self.add_tab(full_name)
                # 🚀 THE FIX: Tell the UI to load the template we just saved to disk
                self.load_file_by_tab(full_name) 
                self.log_to_console(f"File created: {result['path']}")
            else:
                self.log_to_console(f"Error: {result['message']}", True)
                

    def load_file_by_tab(self, filename: str):
        result = self.file_manager.read_file(filename, folder='Code')
        if not result['success']: result = self.file_manager.read_file(filename, folder='Projects')
        if result['success']:
            if self.monacoPlaceholder:
                self.monacoPlaceholder.setPlainText(result['content'])
            self.set_active_tab(filename)

    # ──────────────────────────────────────────────────────────
    #  RUN CODE  (non-blocking QProcess, live output + VAR: parse)
    # ──────────────────────────────────────────────────────────

    def save_and_run_code(self):
        """Toggle: start a new run OR stop the currently running process."""
        # ── STOP mode ──────────────────────────────────────────
        if self._run_process is not None:
            self._stop_run()
            return

        # ── START mode ─────────────────────────────────────────
        if not self.current_open_file:
            self.log_to_console("Error: No file loaded to run.", is_error=True)
            return

        code_text = self.monacoPlaceholder.toPlainText()
            
        filename  = self.current_open_file

        # 1. Save a run-copy to disk
        self.file_manager.save_run_copy(filename, code_text)
        run_path = self.file_manager.get_run_file_path(filename)

        if not run_path:
            self.log_to_console(f"Error: cannot locate run file for '{filename}'.", is_error=True)
            return

        # 2. Visual feedback — turn button red / show Stop label
        if self.btnRunCode:
            self.btnRunCode.setText("⏹ Stop")
            self.btnRunCode.setStyleSheet(
                "QPushButton { background-color: #dc2626; color: white; "
                "border-radius: 6px; font-weight: bold; padding: 6px 12px; }"
                "QPushButton:hover { background-color: #b91c1c; }"
            )

        self._live_vars.clear()
        self.log_to_console(f"▶ Running {filename}...")
        if self.lblTimestamp:
            self.lblTimestamp.setText(datetime.now().strftime("%H:%M:%S"))

        # ── Dashboard UI Pivot ──────────────────────────────────
        # 1. Collapse the Learning Hub (Left Column)
        if self.mainSplitter:
            self.mainSplitter.setSizes([0, 800, 400])
        # 2. Split Right Column (Camera 2/3 vs Results 1/3)
        if self.rightSplitter:
            self.rightSplitter.setSizes([600, 300])
        # ────────────────────────────────────────────────────────

        # 3. Launch with QProcess (non-blocking)
        self._run_process = QProcess(self)
        
        # FIX: Set working directory to project root so 'src' can be found
        project_root = os.path.dirname(os.path.abspath(__file__))
        self._run_process.setWorkingDirectory(project_root)
        
        # FIX: Ensure project root is in PYTHONPATH for the child process
        # This allows internal modules like 'src.modules...' to be imported correctly
        from PyQt5.QtCore import QProcessEnvironment
        env = QProcessEnvironment.systemEnvironment()
        python_path = env.value("PYTHONPATH", "")
        if python_path:
            env.insert("PYTHONPATH", f"{project_root}{os.pathsep}{python_path}")
        else:
            env.insert("PYTHONPATH", project_root)
        self._run_process.setProcessEnvironment(env)

        self._run_process.setProgram(sys.executable)
        self._run_process.setArguments([str(run_path)])

        # Stream stdout live
        self._run_process.readyReadStandardOutput.connect(self._on_stdout)
        # Stream stderr live
        self._run_process.readyReadStandardError.connect(self._on_stderr)
        # Cleanup on finish
        self._run_process.finished.connect(self._on_process_finished)

        self._stdout_buf = ""
        self._run_process.start()

        if not self._run_process.waitForStarted(3000):
            self.log_to_console("Error: Process could not be started.", is_error=True)
            self._reset_run_button()
            self._run_process = None

    def _stop_run(self):
        """Kill the running QProcess."""
        if self._run_process:
            self._run_process.kill()
            self._run_process.waitForFinished(2000)
            self.log_to_console(STRINGS[self.current_lang]["HINT_RUN_STOPPED"], is_error=True)

    def _on_stdout(self):
        """Called whenever the child process writes to stdout."""
        if not self._run_process:
            return
        raw = bytes(self._run_process.readAllStandardOutput()).decode("utf-8", errors="replace")

        # Buffer partial lines: large IMG: payloads may arrive split across reads
        if not hasattr(self, '_stdout_buf'):
            self._stdout_buf = ""
        self._stdout_buf += raw

        # Only process complete lines (ending with \n); keep the rest buffered
        while "\n" in self._stdout_buf:
            line, self._stdout_buf = self._stdout_buf.split("\n", 1)
            line = line.rstrip()
            if not line:
                continue
            if line.startswith("VAR:"):
                # Format: VAR:<Name>:<Value>
                parts = line.split(":", 2)
                if len(parts) == 3:
                    _, var_name, var_value = parts
                    self._live_vars[var_name.strip()] = var_value.strip()
                    self._flush_vars_to_panel()
            elif line.startswith("IMG:"):
                # Format: IMG:<base64_data>
                try:
                    img_data = line[4:].strip()
                    if img_data:
                        pixmap = self._decode_base64_to_pixmap(img_data)
                        if pixmap and not pixmap.isNull():
                            self.camDisplay.setPixmap(pixmap)
                except Exception:
                    pass  # Silently drop corrupt frames
            else:
                self.log_to_console(line)

    def _decode_base64_to_pixmap(self, base64_str):
        try:
            data = base64.b64decode(base64_str)
            image = QImage.fromData(data)
            return QPixmap.fromImage(image)
        except:
            return None

    _SUPPRESSED_STDERR = ("Corrupt JPEG data", "premature end of data segment",
                          "Failed to open file", "/sys/class/drm")

    def _on_stderr(self):
        """Called whenever the child process writes to stderr."""
        if not self._run_process:
            return
        raw = bytes(self._run_process.readAllStandardError()).decode("utf-8", errors="replace")
        for line in raw.splitlines():
            line = line.rstrip()
            if line and not any(s in line for s in self._SUPPRESSED_STDERR):
                self.log_to_console(line, is_error=True)

    def _on_process_finished(self, exit_code, exit_status):
        """Called when the QProcess ends (naturally or was killed)."""
        msg = STRINGS[self.current_lang]["HINT_RUN_FINISHED"].format(exit_code)
        self.log_to_console(msg)
        if self.lblTimestamp:
            self.lblTimestamp.setText(datetime.now().strftime("%H:%M:%S"))
        self._run_process = None
        self._reset_run_button()
        self._flush_vars_to_panel()

    def _flush_vars_to_panel(self):
        """Convert accumulated VAR: dict into results-panel cards."""
        var_list = [
            {"name": k, "type": type(v).__name__, "value": v}
            for k, v in self._live_vars.items()
        ]
        update_results_panel(self, var_list)
        if self.lblVarCount:
            msg = STRINGS[self.current_lang]["VAR_COUNT"].format(len(var_list))
            self.lblVarCount.setText(msg)

    def _reset_run_button(self):
        """Restore the Run Code button and reset dashboard layout."""
        if self.btnRunCode:
            self.btnRunCode.setText("▶ Run")
            self.btnRunCode.setStyleSheet("")
            
        # Restore original dashboard layout (Show Learning Hub)
        if self.mainSplitter:
            self.mainSplitter.setSizes([300, 600, 300])
        if self.rightSplitter:
            self.rightSplitter.setSizes([400, 400])
            
        # Optional: Clear camera preview if it's just black/stuck
        if hasattr(self, 'camDisplay'):
            self.camDisplay.clear()
            self.camDisplay.setText("Camera Ready")
            self.camDisplay.setStyleSheet("color: #4b5563; background: black; font-weight: bold;")

    def on_function_dropped(self, function_id, drop_pos=None):
        # Determine which editor received the drop
        editor = self.monacoPlaceholder
            
        # 1. Get code & find what function usage we need
        current_code = editor.toPlainText()
        result = prepare_code_injection(function_id, current_code)
        
        if not result:
            return

        # 2. Add imports if needed (Always at line 0)
        import_added = False
        if result["add_import"]:
            # Check if import already exists (prevent duplicates from being added by multiple drops)
            if result["import_line"] not in current_code:
                editor.insertAt(f"{result['import_line']}\n", 0, 0)
                self.log_to_console(STRINGS[self.current_lang]["HINT_ADDED_IMPORT"].format(result['import_line']))
                import_added = True

        # 3. Extract Target Coordinates
        if not drop_pos:
            line, col = editor.getCursorPosition()
        else:
            line, col = drop_pos
            # Offset if we added an import line
            if import_added: line += 1

        # 4. Determine target indentation level based on Ghost Block zones (0, 4, 8)
        # We use the logical column 'col' passed from the editor's pixel calculation
        indent_level = 0
        if col >= 4 and col < 8: 
            indent_level = 1
        elif col >= 8: 
            indent_level = 2
        
        indent_prefix = "    " * indent_level
        
        # 5. Format the Snippet
        snippet = result["snippet"]
        lines = snippet.splitlines()
        indented_lines = []
        for i, l in enumerate(lines):
            # Apply the full indentation to every line in the snippet
            indented_lines.append(indent_prefix + l)
        
        snippet_formatted = "\n".join(indented_lines)

        # 6. Smart Injection: Occupied Line Protection
        # We always want the snippet to have its own line.
        target_line_text = editor.text(line).strip()
        
        if target_line_text:
            # If the targeted line has code, we insert BELOW it as a new line
            self.monacoPlaceholder.insertAt("\n" + snippet_formatted, line, len(self.monacoPlaceholder.text(line).rstrip()))
        else:
            # If the line is empty, we replace it with the correctly indented snippet
            # We clear the existing whitespace if any, then insert
            self.monacoPlaceholder.setSelection(line, 0, line, len(self.monacoPlaceholder.text(line)))
            self.monacoPlaceholder.replaceSelectedText(snippet_formatted)
            
        self.log_to_console(STRINGS[self.current_lang]["HINT_INJECTED"].format(function_id))
            
    # --- New Drop Event Handlers ---

    def switch_mode(self, index):
        """Toggle between Running Mode (0) and Training Mode (1)."""
        self.mainStack.setCurrentIndex(index)
        # Let Qt handle the :checked style from the .ui stylesheet automatically
        if index == 1:
            self.setup_training_mode_logic()

    def setup_training_mode_logic(self):
        """Configure all signals for the Training Mode UI."""
        if hasattr(self, '_training_init_done'): return
        
        # Mode state
        self._training_task = "recognition"  # 'recognition' or 'detection'
        self._class_data = []  # list of class info dicts
        self._bbox_panel_visible = False
        self._active_camera_class = None
        self._cam_cap = None  # cv2.VideoCapture
        self._cam_timer = QTimer()
        self._cam_timer.setInterval(33)  # ~30fps
        self._cam_timer.timeout.connect(self._update_cam_frame)
        self._data_root = os.path.join("projects", "data")
        os.makedirs(self._data_root, exist_ok=True)
        
        self._current_project_name = ""
        self._project_initialized = False
        self._train_process = None
        self._training_is_running = False
        self._last_exported_engine = None
        self._train_dot_count = 0
        self._train_dot_timer = QTimer(self)
        self._train_dot_timer.setInterval(500)
        self._train_dot_timer.timeout.connect(self._animate_training_dots)

        
        # Wire Recognition / Detection toggle (Group 1 - Task)
        from PyQt5.QtWidgets import QButtonGroup
        self.task_group = QButtonGroup(self)
        btnRec = self.training_mode_widget.findChild(QPushButton, "btnRecognition")
        btnDet = self.training_mode_widget.findChild(QPushButton, "btnDetection")
        
        if btnRec and btnDet:
            self.task_group.addButton(btnRec)
            self.task_group.addButton(btnDet)
            self.task_group.setExclusive(True)
            
            btnRec.setChecked(self._training_task == "recognition")
            btnDet.setChecked(self._training_task == "detection")
            
            btnRec.clicked.connect(lambda: self._set_task_type("recognition"))
            btnDet.clicked.connect(lambda: self._set_task_type("detection"))

        # ─── 🏗️ PROJECT NAME SECTION (New) ───
        lhLayout = self.training_mode_widget.findChild(QVBoxLayout, "lhLayout")
        if lhLayout:
            # Create Project Name Row
            self.projRow = QFrame()
            self.projRow.setObjectName("projectRow")
            self.projLayout = QHBoxLayout(self.projRow)
            self.projLayout.setContentsMargins(0, 0, 0, 0)
            self.projLayout.setSpacing(6)
            
            lblProj = QLabel("Project name:")
            lblProj.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
            
            self.editProjName = QLineEdit()
            self.editProjName.setPlaceholderText("Enter name...")
            self.editProjName.setFixedHeight(28)
            self.editProjName.setStyleSheet("""
                QLineEdit { 
                    background: rgba(255, 255, 255, 0.9); border: 2px solid #ef4444; 
                    border-radius: 6px; padding: 2px 8px; font-size: 14px;
                }
            """)
            
            self.btnProjCheck = QPushButton("✓") # V-check button
            self.btnProjCheck.setFixedSize(28, 28)
            self.btnProjCheck.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btnProjCheck.setStyleSheet("""
                QPushButton { 
                    background: #10b981; color: white; border-radius: 6px; font-weight: bold; font-size: 14px;
                }
                QPushButton:hover { background: #059669; }
                QPushButton:disabled { background: #94a3b8; }
            """)
            
            self.btnProjReload = QPushButton("📂")
            self.btnProjReload.setFixedSize(28, 28)
            self.btnProjReload.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btnProjReload.setToolTip("Reload existing project")
            self.btnProjReload.setStyleSheet("""
                QPushButton {
                    background: #f59e0b; color: white; border-radius: 6px; font-size: 14px;
                }
                QPushButton:hover { background: #d97706; }
                QPushButton:disabled { background: #94a3b8; }
            """)

            self.projLayout.addWidget(lblProj)
            self.projLayout.addWidget(self.editProjName, 1)
            self.projLayout.addWidget(self.btnProjCheck)
            self.projLayout.addWidget(self.btnProjReload)

            # Insert between Task Toggle and Size Toggle
            lhLayout.insertWidget(2, self.projRow)

            # Connect Logic
            self.btnProjCheck.clicked.connect(self._init_project_folder)
            self.btnProjReload.clicked.connect(self._show_reload_dialog)
            self.editProjName.textChanged.connect(self._validate_project_name_visual)


        # Wire Capture Size toggle (Group 2 - Resolution)
        self.size_group = QButtonGroup(self)
        self._capture_size = 640
        self.btnCapSize320 = self.training_mode_widget.findChild(QPushButton, "btnCapSize320")
        self.btnCapSize640 = self.training_mode_widget.findChild(QPushButton, "btnCapSize640")

        self.lblStaticImgSize = self.training_mode_widget.findChild(QLabel, "lblStaticImgSize")
        
        if self.btnCapSize320 and self.btnCapSize640:
            self.size_group.addButton(self.btnCapSize320)
            self.size_group.addButton(self.btnCapSize640)
            self.size_group.setExclusive(True)
            
            self.btnCapSize640.setChecked(True)
            
            def set_size_unified(size):
                self._set_capture_size(size)
                if self.lblStaticImgSize:
                    text = "320x320 (Fast)" if size == 320 else "640x640 (High Detail)"
                    self.lblStaticImgSize.setText(text)
            
            self.btnCapSize320.clicked.connect(lambda: set_size_unified(320))
            self.btnCapSize640.clicked.connect(lambda: set_size_unified(640))

        
        # Wire Add Class
        self.btnAddClass = self.training_mode_widget.findChild(QPushButton, "btnAddClass")
        if self.btnAddClass: self.btnAddClass.clicked.connect(self.add_training_class)


        
        # Wire Training Start
        self.btnStartTraining = self.training_mode_widget.findChild(QPushButton, "btnStartTraining")

        if self.btnStartTraining:
            self.btnStartTraining.clicked.connect(self._start_training)

        # Dataset Labels
        self.lblImageCountLarge = self.training_mode_widget.findChild(QLabel, "lblImageCountLarge")
        self.lblDsHint = self.training_mode_widget.findChild(QLabel, "lblDsHint")

        # Metrics Panel & Charts
        self.metricsPanel = self.training_mode_widget.findChild(QFrame, "metricsPanel")
        self.statusPlaceholder = self.training_mode_widget.findChild(QFrame, "statusPlaceholder")
        self.epochBarFrame = self.training_mode_widget.findChild(QFrame, "epochBarFrame")
        self.progEpoch = self.training_mode_widget.findChild(QProgressBar, "progEpoch")
        self.lblEpochCounter = self.training_mode_widget.findChild(QLabel, "lblEpochCounter")
        
        self.lblValueAccuracy = self.training_mode_widget.findChild(QLabel, "lblValueAccuracy")
        self.lblValueLoss = self.training_mode_widget.findChild(QLabel, "lblValueLoss")
        # Note: Val Acc and mAP removed from UI for space, handled safely below
        self.txtTrainLog = self.training_mode_widget.findChild(QPlainTextEdit, "txtTrainLog")

        # Console toggle button — collapsed by default
        self.btnToggleConsole = QPushButton("▶ Console")
        self.btnToggleConsole.setFixedHeight(22)
        self.btnToggleConsole.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnToggleConsole.setStyleSheet("""
            QPushButton {
                background: #e2e8f0; color: #475569; border: 1px solid #cbd5e1;
                border-radius: 6px; font-size: 10px; font-weight: bold; padding: 2px 8px;
            }
            QPushButton:hover { background: #cbd5e1; }
        """)
        self.btnToggleConsole.clicked.connect(self._toggle_train_console)
        # Insert toggle button before txtTrainLog in the progress layout
        if self.txtTrainLog and self.txtTrainLog.parentWidget():
            parent_layout = self.txtTrainLog.parentWidget().layout()
            if parent_layout:
                idx = parent_layout.indexOf(self.txtTrainLog)
                if idx >= 0:
                    parent_layout.insertWidget(idx, self.btnToggleConsole)
        # Default: collapsed
        if self.txtTrainLog:
            self.txtTrainLog.setVisible(False)

        # Embed Accuracy Chart (single chart — accuracy is the key metric for students)
        chart_acc_frame = self.training_mode_widget.findChild(QFrame, "chartAcc")

        self.canvasLoss = None
        self.canvasAcc = None
        if chart_acc_frame:
            chart_acc_frame.setLayout(QVBoxLayout())
            chart_acc_frame.layout().setContentsMargins(4, 2, 4, 2)
            chart_acc_frame.setMinimumHeight(300) 
            self.canvasAcc = TrainingCanvas(chart_acc_frame, title="Accuracy (mAP50) Over Epochs", ylabel="Accuracy (%)", color_train="#10b981", color_val="#f59e0b")
            chart_acc_frame.layout().addWidget(self.canvasAcc)

        self._training_total_epochs = 20
        
        # Training Camera Display (Right Panel) - Standard QLabel
        self.trCamDisplay = QLabel()
        self.trCamDisplay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.trCamDisplay.setStyleSheet("background: black; border-radius: 12px;")
        self.trCamDisplay.setVisible(False)
        self.trCamDisplay.setScaledContents(False)  # Prevents unnatural stretching
        self.trCamDisplay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Handle Enter to capture
        self.trCamDisplay.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        fvLayout = self.training_mode_widget.findChild(QVBoxLayout, "fvContentLayout")
        if fvLayout:
            fvLayout.insertWidget(0, self.trCamDisplay)

        # Validation buttons (hidden until training completes)
        self.btnStopValidation = QPushButton("🎯  Stop Validation")
        self.btnStopValidation.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnStopValidation.setVisible(False)
        self.btnStopValidation.setFixedHeight(36)
        self.btnStopValidation.setStyleSheet("""
            QPushButton {
                background: #ef4444; color: white; border-radius: 8px;
                font-weight: bold; font-size: 14px; padding: 6px 12px;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        self.btnStopValidation.clicked.connect(self._stop_fast_validation)

        self.btnSaveModel = QPushButton("💾  Save Model")
        self.btnSaveModel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnSaveModel.setVisible(False)
        self.btnSaveModel.setFixedHeight(36)
        self.btnSaveModel.setStyleSheet("""
            QPushButton {
                background: #10b981; color: white; border-radius: 8px;
                font-weight: bold; font-size: 14px; padding: 6px 12px;
            }
            QPushButton:hover { background: #059669; }
        """)
        self.btnSaveModel.clicked.connect(self._save_trained_model)

        if fvLayout:
            fvLayout.addWidget(self.btnStopValidation)
            fvLayout.addWidget(self.btnSaveModel)

        self._val_process = None
        self._local_model_path = None
        self._val_stdout_buf = ""

        # Simulation Timer

        # Build BBox collapsible panel (hidden by default)
        self._build_bbox_panel()
        
        # Add 2 default classes
        self.add_training_class("Class 1")
        self.add_training_class("Class 2")
        
        self._training_init_done = True
        
        # Initially lock features until project is named
        if not hasattr(self, '_project_initialized') or not self._project_initialized:
            QTimer.singleShot(100, self._update_project_ui_lock)

        
        # Initially lock features until project is named
        QTimer.singleShot(100, self._update_project_ui_lock)

    def _validate_project_name_visual(self, text):
        """Highlight red if empty, normal if has text."""
        if not text.strip():
            self.editProjName.setStyleSheet("QLineEdit { background: rgba(255, 255, 255, 0.9); border: 2px solid #ef4444; border-radius: 6px; padding: 2px 8px; }")
        else:
            self.editProjName.setStyleSheet("QLineEdit { background: white; border: 2px solid #3b82f6; border-radius: 6px; padding: 2px 8px; }")

    def _init_project_folder(self):
        """Create the project directory and unlock features."""
        name = self.editProjName.text().strip()
        if not name:
            self.log_to_console("Error: Project name cannot be empty.")
            return
            
        # Path logic
        base_path = os.path.join(self._data_root, name)

        # Confirm overwrite if folder has content
        try:
            if os.path.exists(base_path) and os.listdir(base_path):
                reply = QMessageBox.question(
                    self, "Overwrite Project?",
                    f"Project '{name}' already exists with data.\n\nDelete it and start fresh?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            if os.path.exists(base_path):
                import shutil
                shutil.rmtree(base_path)
            os.makedirs(base_path, exist_ok=True)
            
            self._current_project_name = name
            self._project_initialized = True
            
            # Disable project entry
            self.editProjName.setDisabled(True)
            self.btnProjCheck.setDisabled(True)
            if hasattr(self, 'btnProjReload'):
                self.btnProjReload.setDisabled(True)
            self.editProjName.setStyleSheet("QLineEdit { background: #f1f5f9; border: 1px solid #cbd5e1; color: #64748b; border-radius: 6px; padding: 2px 8px; }")

            self.log_to_console(f"Project '{name}' initialized. Data will be saved in: /projects/data/{name}/")
            self._update_project_ui_lock()
            
        except Exception as e:
            self.log_to_console(f"Error creating project folder: {str(e)}")

    def _show_reload_dialog(self):
        """Show a dialog to select an existing detection project to reload."""
        candidates = []
        if os.path.isdir(self._data_root):
            for entry in sorted(os.listdir(self._data_root)):
                full = os.path.join(self._data_root, entry)
                if os.path.isdir(full):
                    has_images = any(
                        f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))
                        for f in os.listdir(full)
                    )
                    if has_images:
                        candidates.append(entry)

        if not candidates:
            QMessageBox.information(self, "No Projects", "No existing projects with images found in projects/data/.")
            return

        name, ok = QInputDialog.getItem(self, "Reload Project", "Select a project:", candidates, 0, False)
        if ok and name:
            self._reload_project(name)

    def _reload_project(self, project_name):
        """Reload an existing detection project: images, class names, and annotation status."""
        project_path = os.path.join(self._data_root, project_name)

        # Ensure detection mode
        if self._training_task != "detection":
            self._set_task_type("detection")

        # Reset class cards to a fresh single detection card
        self._reset_training_classes()

        # Set project identity
        self._current_project_name = project_name
        self._project_initialized = True

        # Lock project name UI
        self.editProjName.setText(project_name)
        self.editProjName.setDisabled(True)
        self.btnProjCheck.setDisabled(True)
        self.btnProjReload.setDisabled(True)
        self.editProjName.setStyleSheet(
            "QLineEdit { background: #f1f5f9; border: 1px solid #cbd5e1; color: #64748b; border-radius: 6px; padding: 2px 8px; }"
        )

        # Load class names from classes.txt or fall back to scanning annotations
        classes_file = os.path.join(project_path, "classes.txt")
        class_names = []
        if os.path.exists(classes_file):
            with open(classes_file, "r") as f:
                class_names = [line.strip() for line in f if line.strip()]
        if not class_names:
            max_id = -1
            for fname in os.listdir(project_path):
                if fname.endswith('.txt') and fname != 'classes.txt':
                    try:
                        with open(os.path.join(project_path, fname), 'r') as f:
                            for line in f:
                                parts = line.strip().split()
                                if parts:
                                    cid = int(parts[0])
                                    if cid > max_id:
                                        max_id = cid
                    except (ValueError, IOError):
                        pass
            if max_id >= 0:
                class_names = [f"Class{i}" for i in range(max_id + 1)]

        # Populate tag panel with class names
        info = self._class_data[0]
        if info and info.get("tag_panel") and class_names:
            info["tag_panel"].set_class_names(class_names)

        # Collect and sort image files naturally
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
        image_files = [
            os.path.join(project_path, f)
            for f in os.listdir(project_path)
            if f.lower().endswith(image_extensions)
        ]
        image_files.sort(key=lambda p: [
            int(c) if c.isdigit() else c.lower()
            for c in re.split(r'(\d+)', os.path.basename(p))
        ])

        # Infer capture size from first image
        if image_files:
            pix = QPixmap(image_files[0])
            if not pix.isNull() and pix.width() in (320, 640):
                detected_size = pix.width()
                self._capture_size = detected_size
                if hasattr(self, 'btnCapSize320') and self.btnCapSize320:
                    self.btnCapSize320.setChecked(detected_size == 320)
                if hasattr(self, 'btnCapSize640') and self.btnCapSize640:
                    self.btnCapSize640.setChecked(detected_size == 640)
                if hasattr(self, 'lblStaticImgSize') and self.lblStaticImgSize:
                    text = "320x320 (Fast)" if detected_size == 320 else "640x640 (High Detail)"
                    self.lblStaticImgSize.setText(text)
                self.log_to_console(f"Detected image size: {detected_size}x{detected_size}")

        # Load all images into the class card
        for img_path in image_files:
            self._add_image_to_class(0, img_path)

        # Refresh all UI states
        self._update_project_ui_lock()
        self._update_ui_for_task()
        self._update_dataset_summary()
        self._update_label_status(0)
        self.log_to_console(f"Project '{project_name}' reloaded with {len(image_files)} images.")

    def _update_project_ui_lock(self):
        """Disable and add helper tooltips to collection elements if project not initialized."""
        locked = not self._project_initialized
        tip = "⚠️ Please enter project name and click ✔ first." if locked else ""
        
        # 1. Add Class button
        if hasattr(self, 'btnAddClass') and self.btnAddClass:
            self.btnAddClass.setEnabled(not locked)
            self.btnAddClass.setToolTip(tip)
            
        # 2. Individual class cards
        for info in self._class_data:
            if not info or "card" not in info: continue
            
            # Set tooltip for the entire card and its children when locked
            info["card"].setToolTip(tip)
            
            for btn in info["card"].findChildren(QPushButton):
                btn.setEnabled(not locked)
                btn.setToolTip(tip)
            
            for edit in info["card"].findChildren(QLineEdit):
                # Don't disable name_edit in Recognition mode? 
                # Actually, in recognition mode each card has its name.
                # If project is not initialized, we lock the WHOLE CARD.
                edit.setEnabled(not locked)
                edit.setToolTip(tip)

        # 3. Image Size buttons (Locked when project active to prevent midway changes)
        lock_msg = "Cannot change size once project is started."
        if hasattr(self, 'btnCapSize320') and self.btnCapSize320:
            self.btnCapSize320.setEnabled(locked)
            if not locked: self.btnCapSize320.setToolTip(lock_msg)
        if hasattr(self, 'btnCapSize640') and self.btnCapSize640:
            self.btnCapSize640.setEnabled(locked)
            if not locked: self.btnCapSize640.setToolTip(lock_msg)


    def _set_task_type(self, task):
        """Switch between recognition and detection modes."""
        if hasattr(self, '_training_task') and self._training_task == task: return
        
        self._training_task = task
        
        # Reset project row UI
        self._project_initialized = False
        self._current_project_name = ""
        
        if hasattr(self, 'editProjName'):
            self.editProjName.setDisabled(False)
            self.editProjName.setText("")
            self._validate_project_name_visual("")
            
        if hasattr(self, 'btnProjCheck'):
            self.btnProjCheck.setDisabled(False)

        if hasattr(self, 'btnProjReload'):
            self.btnProjReload.setDisabled(False)

        self._update_project_ui_lock()
        self._update_ui_for_task()
        
        # Shutdown cameras and hide panels on mode switch
        self._stop_webcam()
        self._reset_training_classes() # Clean all class cards and images
        
        if task == "recognition":
             self._close_bbox_panel()



    def _set_capture_size(self, size):
        self._capture_size = size
        self.log_to_console(f"Training capture resolution set to: {size}x{size}")

    def _reset_training_classes(self):
        """Wipe all existing class cards and data state."""
        # 1. Clear UI widgets for all classes
        for info in self._class_data:
            if info and "card" in info:
                info["card"].setParent(None)
                info["card"].deleteLater()
        
        # 2. Reset internal collection state
        self._class_data = []
        
        # 3. Re-initialize with default classes based on mode
        is_detection = (hasattr(self, '_training_task') and self._training_task == "detection")
        
        self.add_training_class("Class 1")
        if not is_detection:
            self.add_training_class("Class 2")
        
        # 4. Refresh counters and Sweep UI
        self._update_dataset_summary()
        self._update_ui_for_task() # Final sweep to ensure correct visibility
        self._update_project_ui_lock() # Re-lock the new classes




    def _build_bbox_panel(self):
        """Create the collapsible BBox editor panel at the bottom of the left panel."""
        left_panel = self.training_mode_widget.findChild(QFrame, "leftPanel")
        if not left_panel: return
        
        # The panel itself (collapsible annotation area)
        self._bbox_panel = QFrame(left_panel)
        self._bbox_panel.setObjectName("bboxPanel")
        self._bbox_panel.setVisible(False)
        self._bbox_panel.setFixedHeight(350) # Stable default
        self._bbox_panel.setStyleSheet("""
            QFrame#bboxPanel { 
                background: #0f172a; 
                border-top: 3px solid #8b5cf6;
            }
        """)
        
        panel_layout = QVBoxLayout(self._bbox_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # Drag handle
        drag_handle = QFrame()
        drag_handle.setObjectName("bboxHandle")
        drag_handle.setFixedHeight(20)
        drag_handle.setCursor(Qt.CursorShape.SizeVerCursor)
        drag_handle.setStyleSheet("background: rgba(139,92,246,0.3); hover { background: rgba(139,92,246,0.6); }")
        handle_layout = QHBoxLayout(drag_handle)
        pip = QLabel()
        pip.setFixedSize(48, 4)
        pip.setStyleSheet("background: white; border-radius: 2px;")
        handle_layout.addStretch()
        handle_layout.addWidget(pip)
        handle_layout.addStretch()
        panel_layout.addWidget(drag_handle)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background: #1e293b; border-bottom: 1px solid #334155;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 4, 12, 4)
        
        title_layout = QVBoxLayout()
        lbl_title = QLabel()
        lbl_title.setObjectName("bboxTitle")
        lbl_title.setStyleSheet("color: white; font-weight: bold; font-size: 15px;")
        self._bbox_hint = QLabel("Click an image above to annotate it.")
        self._bbox_hint.setStyleSheet("color: #94a3b8; font-size: 13px;")
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(self._bbox_hint)
        
        btn_close_bbox = QPushButton("✕")
        btn_close_bbox.setFixedSize(28, 28)
        btn_close_bbox.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close_bbox.setStyleSheet("QPushButton { background: transparent; color: #94a3b8; border: none; font-size: 16px; } QPushButton:hover { color: white; }")
        btn_close_bbox.clicked.connect(self._close_bbox_panel)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(btn_close_bbox)
        panel_layout.addWidget(header)
        
        # Canvas area
        self._bbox_canvas = AnnotationLabel()
        self._bbox_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bbox_canvas.setStyleSheet("background: #000; color: #64748b;")
        self._bbox_canvas.setText("Select an image to annotate")
        self._bbox_canvas.save_requested.connect(self._save_bbox_annotation)
        self._bbox_canvas.close_requested.connect(self._close_bbox_panel)
        panel_layout.addWidget(self._bbox_canvas, 1)
        
        # Floating Shutter Button for the right-panel webcam (visible when cam active)
        self._tr_shutter_btn = QPushButton("📸 Capture Frame")
        self._tr_shutter_btn.setParent(self) # Floating
        self._tr_shutter_btn.setFixedSize(160, 48)
        self._tr_shutter_btn.setVisible(False)
        self._tr_shutter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tr_shutter_btn.setStyleSheet("""
            QPushButton { 
                background: #3b82f6; color: white; border: 2px solid white;
                border-radius: 24px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background: #2563eb; }
        """)
        self._tr_shutter_btn.clicked.connect(self._capture_image)
        
        # Bottom action area — enhanced with navigation and info
        bottom_bar = QFrame()
        bottom_bar.setStyleSheet("background: #0f172a; border-top: 1px solid #1e293b;")
        bottom_bar_layout = QVBoxLayout(bottom_bar)
        bottom_bar_layout.setContentsMargins(16, 4, 16, 6)
        bottom_bar_layout.setSpacing(4)
        
        # Row 1: Status and Navigation Info
        info_row = QHBoxLayout()
        self._lbl_batch_progress = QLabel("Image 0 of 0")
        self._lbl_batch_progress.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold;")
        
        shortcut_hint = QLabel("[Enter] Save  [Del] Clear  [Esc] Close")
        shortcut_hint.setStyleSheet("color: #475569; font-size: 10px;")
        
        info_row.addWidget(self._lbl_batch_progress)
        info_row.addStretch()
        info_row.addWidget(shortcut_hint)
        bottom_bar_layout.addLayout(info_row)

        # Row 2: Navigation and Action Buttons
        action_row = QHBoxLayout()
        
        btn_prev = QPushButton("◀")
        btn_prev.setFixedSize(36, 36)
        btn_prev.setToolTip("Previous Image")
        btn_prev.setStyleSheet("""
            QPushButton { background: #1e293b; color: white; border: 1px solid #334155; border-radius: 18px; font-weight: bold; }
            QPushButton:hover { background: #334155; }
            QPushButton:disabled { color: #334155; }
        """)
        btn_prev.clicked.connect(lambda: self._navigate_annotation(-1))
        self._btn_prev_annotation = btn_prev

        btn_next = QPushButton("▶")
        btn_next.setFixedSize(36, 36)
        btn_next.setToolTip("Next Image / Skip")
        btn_next.setStyleSheet("""
            QPushButton { background: #1e293b; color: white; border: 1px solid #334155; border-radius: 18px; font-weight: bold; }
            QPushButton:hover { background: #334155; }
            QPushButton:disabled { color: #334155; }
        """)
        btn_next.clicked.connect(lambda: self._navigate_annotation(1))
        self._btn_next_annotation = btn_next

        # BBox Save button
        self._bbox_save_btn = QPushButton("Save & Continue ▶")
        self._bbox_save_btn.setStyleSheet("""
            QPushButton { background: #7c3aed; color: white; border: none; border-radius: 6px;
                         font-weight: bold; font-size: 15px; padding: 10px 24px; min-width: 140px; }
            QPushButton:hover { background: #6d28d9; }
        """)
        self._bbox_save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._bbox_save_btn.clicked.connect(self._save_bbox_annotation)
        
        # Camera shutter button
        self._cam_shutter_btn = QPushButton("⬤  Capture")
        self._cam_shutter_btn.setStyleSheet("""
            QPushButton { 
                background: white; color: #1e293b; border: 4px solid #94a3b8;
                border-radius: 20px; font-weight: bold; font-size: 14px; 
                padding: 10px 32px; min-width: 120px;
            }
            QPushButton:hover { background: #f0f9ff; border-color: #3b82f6; color: #1d4ed8; }
        """)
        self._cam_shutter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cam_shutter_btn.setVisible(False)
        self._cam_shutter_btn.clicked.connect(self._capture_image)
        
        action_row.addWidget(btn_prev)
        action_row.addSpacing(4)
        action_row.addWidget(btn_next)
        action_row.addStretch()
        action_row.addWidget(self._bbox_save_btn)
        action_row.addWidget(self._cam_shutter_btn)
        bottom_bar_layout.addLayout(action_row)
        
        # Class Selection Bar (Detection Mode)
        self._bbox_class_selector = QFrame()
        self._bbox_class_selector.setStyleSheet("background: #0f172a; border-top: 1px solid #1e293b;")
        self._class_selector_layout = QHBoxLayout(self._bbox_class_selector)
        self._class_selector_layout.setContentsMargins(12, 4, 12, 4)
        self._class_selector_layout.setSpacing(6)
        self._class_btn_group = [] # List of buttons
        self._active_label_class_idx = 0
        panel_layout.addWidget(self._bbox_class_selector)
        
        panel_layout.addWidget(bottom_bar)
        
        # Store handle and add to left panel layout
        self._bbox_drag_handle = drag_handle
        self._bbox_drag_start_y = 0
        self._bbox_drag_start_h = 350
        drag_handle.mousePressEvent = self._bbox_handle_press
        drag_handle.mouseMoveEvent = self._bbox_handle_move
        
        left_panel.layout().addWidget(self._bbox_panel)

    def _close_bbox_panel(self):
        if hasattr(self, '_bbox_panel'):
            self._bbox_panel.setVisible(False)
            self._bbox_panel_visible = False

    def _bbox_handle_press(self, event):
        self._bbox_drag_start_y = event.globalPos().y()
        self._bbox_drag_start_h = self._bbox_panel.height()

    def _bbox_handle_move(self, event):
        delta = int(self._bbox_drag_start_y - event.globalPos().y())
        # Tight cap (500px) to ensure we don't push the window beyond display limits (991px high)
        new_h = max(120, min(500, self._bbox_drag_start_h + delta))
        self._bbox_panel.setFixedHeight(new_h)

    def add_training_class(self, default_name=None):
        """Add a new class card with editable name, image grid, and webcam/upload actions."""
        layout = self.training_mode_widget.findChild(QVBoxLayout, "classListLayout")
        if not layout: return
        
        class_idx = len(self._class_data) + 1
        label = default_name or f"Class {class_idx}"
        
        # ── Card Frame
        card = QFrame()
        card.setObjectName("classCard")
        is_detection = (hasattr(self, '_training_task') and self._training_task == "detection")
        if is_detection:
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card.setStyleSheet("""
            QFrame#classCard { 
                background: white; 
                border: 1px solid #e2e8f0; 
                border-radius: 10px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # ── Header (light gray bar)
        header_frame = QFrame()
        header_frame.setStyleSheet("background: #f8fafc; border-bottom: 1px solid #f1f5f9; border-radius: 0;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 6, 12, 6)
        header_layout.setSpacing(6)
        
        # Editable class name
        name_edit = QLineEdit(label)
        name_edit.setObjectName("classNameEdit")
        if hasattr(self, '_training_task') and self._training_task == "detection":
            name_edit.setVisible(False)
            
        name_edit.setStyleSheet("""

            QLineEdit { 
                font-weight: bold; font-size: 20px; color: #1e293b;
                border: 1px solid transparent; border-radius: 4px;
                background: transparent; padding: 2px 6px;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6; background: white;
            }
            QLineEdit:hover { border: 1px solid #cbd5e1; }
        """)
        
        count_badge = QLabel("0 imgs")
        count_badge.setFixedWidth(68)
        count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_badge.setStyleSheet("""
            background: #e2e8f0; color: #64748b; 
            border-radius: 10px; padding: 2px 2px; 
            font-size: 14px; font-weight: bold;
        """)
        
        status_check = QLabel("")
        status_check.setFixedWidth(20)
        status_check.setStyleSheet("color: #10b981; font-weight: bold; font-size: 16px;")
        
        btn_del = QPushButton("🗑")
        btn_del.setFixedSize(26, 26)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #94a3b8; font-size: 16px; }
            QPushButton:hover { color: #ef4444; }
        """)
        
        header_layout.addWidget(name_edit)
        header_layout.addStretch(1) # Always pushes following elements to the right
        header_layout.addWidget(status_check)
        header_layout.addWidget(count_badge)
        header_layout.addWidget(btn_del)
        card_layout.addWidget(header_frame)

        
        # ── Body
        body = QFrame()
        body.setStyleSheet("background: white;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(8)
        
        # Image thumbnail area (Scroll Area)
        scroll = QScrollArea()
        scroll.setObjectName("imgScroll")
        is_detection = (hasattr(self, '_training_task') and self._training_task == "detection")
        
        if is_detection:
            scroll.setMinimumHeight(300)
            scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            scroll.setFixedHeight(80)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        
        # In Detection mode, use a multi-row Grid Layout. In Recognition, keep Horizontal.
        if is_detection:
            img_grid = QGridLayout(scroll_widget)
            img_grid.setContentsMargins(6, 6, 6, 6)
            img_grid.setSpacing(8)
            img_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        else:
            img_grid = QHBoxLayout(scroll_widget)
            img_grid.setContentsMargins(0, 0, 0, 0)
            img_grid.setSpacing(6)
            img_grid.addStretch()
            
        scroll.setWidget(scroll_widget)
        # Placeholder hint label (shown when no images)
        hint_lbl = QLabel("No images collected yet.")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_lbl.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: 50;")
        if is_detection:
            # Allow hint to stretch and fill the expansive 300px+ height
            hint_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            hint_lbl.setMinimumHeight(240)
        
        body_layout.addWidget(hint_lbl)
        body_layout.addWidget(scroll)
        scroll.setVisible(False)
        
        # ── Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        btn_cam = QPushButton("🎥  Webcam")
        btn_cam.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cam.setStyleSheet("""
            QPushButton { 
                background: white; border: 1px solid #e2e8f0; color: #475569;
                border-radius: 6px; padding: 6px; font-weight: 600; font-size: 15px;
            }
            QPushButton:hover { background: #f8fafc; border-color: #3b82f6; color: #3b82f6; }
            QPushButton[active="true"] { background: #eff6ff; border-color: #3b82f6; color: #2563eb; }
        """)
        
        btn_upload = QPushButton("📁  Upload")
        btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload.setStyleSheet("""
            QPushButton { 
                background: white; border: 1px solid #e2e8f0; color: #475569;
                border-radius: 6px; padding: 6px; font-weight: 600; font-size: 15px;
            }
            QPushButton:hover { background: #f8fafc; border-color: #10b981; color: #059669; }
        """)
        
        btn_row.addWidget(btn_cam)
        btn_row.addWidget(btn_upload)
        
        btn_label = QPushButton("⬚  Label")
        btn_label.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_label.setVisible(self._training_task == "detection")
        btn_label.setStyleSheet("""
            QPushButton { 
                background: white; border: 1px solid #f87171; color: #ef4444;
                border-radius: 6px; padding: 6px; font-weight: 600; font-size: 15px;
            }
            QPushButton:hover { background: #fef2f2; border-color: #ef4444; }
        """)
        btn_row.addWidget(btn_label)
        
        # ── Tag Panel (Detection Mode Only)
        tag_panel = None
        if hasattr(self, '_training_task') and self._training_task == "detection":
            tag_panel = MultiClassTagPanel()
            body_layout.addWidget(tag_panel)
            # Validation logic: disable Label button until classes are defined
            tag_panel.validation_changed.connect(btn_label.setEnabled)
            btn_label.setEnabled(False) # Initial state
            btn_label.setToolTip("Please define at least 2 classes to start labeling.")
        
        body_layout.addLayout(btn_row)
        
        card_layout.addWidget(body)
        
        # ── Store class data
        class_info = {
            "name_edit": name_edit,
            "count_badge": count_badge,
            "hint_lbl": hint_lbl,
            "img_grid": img_grid,
            "scroll": scroll,
            "images": [],
            "card": card,
            "btn_cam": btn_cam,
            "btn_label": btn_label,
            "status_check": status_check,
            "btn_del": btn_del, # Store to hide in detection mode
            "tag_panel": tag_panel, # 4-class multi-tag panel
        }
        self._class_data.append(class_info)

        ci = len(self._class_data) - 1
        
        # ── Connect signals
        btn_del.clicked.connect(lambda _, idx=ci: self._delete_class(idx))
        btn_upload.clicked.connect(lambda _, idx=ci: self._upload_images(idx))
        btn_cam.clicked.connect(lambda _, idx=ci: self._toggle_webcam(idx))
        btn_label.clicked.connect(lambda _, idx=ci: self._annotate_next_in_class(idx))
        
        # Folder rename when class name is edited
        old_name_ref = [label]
        def on_name_changed(new_name, idx=ci, old_ref=old_name_ref):
            self._rename_class_folder(old_ref[0], new_name)
            old_ref[0] = new_name
        name_edit.editingFinished.connect(lambda: on_name_changed(name_edit.text()))
        
        # Create the data folder on disk immediately
        self._ensure_class_folder(label)
        
        # Insert before the spacer (last item)
        # Give higher stretch in Detection mode to expand and push the spacer
        stretch = 10 if is_detection else 0
        layout.insertWidget(layout.count() - 1, card, stretch)
        card.show()
        
        self._update_label_status(ci)

    def _delete_class(self, idx):
        """Remove a class card."""
        if len(self._class_data) <= 1:
            return  # Keep at least one
        info = self._class_data[idx]
        info["card"].setParent(None)
        info["card"].deleteLater()
        self._class_data[idx] = None  # Mark as deleted (preserve indices)
        self._update_dataset_summary()

    def _upload_images(self, idx):
        """Upload image files for a class."""
        info = self._class_data[idx]
        if info is None: return
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        for path in files:
            self._add_image_to_class(idx, path)

    def _add_image_to_class(self, idx, image_path):
        """Add a thumbnail tile to the image grid for a class."""
        info = self._class_data[idx]
        if info is None: return
        
        info["images"].append(image_path)
        count = len(info["images"])
        info["count_badge"].setText(f"{count} imgs")
        info["hint_lbl"].setVisible(False)
        info["scroll"].setVisible(True)
        
        # Create thumbnail tile
        tile = QFrame()
        tile.setFixedSize(80, 80)
        tile.setStyleSheet("QFrame { border-radius: 6px; border: 2px solid #e2e8f0; }")
        tile_layout = QVBoxLayout(tile)
        tile_layout.setContentsMargins(0, 0, 0, 0)
        
        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_lbl.setStyleSheet("border-radius: 4px;")
        
        pix = QPixmap(image_path)
        if not pix.isNull():
            img_lbl.setPixmap(pix.scaled(76, 76, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        
        # If detection mode, make tile clickable to annotate via double click
        if self._training_task == "detection":
            tile.setStyleSheet("QFrame { border-radius: 6px; border: 2px solid #f87171; }")
            tile.setCursor(Qt.CursorShape.PointingHandCursor)
            tile.mouseDoubleClickEvent = lambda e, p=image_path, ci=idx: self._open_bbox_editor(p, ci)
        
        tile_layout.addWidget(img_lbl)
        
        # Insert into grid (wrap if Detection) or layout
        grid = info["img_grid"]
        if isinstance(grid, QGridLayout):
            cols = 4
            grid_pos = len(info["images"]) - 1
            row, col = divmod(grid_pos, cols)
            grid.addWidget(tile, row, col)
        else:
            grid.insertWidget(grid.count() - 1, tile)
        
        self._update_dataset_summary()
        self._update_label_status(idx)

    def _save_bbox_annotation(self):
        """Persist the bounding box to a YOLO format text file."""
        if not hasattr(self, '_current_annotating_img'): return
        
        boxes = self._bbox_canvas.get_all_normalized_boxes()
        if not boxes:
            self._bbox_hint.setText("⚠️ Please draw at least one box first!")
            return
            
        # Save all boxes to .txt (one line per box)
        txt_path = os.path.splitext(self._current_annotating_img)[0] + ".txt"
        try:
            with open(txt_path, "w") as f:
                for b in boxes:
                    cx, cy, w, h, cid = b
                    f.write(f"{cid} {cx} {cy} {w} {h}\n")
            
            self._bbox_hint.setText(f"✅ {len(boxes)} Boxes Saved!")
            self._save_classes_txt()
            # Brief flash
            self._bbox_canvas.setStyleSheet("background: #052e16;")
            QTimer.singleShot(200, lambda: self._bbox_canvas.setStyleSheet("background: #000;"))
            
            # If we were in a batch, open next. If not, just stay.
            if hasattr(self, '_is_batch_annotating') and self._is_batch_annotating:
                QTimer.singleShot(400, lambda: self._navigate_annotation(1))
            
            self._update_label_status(self._current_annotating_class)
            
        except Exception as e:
            print(f"[ERROR] Could not save annotation: {e}")
            self._bbox_hint.setText("❌ Error saving box")

    def _navigate_annotation(self, step):
        """Go to the next or previous image in the current class."""
        if self._current_annotating_class is None: return
        info = self._class_data[self._current_annotating_class]
        if not info or not info["images"]: return
        
        try:
            curr_idx = info["images"].index(self._current_annotating_img)
            new_idx = curr_idx + step
            
            if 0 <= new_idx < len(info["images"]):
                self._open_bbox_editor(info["images"][new_idx], self._current_annotating_class)
            elif new_idx >= len(info["images"]):
                self.log_to_console(f"Batch complete for {info['name_edit'].text()}")
                self._bbox_hint.setText("✅ All images in this class annotated!")
                QTimer.singleShot(1500, self._close_bbox_panel)
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}")

    def _open_bbox_editor(self, image_path, class_idx):
        """Load image into bbox canvas and show the panel."""
        if not hasattr(self, '_bbox_panel'): return
        self._current_annotating_img = image_path
        self._current_annotating_class = class_idx
        
        # Clear specific batch state
        self._is_batch_annotating = True
        
        pix = QPixmap(image_path)
        if not pix.isNull():
            self._bbox_canvas.set_image(pix)
            
            # Reset and Load existing boxes if any
            self._bbox_canvas.clear_all()
            txt_path = os.path.splitext(image_path)[0] + ".txt"
            if os.path.exists(txt_path):
                try:
                    with open(txt_path, "r") as f:
                        lines = f.readlines()
                        for line in lines:
                            parts = line.strip().split()
                            if len(parts) == 5:
                                cid = int(parts[0])
                                cx, cy, w, h = map(float, parts[1:])
                                # Get name from tag_panel if available
                                name = ""
                                if self._training_task == "detection":
                                    tnames = self._class_data[self._current_annotating_class]["tag_panel"].get_class_names()
                                    if cid < len(tnames): name = tnames[cid]
                                self._bbox_canvas.add_box(cx, cy, w, h, cid, name)
                except: pass
        
        info = self._class_data[class_idx]
        class_name = info["name_edit"].text() if info else "Unknown"
        self._bbox_hint.setText(f"Annotating: {os.path.basename(image_path)}")
        
        # 🧪 Multi-class assignment in Detection mode
        if self._training_task == "detection" and "tag_panel" in info and info["tag_panel"]:
            self._bbox_class_selector.setVisible(True)
            # Rebuild class selector buttons based on current tag panel names
            # (First Clear existing)
            for i in reversed(range(self._class_selector_layout.count())):
                w = self._class_selector_layout.itemAt(i).widget()
                if w: w.setParent(None); w.deleteLater()
            self._class_btn_group = []
            
            names = info["tag_panel"].get_class_names()
            colors = ["#a855f7", "#fb7185", "#3b82f6", "#10b981"] # Match MultiClassTagPanel
            
            for i, name in enumerate(names):
                btn = QPushButton(name)
                btn.setCheckable(True)
                btn.setFixedHeight(24)
                color = colors[i % len(colors)]
                btn.setStyleSheet(f"""
                    QPushButton {{ 
                        background: transparent; color: {color}; border: 1px solid {color}; 
                        border-radius: 4px; font-weight: bold; font-size: 10px; padding: 2px 8px;
                    }}
                    QPushButton:checked {{ background: {color}; color: white; }}
                """)
                btn.clicked.connect(lambda _, idx=i: self._set_active_label_class(idx))
                self._class_selector_layout.addWidget(btn)
                self._class_btn_group.append(btn)
            
            self._class_selector_layout.addStretch()
            if self._class_btn_group:
                self._set_active_label_class(0)
        else:
            self._bbox_class_selector.setVisible(False)
        
        # Update progress label
        img_list = info["images"]
        curr_num = img_list.index(image_path) + 1
        self._lbl_batch_progress.setText(f"IMAGE {curr_num} OF {len(img_list)}")
        
        # Update navigation button states
        self._btn_prev_annotation.setEnabled(curr_num > 1)
        self._btn_next_annotation.setEnabled(curr_num < len(img_list))
        
        # UI visibility
        if hasattr(self, '_bbox_save_btn') and hasattr(self, '_cam_shutter_btn'):
            self._bbox_save_btn.setVisible(True)
            self._cam_shutter_btn.setVisible(False)
            
        self._bbox_panel.setVisible(True)
        self._bbox_panel_visible = True
        self._bbox_canvas.setFocus()
        self._bbox_canvas.update()

    def _annotate_next_in_class(self, idx):
        """Find the next unannotated image in a class and open it."""
        info = self._class_data[idx]
        if info is None: return
        
        self._is_batch_annotating = True
        
        # Look for first image without a .txt file
        target_img = None
        for img_path in info["images"]:
            txt_path = os.path.splitext(img_path)[0] + ".txt"
            if not os.path.exists(txt_path):
                target_img = img_path
                break
        
        if target_img:
            self._open_bbox_editor(target_img, idx)
        else:
            self._is_batch_annotating = False
            self.log_to_console(f"Done annotating category: {info['name_edit'].text()}")
            self._bbox_hint.setText("✅ All images in this class annotated!")
            QTimer.singleShot(2000, self._close_bbox_panel)
            
        self._update_label_status(idx)

    def _set_active_label_class(self, idx):
        """Switch the current class index for newly drawn boxes."""
        self._active_label_class_idx = idx
        for i, btn in enumerate(self._class_btn_group):
            btn.setChecked(i == idx)
        
        # Update canvas context
        self._bbox_canvas.active_class_id = idx
        if "tag_panel" in self._class_data[self._current_annotating_class]:
            names = self._class_data[self._current_annotating_class]["tag_panel"].get_class_names()
            if idx < len(names):
                self._bbox_canvas.active_class_name = names[idx]
        self._bbox_canvas.update()

    def _update_label_status(self, idx):
        """Update the appearance of the 'Label Series' button based on progress."""
        info = self._class_data[idx]
        if not info: return
        
        # Check if all images have annotations
        all_labeled = True
        images = info["images"]
        if not images:
            all_labeled = False
        else:
            for img in images:
                if not os.path.exists(os.path.splitext(img)[0] + ".txt"):
                    all_labeled = False
                    break
        
        # Update button look
        if all_labeled:
            info["btn_label"].setStyleSheet("""
                QPushButton { 
                    background: #10b981; border: 1px solid #059669; color: white;
                    border-radius: 6px; padding: 10px; font-weight: 800; font-size: 15px;
                }
                QPushButton:hover { background: #059669; }
            """)
            info["status_check"].setText("✔")
        else:
            # Revert to standard red variant
            info["btn_label"].setStyleSheet("""
                QPushButton { 
                    background: white; border: 1px solid #f87171; color: #ef4444;
                    border-radius: 6px; padding: 10px; font-weight: 600; font-size: 17px;
                }
                QPushButton:hover { background: #fef2f2; border-color: #ef4444; }
            """)
            info["status_check"].setText("")

    def _ensure_class_folder(self, class_name):
        """Create class folder if it doesn't exist, nested within project name if active.
           In Detection mode, we skip class-specific subfolders and save everything to projects/data/[project_name]/."""
        # Sanitize class name
        class_name = "".join([c for c in class_name if c.isalnum() or c in (' ', '_', '-')]).strip()
        if not class_name: class_name = "UnnamedClass"
        
        # Data paths
        if hasattr(self, '_project_initialized') and self._project_initialized and self._current_project_name:
            if self._training_task == "detection":
                folder = os.path.join(self._data_root, self._current_project_name)
            else:
                folder = os.path.join(self._data_root, self._current_project_name, class_name)
        else:
            # Fallback for non-project data collection (Legacy)
            folder = os.path.join(self._data_root, class_name)
            
        os.makedirs(folder, exist_ok=True)
        return folder

    def _save_classes_txt(self):
        """Persist current detection class names to classes.txt in the project folder."""
        if not self._project_initialized or self._training_task != "detection":
            return
        if not self._class_data or not self._class_data[0]:
            return
        tag_panel = self._class_data[0].get("tag_panel")
        if not tag_panel:
            return
        names = tag_panel.get_class_names()
        if names:
            path = os.path.join(self._data_root, self._current_project_name, "classes.txt")
            with open(path, "w") as f:
                for n in names:
                    f.write(n + "\n")

    def _rename_class_folder(self, old_name, new_name):
        """Rename the class folder when class name changes."""
        if not new_name.strip() or old_name == new_name: return
        
        # Determine base directory holding class folders
        if hasattr(self, '_project_initialized') and self._project_initialized and self._current_project_name:
            if self._training_task == "detection":
               # Detection mode has no class folders, everything is root
               return
            else:
                parent_dir = os.path.join(self._data_root, self._current_project_name)
        else:
            parent_dir = self._data_root
            
        old_folder = os.path.join(parent_dir, old_name)
        new_folder = os.path.join(parent_dir, new_name)
        
        if os.path.exists(old_folder) and not os.path.exists(new_folder):
            try:
                os.rename(old_folder, new_folder)
                # Update stored paths in class_info.images list
                for cinfo in self._class_data:
                    if cinfo is None: continue
                    if cinfo["name_edit"].text() == new_name:
                        old_s = old_folder.replace("\\", "/")
                        new_s = new_folder.replace("\\", "/")
                        cinfo["images"] = [
                            p.replace(old_s, new_s).replace(old_folder, new_folder) for p in cinfo["images"]
                        ]
            except Exception as e:
                print(f"[WARN] Could not rename folder: {e}")
        else:
            self._ensure_class_folder(new_name)

    def _toggle_webcam(self, idx):
        """Show or hide the webcam capture panel for this class."""
        info = self._class_data[idx]
        if info is None: return

        # If already open for this class → close it
        if self._active_camera_class == idx:
            self._stop_webcam()
            return

        # If open for another class → close first
        if self._active_camera_class is not None:
            self._stop_webcam()

        # Open webcam
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Cannot open camera.")
            return

        self._cam_cap = cap
        self._active_camera_class = idx
        info["btn_cam"].setText("⏹  Stop Cam")
        info["btn_cam"].setProperty("active", "true")
        info["btn_cam"].style().unpolish(info["btn_cam"])
        info["btn_cam"].style().polish(info["btn_cam"])

        # Show webcam feed — no annotation drawing during capture
        self._show_webcam_panel(idx)
        self._cam_timer.start()

    def _show_webcam_panel(self, idx):
        """Configure the UI to show webcam stream in the right panel + capture button."""
        # Update header
        info = self._class_data[idx]
        class_name = info["name_edit"].text() if info else "?"
        self.log_to_console(f"Webcam active for: {class_name}")

        # Show the camera in the right panel
        if hasattr(self, 'trCamDisplay'):
            self.trCamDisplay.setVisible(True)
            if hasattr(self, 'statusPlaceholder'):
                self.statusPlaceholder.setVisible(False)
            if hasattr(self, '_tr_shutter_btn'):
                self._tr_shutter_btn.setVisible(True)
                self._tr_shutter_btn.raise_()
        
        self._bbox_panel.setVisible(False) # Hide annotation panel during live capture

    def _update_cam_frame(self):
        """Timer callback: grab frame from cv2, display in trCamDisplay."""
        if self._cam_cap is None: return
        import cv2
        ret, frame = self._cam_cap.read()
        if not ret: return
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        qimg = QImage(frame_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        
        # Display live frame — just set pixmap, no annotation overlay
        self.trCamDisplay.setPixmap(pix.scaled(
            self.trCamDisplay.width(), self.trCamDisplay.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self._last_cam_frame = frame  # Store raw BGR for saving
        
        # Position floating shutter over the camera
        if self._tr_shutter_btn.isVisible():
            # Get global position of camera preview and center the button at the bottom
            try:
                cam_rect = self.trCamDisplay.geometry()
                global_pos = self.trCamDisplay.mapToGlobal(QPoint(0,0))
                # Target the bottom center of the camera view
                btn_x = global_pos.x() + (cam_rect.width() - self._tr_shutter_btn.width()) // 2
                btn_y = global_pos.y() + cam_rect.height() - 70
                self._tr_shutter_btn.move(self.mapFromGlobal(QPoint(btn_x, btn_y)))
                self._tr_shutter_btn.raise_()
            except: pass

    def _capture_image(self):
        """Capture the current camera frame, square crop, resize and save to disk."""
        if not hasattr(self, '_last_cam_frame') or self._last_cam_frame is None: return
        if self._active_camera_class is None: return
        import cv2
        idx = self._active_camera_class
        info = self._class_data[idx]
        if info is None: return

        # 1. Processing: Center Square Crop and Resize
        frame = self._last_cam_frame
        h, w = frame.shape[:2]
        min_dim = min(h, w)
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        crop = frame[start_y:start_y+min_dim, start_x:start_x+min_dim]
        
        # Resize to user target (320 or 640)
        final_img = cv2.resize(crop, (self._capture_size, self._capture_size), interpolation=cv2.INTER_AREA)

        # 2. Saving logic
        class_name = info["name_edit"].text()
        folder = self._ensure_class_folder(class_name)
        
        # Sequential numbering
        count = len(info["images"]) + 1
        img_filename = f"Image{count}.jpg"
        img_save_path = os.path.join(folder, img_filename)
        cv2.imwrite(img_save_path, final_img)
        
        # Save image only — no annotation during camera capture
        self.log_to_console(f"📸 Captured Image for: {class_name}")

        self._add_image_to_class(idx, img_save_path)
        self._update_label_status(idx)
        
        # Flash effect
        self.trCamDisplay.setStyleSheet("background: #fff;") # White flash
        QTimer.singleShot(80, lambda: self.trCamDisplay.setStyleSheet("background: black; border-radius: 12px;"))

    def _stop_webcam(self):
        """Stop the camera and restore the validation placeholder."""
        self._cam_timer.stop()
        if self._cam_cap:
            self._cam_cap.release()
            self._cam_cap = None
        self._last_cam_frame = None
        
        if hasattr(self, 'trCamDisplay'):
            self.trCamDisplay.setVisible(False)
            if hasattr(self, 'statusPlaceholder'):
                self.statusPlaceholder.setVisible(True)
            if hasattr(self, '_tr_shutter_btn'):
                self._tr_shutter_btn.setVisible(False)
        
        # Reset the button for the previous class
        if self._active_camera_class is not None:
            prev = self._class_data[self._active_camera_class]
            if prev:
                prev["btn_cam"].setText("🎥  Webcam")
                prev["btn_cam"].setProperty("active", "false")
                prev["btn_cam"].style().unpolish(prev["btn_cam"])
                prev["btn_cam"].style().polish(prev["btn_cam"])
        
        self._active_camera_class = None
        self._close_bbox_panel()
        
    def _update_ui_for_task(self):
        """Update training mode UI visibility based on current task type."""
        is_detection = (self._training_task == "detection")
        
        # 1. Hide Add Class button in Detection Mode
        if hasattr(self, 'btnAddClass') and self.btnAddClass:
            self.btnAddClass.setVisible(not is_detection)

        for i, info in enumerate(self._class_data):
            if not info: continue
            
            # 2. Hide extra classes in Detection Mode
            if i > 0:
                info["card"].setVisible(not is_detection)
            else:
                # 3. For the primary class, hide the "Class 1" label and delete button in Detection
                # This makes the detection workflow extremely minimal (just a capture slot)
                if "name_edit" in info:
                    info["name_edit"].setVisible(not is_detection)
                if "btn_del" in info:
                    info["btn_del"].setVisible(not is_detection)
                
                # In detection mode, we want the counter and check to be pinned to the right
                # The stretch (index 1) handles this already, but we ensure it works well

            
            if "btn_label" in info:
                info["btn_label"].setVisible(is_detection)
                self._update_label_status(i)

    def _update_dataset_summary(self):
        """Refresh the total image count shown in the Training Config panel."""
        total = sum(len(c["images"]) for c in self._class_data if c)
        classes = sum(1 for c in self._class_data if c)
        
        # New large count label support
        if hasattr(self, 'lblImageCountLarge'):
            self.lblImageCountLarge.setText(str(total))
        
        try:
            s = STRINGS[self.current_lang]
            lbl = self.training_mode_widget.findChild(QLabel, "lblImageCount")
            # Fallback for old label name if it still exists in some variant
            if lbl: lbl.setText(f"{total} images across {classes} classes")
        except Exception:
            pass

    def _start_training(self):
        """Launch the real background training process for YOLOv8."""
        if self._train_process is not None:
            # Stop training
            self._train_process.kill()
            self._train_process = None
            self._training_is_running = False
            self.btnStartTraining.setText("🚀 Resume Training")
            self.btnStartTraining.setEnabled(True)
            self.txtTrainLog.appendPlainText("> Training Stopped by User.")
            return

        # 0. Kill any running validation camera to free GPU memory
        self._stop_fast_validation()
        self._stop_webcam()

        # 1. Validation Logic
        if not self._project_initialized:
            self.log_to_console("Error: Project not initialized.", is_error=True)
            return
        
        # Check for backbone model yolov8n.pt (Stored in backend for protection)
        project_root = os.path.dirname(os.path.abspath(__file__))
        backbone_path = Path(project_root) / "src" / "modules" / "training" / "yolov8n.pt"
        
        if not backbone_path.exists():
            self.log_to_console(f"Error: Backbone model not found at {backbone_path}", is_error=True)
            self.log_to_console("Please place 'yolov8n.pt' in the src/modules/training/ folder.")
            return

        # 2. Get config from UI
        spin_epochs = self.training_mode_widget.findChild(QSpinBox, "spinEpochs")
        epochs = spin_epochs.value() if spin_epochs else 20
        self._training_total_epochs = epochs
        
        # Image size
        imgsz = self._capture_size
        
        # Class names (from Tag Panel)
        info = self._class_data[0] # Detection mode uses first class card
        if not info or "tag_panel" not in info:
            self.log_to_console("Error: Class tags not found.", is_error=True)
            return
        names = ",".join(info["tag_panel"].get_class_names())

        # 3. UI Feedback - Prepare Dashboard
        self.btnStartTraining.setText("⏸️ Stop Training")
        if hasattr(self, 'statusPlaceholder') and self.statusPlaceholder: 
            self.statusPlaceholder.setVisible(False)
        if self.metricsPanel: self.metricsPanel.setVisible(True)
        if self.epochBarFrame: self.epochBarFrame.setVisible(True)
        
        if self.progEpoch: self.progEpoch.setValue(0)
        if self.lblEpochCounter: self.lblEpochCounter.setText(f"0 / {epochs}")
        
        # Reset chart
        if self.canvasAcc:
            self.canvasAcc.x_data = []
            self.canvasAcc.y_train = []
            self.canvasAcc.y_val = []
        
        self.txtTrainLog.clear()
        self.txtTrainLog.appendPlainText(f"> [START] Initializing AI Training Pipeline...")
        self.txtTrainLog.appendPlainText(f"> Project: {self._current_project_name}")
        self.txtTrainLog.appendPlainText(f"> Parameters: Epochs={epochs}, ImgSz={imgsz}")

        # Persist class names before training
        self._save_classes_txt()

        # 4. Launch QProcess
        self._train_process = QProcess(self)
        
        # Setup Environment
        project_root = os.path.dirname(os.path.abspath(__file__))
        env = QProcessEnvironment.systemEnvironment()
        python_path = env.value("PYTHONPATH", "")
        env.insert("PYTHONPATH", f"{project_root}{os.pathsep}{python_path}" if python_path else project_root)
        self._train_process.setProcessEnvironment(env)
        self._train_process.setWorkingDirectory(project_root)

        # Build Arguments
        script_path = os.path.join(project_root, "src", "modules", "training", "trainer.py")
        data_path = os.path.join(self._data_root, self._current_project_name)
        
        args = [
            script_path,
            "--model", str(backbone_path.resolve()),
            "--project_path", str(Path(data_path).resolve()),
            "--epochs", str(epochs),
            "--imgsz", str(imgsz),
            "--names", names
        ]
        
        self._train_process.setProgram(sys.executable)
        self._train_process.setArguments(args)

        # Connect Signals
        self._train_process.readyReadStandardOutput.connect(self._on_train_stdout)
        self._train_process.readyReadStandardError.connect(self._on_train_stderr)
        self._train_process.finished.connect(self._on_train_finished)

        self._training_is_running = True
        self._train_dot_count = 0
        self._train_dot_timer.start()
        self._train_process.start()

    def _on_train_stdout(self):
        """Parse trainer.py output and update UI metrics."""
        if not self._train_process: return
        raw = bytes(self._train_process.readAllStandardOutput()).decode("utf-8", errors="replace")
        
        for line in raw.splitlines():
            line = line.strip()
            if not line: continue
            
            if line.startswith("STATUS:"):
                # General feedback
                msg = line[7:].strip()
                self.txtTrainLog.appendPlainText(f"  [INFO] {msg}")
            
            elif line.startswith("EPOCH:"):
                # Format: EPOCH:Current:Total:Loss
                parts = line.split(":")
                if len(parts) == 4:
                    self._train_dot_timer.stop()
                    curr, total, loss = int(parts[1]), int(parts[2]), float(parts[3])
                    self._current_train_epoch = curr
                    self.progEpoch.setValue(int((curr / total) * 100))
                    self.lblEpochCounter.setText(f"{curr} / {total}")
                    if self.lblValueLoss: self.lblValueLoss.setText(f"{loss:.4f}")

            elif line.startswith("METRIC:acc:"):
                # Accuracy/mAP report
                acc = float(line.split(":")[-1])
                if self.lblValueAccuracy: self.lblValueAccuracy.setText(f"{acc:.1f}%")
                if self.canvasAcc:
                    epoch = getattr(self, '_current_train_epoch', len(self.canvasAcc.x_data) + 1)
                    self.canvasAcc.update_data(epoch, acc, acc * 0.9)

            elif line.startswith("RESULT_MODEL_ENGINE:"):
                self._last_exported_engine = line[20:].strip()

            elif line.startswith("RESULT_MODEL_LOCAL:"):
                self._local_model_path = line[19:].strip()

            else:
                # Fallback to standard logging
                self.txtTrainLog.appendPlainText(line)

    def _animate_training_dots(self):
        """Cycle dots on epoch counter to show training is active."""
        self._train_dot_count = (self._train_dot_count % 3) + 1
        dots = "." * self._train_dot_count
        self.lblEpochCounter.setText(f"Training{dots}")

    def _toggle_train_console(self):
        """Toggle the training console visibility."""
        visible = not self.txtTrainLog.isVisible()
        self.txtTrainLog.setVisible(visible)
        self.btnToggleConsole.setText("▼ Console" if visible else "▶ Console")

    def _on_train_stderr(self):
        """Forward stderr logs to the training console."""
        if not self._train_process: return
        raw = bytes(self._train_process.readAllStandardError()).decode("utf-8", errors="replace")
        for line in raw.splitlines():
            line = line.strip()
            if line and "warn" not in line.lower():
                self.txtTrainLog.appendPlainText(f"  [SYSTEM] {line}")

    def _on_train_finished(self, exit_code, exit_status):
        """Cleanup and start fast validation on success (or if model exists despite crash)."""
        self._train_dot_timer.stop()
        self._training_is_running = False
        self._train_process = None

        # Check if a usable model exists even if the process crashed (e.g. TRT export OOM)
        project_root = os.path.dirname(os.path.abspath(__file__))
        local_pt = os.path.join(project_root, "src", "modules", "training", "best.pt")
        has_model = (self._local_model_path and os.path.exists(self._local_model_path)) or os.path.exists(local_pt)

        if exit_code == 0 or has_model:
            self.btnStartTraining.setText("✅ Training Complete")
            self.btnStartTraining.setEnabled(False)
            if exit_code != 0:
                self.txtTrainLog.appendPlainText("> TRT export crashed but model is available. Starting validation with .pt...")
            else:
                self.txtTrainLog.appendPlainText("> Success! Starting fast validation...")
            self.log_to_console("Training complete. Starting live validation camera...")
            self._start_fast_validation()
        else:
            self.btnStartTraining.setText("❌ Training Failed")
            self.log_to_console("Training failed. Check terminal for details.", is_error=True)

        self.update_workspace_counts()

    # ── Fast Validation (Post-Training Live Camera) ──────────────────────

    def _start_fast_validation(self):
        """Launch validator.py to stream live detections in the right panel."""
        # Stop any active data-collection camera first
        self._stop_webcam()

        # Determine model path (prefer .engine, fallback to .pt)
        project_root = os.path.dirname(os.path.abspath(__file__))
        local_engine = os.path.join(project_root, "src", "modules", "training", "best.engine")
        local_pt = os.path.join(project_root, "src", "modules", "training", "best.pt")

        if self._local_model_path and os.path.exists(self._local_model_path):
            model_path = self._local_model_path
        elif os.path.exists(local_engine):
            model_path = local_engine
        elif os.path.exists(local_pt):
            model_path = local_pt
        else:
            self.log_to_console("No trained model found for validation.", is_error=True)
            return

        # Get class names
        names = ""
        if self._class_data and self._class_data[0] and self._class_data[0].get("tag_panel"):
            names = ",".join(self._class_data[0]["tag_panel"].get_class_names())
        if not names:
            names = "Object"

        # Show camera UI, hide placeholder
        if hasattr(self, 'statusPlaceholder') and self.statusPlaceholder:
            self.statusPlaceholder.setVisible(False)
        self.trCamDisplay.setVisible(True)
        self.btnStopValidation.setVisible(True)
        self.btnSaveModel.setVisible(True)

        # Launch validator as QProcess
        self._val_stdout_buf = ""
        self._val_process = QProcess(self)
        env = QProcessEnvironment.systemEnvironment()
        self._val_process.setProcessEnvironment(env)
        self._val_process.setWorkingDirectory(project_root)

        script_path = os.path.join(project_root, "src", "modules", "training", "validator.py")
        args = [
            script_path,
            "--model", model_path,
            "--names", names,
            "--imgsz", str(self._capture_size),
        ]

        self._val_process.readyReadStandardOutput.connect(self._on_val_stdout)
        self._val_process.readyReadStandardError.connect(self._on_val_stderr)
        self._val_process.finished.connect(self._on_val_finished)

        self._val_process.setProgram(sys.executable)
        self._val_process.setArguments(args)
        self._val_process.start()
        self.txtTrainLog.appendPlainText("> Validation camera started.")

    def _on_val_stdout(self):
        """Parse IMG: frames from validator.py and display in trCamDisplay."""
        if not self._val_process:
            return
        raw = bytes(self._val_process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self._val_stdout_buf += raw

        # Only process complete lines (ending with \n)
        while "\n" in self._val_stdout_buf:
            line, self._val_stdout_buf = self._val_stdout_buf.split("\n", 1)
            line = line.strip()
            if line.startswith("IMG:"):
                img_data = line[4:]
                try:
                    data = base64.b64decode(img_data)
                    qimg = QImage.fromData(data)
                    if not qimg.isNull():
                        pix = QPixmap.fromImage(qimg)
                        self.trCamDisplay.setPixmap(
                            pix.scaled(self.trCamDisplay.size(),
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                        )
                except Exception:
                    pass
            elif line.startswith("STATUS:"):
                self.txtTrainLog.appendPlainText(f"  [VAL] {line[7:].strip()}")

    def _on_val_stderr(self):
        """Forward validator stderr to training log."""
        if not self._val_process:
            return
        raw = bytes(self._val_process.readAllStandardError()).decode("utf-8", errors="replace")
        for line in raw.splitlines():
            line = line.strip()
            if line:
                self.txtTrainLog.appendPlainText(f"  [VAL] {line}")

    def _on_val_finished(self):
        """Handle validator process exit."""
        self._val_process = None
        self.trCamDisplay.clear()
        self.trCamDisplay.setVisible(False)
        self.btnStopValidation.setVisible(False)
        if hasattr(self, 'statusPlaceholder') and self.statusPlaceholder:
            self.statusPlaceholder.setVisible(True)
            msg = self.training_mode_widget.findChild(QLabel, "statusMsg")
            if msg:
                msg.setText("Model Ready ✨")

    def _stop_fast_validation(self):
        """Stop the live validation camera and re-enable training."""
        if self._val_process and self._val_process.state() != QProcess.ProcessState.NotRunning:
            self._val_process.kill()
            self._val_process.waitForFinished(2000)
        # Re-enable training button so user can retrain
        if hasattr(self, 'btnStartTraining') and self.btnStartTraining:
            self.btnStartTraining.setText("🚀 Start Training")
            self.btnStartTraining.setEnabled(True)

    def _save_trained_model(self):
        """Copy the trained model from local training folder to projects/model/."""
        project_root = os.path.dirname(os.path.abspath(__file__))
        local_engine = os.path.join(project_root, "src", "modules", "training", "best.engine")
        local_pt = os.path.join(project_root, "src", "modules", "training", "best.pt")

        # Pick the best available model file
        if os.path.exists(local_engine):
            src_path = local_engine
            ext = ".engine"
        elif os.path.exists(local_pt):
            src_path = local_pt
            ext = ".pt"
        else:
            self.log_to_console("No trained model found to save.", is_error=True)
            return

        new_name, ok = QInputDialog.getText(
            self, "Save Model", "Enter model name:", text=self._current_project_name
        )
        if not ok or not new_name:
            return
        if not new_name.endswith(ext):
            new_name += ext

        dest_path = os.path.join("projects", "model", new_name)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        try:
            import shutil
            shutil.copy2(src_path, dest_path)
            self.log_to_console(f"Model saved to: projects/model/{new_name}")
            self.txtTrainLog.appendPlainText(f"✨ Saved to projects/model/{new_name}")
            self.update_workspace_counts()
        except Exception as e:
            self.log_to_console(f"Error saving model: {e}", is_error=True)

if __name__ == '__main__':
    # Suppress Qt/DRM warnings on Jetson
    import os
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

    # Disable aggressive auto-scaling on Linux/Jetson which explodes layout sizes
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    
    # Global Font Correction for PyQt5
    # Bump the base font size to match the visual scale of PyQt6
    base_font = app.font()
    base_font.setPointSize(base_font.pointSize() + 2)
    app.setFont(base_font)
    
    # Custom dark tooltip — bypasses Windows native white renderer
    _tooltip_filter = DarkTooltipFilter()
    app.installEventFilter(_tooltip_filter)
    
    window = AICodingLab()
    window.showMaximized()
    sys.exit(app.exec())