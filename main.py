import sys
import os

# Suppress noisy C-library warnings on Jetson (must be set before imports)
os.environ["ORT_LOG_LEVEL"] = "ERROR"
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.xcb.xcbclipboard=false"

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
from PyQt5.QtCore import Qt, QDir, QProcess, QProcessEnvironment, QTimer, QEvent, QPoint, QPropertyAnimation, QEasingCurve
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

    def set_small_mode(self, is_small):
        if not hasattr(self, 'axes') or self.axes is None:
            return
        size = 5 if is_small else 12
        lbl_size = 6 if is_small else 9
        try:
            self.axes.title.set_fontsize(size)
            self.axes.title.set_pad(1 if is_small else 6)
            curr_label = self.axes.get_ylabel()
            if curr_label:
                self.axes.set_ylabel(str(curr_label), fontsize=lbl_size, labelpad=1 if is_small else 4)
            self.axes.tick_params(labelsize=lbl_size-1, pad=1 if is_small else 4)

            if self.axes.get_legend():
                for text in self.axes.get_legend().get_texts():
                    text.set_fontsize(lbl_size-1)
            self.draw_idle()
        except Exception:
            pass

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
                painter.setPen(QPen(QColor(255, 255, 255, 80), 1, Qt.DashDotLine))
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
            
            # Selected box glow
            if is_selected:
                glow = QColor(color.red(), color.green(), color.blue(), 25)
                painter.setPen(QPen(glow, 6))
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(pixel_box.adjusted(-2, -2, 2, 2))

            # Box Body
            pen_width = 2 if is_selected else 1
            painter.setPen(QPen(color, pen_width))
            painter.setBrush(QColor(color.red(), color.green(), color.blue(), 35 if is_selected else 15))
            painter.drawRect(pixel_box)

            # Label tag
            name = box_data["class_name"] or f"Tag {box_data['class_id']}"
            font = painter.font()
            font.setPixelSize(11)
            font.setBold(True)
            painter.setFont(font)
            lbl_w = painter.fontMetrics().horizontalAdvance(name) + 16
            lbl_h = 20
            label_rect = QRect(pixel_box.left(), pixel_box.top() - lbl_h, lbl_w, lbl_h)
            if label_rect.top() < rect.top(): label_rect.moveTop(pixel_box.top())
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(label_rect, 4, 4)

            painter.setPen(Qt.white)
            painter.drawText(label_rect, Qt.AlignCenter, name)

            # Handles for selected box
            if is_selected:
                hs = self.handle_size // 2 + 1
                for h_pos in self._get_handles(pixel_box).values():
                    painter.setBrush(Qt.white)
                    painter.setPen(QPen(color, 2))
                    painter.drawEllipse(h_pos, hs, hs)

        # 5. Draw currently drawing box
        if self.is_drawing:
            color = QColor(palette[self.active_class_id % len(palette)])
            draw_box = QRect(self.start_point, self.end_point).normalized()
            if rect.isValid(): draw_box = draw_box.intersected(rect)
            painter.setBrush(QColor(color.red(), color.green(), color.blue(), 18))
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
# Level Badge — Animated half-circle / flag-ribbon navigation
# ────────────────────────────────────────────────────────────

LEVEL_CONFIG = {
    "Beginner":     {"color": "#22c55e", "icon": "⭐", "trans_key": "LVL_BEGINNER"},
    "Intermediate": {"color": "#eab308", "icon": "🚀", "trans_key": "LVL_INTERMEDIATE"},
    "Advanced":     {"color": "#ef4444", "icon": "🏆", "trans_key": "LVL_ADVANCED"},
}

class LevelBadge(QWidget):
    """Level tab icon — colored circle (active) or muted icon (inactive) inside a shared nav bar."""
    level_clicked = pyqtSignal(str)

    def __init__(self, level_key, color, icon, is_small=False, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)  # CRITICAL: enables background rendering on QWidget
        self._level_key = level_key
        self._color = color
        self._icon = icon
        self._active = False
        self._count = 0
        self._is_small = is_small
        self.setCursor(Qt.PointingHandCursor)

        # Size constants — the icon circle size
        self._std_sz, self._small_sz = 40, 28

        sz = self._small_sz if is_small else self._std_sz
        self.setFixedSize(sz, sz)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        fs_icon = 14 if is_small else 20

        self._icon_lbl = QLabel(icon)
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setStyleSheet(f"font-size: {fs_icon}px; background: transparent;")
        layout.addWidget(self._icon_lbl)

        self._apply_inactive_style()

    def _hex_to_rgb(self, hex_color):
        h = hex_color.lstrip('#')
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def _apply_active_style(self):
        sz = self._small_sz if self._is_small else self._std_sz
        fs = 14 if self._is_small else 20
        self._icon_lbl.setStyleSheet(f"font-size: {fs}px; background: transparent; color: #6d28d9;")
        # White frosted bubble — pops against the purple-blue gradient bar
        self.setObjectName("lvlActive")
        self.setStyleSheet(f"""
            QWidget#lvlActive {{
                background: rgba(255, 255, 255, 0.92);
                border-radius: {sz//2}px;
                border: 2px solid rgba(255, 255, 255, 0.8);
            }}
        """)

    def _apply_inactive_style(self):
        sz = self._small_sz if self._is_small else self._std_sz
        fs = 14 if self._is_small else 20
        self._icon_lbl.setStyleSheet(f"font-size: {fs}px; background: transparent; color: rgba(255,255,255,0.85);")
        self.setObjectName("lvlInactive")
        self.setStyleSheet(f"""
            QWidget#lvlInactive {{
                background: transparent;
                border-radius: {sz//2}px;
                border: none;
            }}
            QWidget#lvlInactive:hover {{
                background: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
            }}
        """)

    def set_active(self, active):
        if active == self._active:
            return
        self._active = active
        if active:
            self._apply_active_style()
        else:
            self._apply_inactive_style()

    def set_count(self, count):
        self._count = count

    def update_resolution(self, is_small):
        self._is_small = is_small
        sz = self._small_sz if is_small else self._std_sz
        self.setFixedSize(sz, sz)
        if self._active:
            self._apply_active_style()
        else:
            self._apply_inactive_style()
        # Also update the nav container bar if it exists
        if hasattr(self.parent(), '_nav_container') if self.parent() else False:
            pass  # handled by MainWindow

    def retranslate(self, strings):
        # No text labels in the new icon-only design — nothing to translate
        pass

    def mousePressEvent(self, event):
        self.level_clicked.emit(self._level_key)
        super().mousePressEvent(event)


# ────────────────────────────────────────────────────────────
#  Dynamic Curriculum Card Widget
# ────────────────────────────────────────────────────────────


class CurriculumCard(QFrame):
    def __init__(self, filename, title, level, icon, color, desc, on_load_click, is_small=False):
        super().__init__()
        self.filename = filename
        card_h = 50 if is_small else 90
        self.setMinimumHeight(card_h)
        self.setMaximumHeight(card_h + 20)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumWidth(0)
        
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
        # Scale margins and spacing
        margin = 6 if is_small else 12
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(margin)
        
        # 1. Icon
        icon_size = 24 if is_small else 40
        icon_font = 12 if is_small else 24
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
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI", icon_font))
        layout.addWidget(icon_lbl)
        
        # 2. Body Container (V-Box to hold the two horizontal rows)
        body_vbox = QVBoxLayout()
        body_vbox.setSpacing(4)
        
        # --- ROW 1: Title + Badge ---
        row1 = QHBoxLayout()
        title_font = 8 if is_small else 15
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-weight: bold; font-size: {title_font}px; color: #1e293b; background: transparent;")
        title_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_lbl.setMinimumWidth(0)
        title_lbl.setWordWrap(True)
        
        # Level Badge
        badge_colors = {"Beginner": "#08a54f", "Intermediate": "#f6710b", "Advanced": "#b51414"}
        badge_bg = badge_colors.get(level, "#64748b")
        badge = QLabel(level)
        badge.setAlignment(Qt.AlignCenter)
        badge_w, badge_h = (52, 14) if is_small else (80, 20)
        badge_fs = 6 if is_small else 9
        badge.setFixedSize(badge_w, badge_h)
        badge.setStyleSheet(f"background: {badge_bg}; color: white; border-radius: {badge_fs}px; font-size: {badge_fs}px; font-weight: bold;")
        
        row1.addWidget(title_lbl, 1)
        row1.addWidget(badge)
        body_vbox.addLayout(row1)
        
        # --- ROW 2: Description + Load Button ---
        row2 = QHBoxLayout()
        desc_font = 6 if is_small else 13
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(f"color: #475569; font-size: {desc_font}px; background: transparent;")
        desc_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        desc_lbl.setMinimumWidth(0)
        desc_lbl.setWordWrap(True)
        
        # Load Button
        btn_load = QPushButton("Load")
        btn_load.setCursor(Qt.PointingHandCursor)
        btn_w, btn_h = (52, 14) if is_small else (80, 28)
        btn_load.setFixedSize(btn_w, btn_h)
        btn_load.setStyleSheet(f"""
            QPushButton {{ 
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #3b82f6, stop:1 #7c3aed); 
                color: white; 
                border-radius: {btn_h//2}px; 
                font-weight: bold; 
                font-size: {desc_font+2}px; 
                border: none;
                padding: 2px;
            }}
            QPushButton:hover {{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #2563eb, stop:1 #6d28d9);
            }}
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
    _spin_arrow_cache = None  # class-level cache for arrow image paths

    @staticmethod
    def _get_spin_arrow_paths():
        """Generate tiny triangle arrow PNGs for QSpinBox buttons (once, cached)."""
        if AICodingLab._spin_arrow_cache:
            return AICodingLab._spin_arrow_cache
        import tempfile
        from PyQt5.QtGui import QPixmap, QPainter, QColor, QPolygonF
        from PyQt5.QtCore import QPointF, Qt as _Qt
        _dir = tempfile.mkdtemp(prefix="ailab_arrows_")
        paths = {}
        for name, points in [
            ("up",   [QPointF(2, 8), QPointF(8, 2), QPointF(14, 8)]),
            ("down", [QPointF(2, 2), QPointF(8, 8), QPointF(14, 2)]),
        ]:
            px = QPixmap(16, 10)
            px.fill(_Qt.transparent)
            p = QPainter(px)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setBrush(QColor("#475569"))
            p.setPen(_Qt.NoPen)
            p.drawPolygon(QPolygonF(points))
            p.end()
            path = os.path.join(_dir, f"arrow_{name}.png")
            px.save(path, "PNG")
            paths[name] = path
        AICodingLab._spin_arrow_cache = (paths["up"], paths["down"])
        return AICodingLab._spin_arrow_cache

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 480) # Ensure it CAN shrink to fit small Jetson screens
        
        # 1. Setup Paths
        self.ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "ui")
        
        self.file_manager = FileManager(os.path.dirname(os.path.abspath(__file__)))
        self.current_lang = "en" # Default to English
        self.is_small_screen = True
        self.current_open_file = None
        print(STRINGS[self.current_lang]["HINT_DIR_INITIALIZED"])
        
        # 2. Load the Main Shell
        try:
            loadUi(os.path.join(self.ui_dir, "main_window.ui"), self)
            self.base_style = self.styleSheet() # Store template for clean resolution switching
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
                v_splitter.setSizes([220, 340])


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

        self.btnResToggle = self.findChild(QPushButton, "btnResToggle")
        if self.btnResToggle:
            self.btnResToggle.setChecked(True)
            self.btnResToggle.clicked.connect(self.toggle_resolution)

        # 6. Wire up Running Mode internal components
        # A) Editor & Basic Buttons
        self.monacoPlaceholder = self.running_mode_widget.findChild(QTextEdit, "monacoPlaceholder")
        self.btnCreateFile = self.running_mode_widget.findChild(QPushButton, "btnCreateFile")
        self.btnRunCode = self.running_mode_widget.findChild(QPushButton, "btnRunCode")
        self.tabPlus = self.running_mode_widget.findChild(QPushButton, "tabPlus")
        self.tabContainer = self.running_mode_widget.findChild(QWidget, "tabContainer")
        
        # DYNAMIC CURRICULUM DISCOVERY
        self.hubContentLayout = self.running_mode_widget.findChild(QVBoxLayout, "hubContentLayout")
        
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
        self.leftSplitter = self.running_mode_widget.findChild(QSplitter, "leftSplitter")
        self.runningEditorSplitter = self.running_mode_widget.findChild(QSplitter, "editorSplitter")
        self.rightSplitter = self.running_mode_widget.findChild(QSplitter, "rightSplitter")

        # 2b) Create Floating Assistant Bot Button
        self._setup_assistant_bot_button()

        # B) HUB TABS & STACKED WIDGET
        # FIX: We must find these child widgets inside running_mode_widget first!
        self.hubStackedWidget = self.running_mode_widget.findChild(QStackedWidget, "hubStackedWidget")
        self.tabExamples = self.running_mode_widget.findChild(QPushButton, "tabExamples")
        self.tabFunctions = self.running_mode_widget.findChild(QPushButton, "tabFunctions")
        self.tabWorkspace = self.running_mode_widget.findChild(QPushButton, "tabWorkspace")

        if self.hubStackedWidget:
            if self.tabExamples: self.tabExamples.clicked.connect(lambda: self._switch_hub_tab(0))
            if self.tabFunctions: self.tabFunctions.clicked.connect(lambda: self._switch_hub_tab(1))
            if self.tabWorkspace: self.tabWorkspace.clicked.connect(lambda: self._switch_hub_tab(2))

        # Apply initial hub tab styling (Examples active by default)
        self._update_hub_tab_styles(0)

        # Setup Level Navigation (must be after hubStackedWidget is found)
        self._setup_level_navigation()
        self.populate_curriculum_hub()

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
            populate_functions_tab(self.running_mode_widget, is_small=self.is_small_screen, lang=self.current_lang)
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

        # leftSplitter is a vertical splitter wrapping hubContainer only (1 child)
        # Ensure it doesn't interfere with mainSplitter's horizontal dragging
        if self.leftSplitter:
            self.leftSplitter.setChildrenCollapsible(False)
            from PyQt5.QtWidgets import QSizePolicy
            self.leftSplitter.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.leftSplitter.setMinimumWidth(80)

        # Middle Column: Editor (top) vs Console (bottom) -> Ratio 3:1
        if self.runningEditorSplitter:
            self.runningEditorSplitter.setChildrenCollapsible(False)
            self.runningEditorSplitter.setStretchFactor(0, 3)
            self.runningEditorSplitter.setStretchFactor(1, 1)
            self.runningEditorSplitter.setSizes([600, 200])
            # Reduce console minimum height so it doesn't fight the splitter
            console = self.running_mode_widget.findChild(QFrame, "consoleContainer")
            if console: console.setMinimumHeight(30)

        # Right Column: Camera (top) vs Results (bottom) -> Ratio 1:1
        if self.rightSplitter:
            self.rightSplitter.setChildrenCollapsible(False)
            self.rightSplitter.setStretchFactor(0, 1)
            self.rightSplitter.setStretchFactor(1, 1)
            self.rightSplitter.setSizes([300, 300])

        # Ensure all mainSplitter children have Ignored size policy so handles drag smoothly
        if self.mainSplitter:
            from PyQt5.QtWidgets import QSizePolicy
            for i in range(self.mainSplitter.count()):
                w = self.mainSplitter.widget(i)
                if w: w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)


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
        for splitter in [self.mainSplitter, self.leftSplitter, self.runningEditorSplitter, self.rightSplitter]:
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

        # 11b. Apply initial resolution scaling (default is small screen)
        self.refresh_ui_resolution(is_transition=False)

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

    # --- Assistant Bot Button ---
    def _setup_assistant_bot_button(self):
        """Create a floating circular assistant bot button inside the code editor."""
        if not hasattr(self, 'monacoPlaceholder') or not self.monacoPlaceholder:
            return

        btn_size = 48 if self.is_small_screen else 56
        padding = 14

        self.btnAssistantBot = QPushButton(self.monacoPlaceholder)
        self.btnAssistantBot.setObjectName("btnAssistantBot")
        self.btnAssistantBot.setFixedSize(btn_size, btn_size)
        self.btnAssistantBot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnAssistantBot.setText("🤖")
        self.btnAssistantBot.setToolTip("AI Assistant — Ask for help with your code")

        self._apply_assistant_bot_style(btn_size)
        self.btnAssistantBot.clicked.connect(self._on_assistant_bot_clicked)

        # Position inside the editor: bottom-right corner
        self._reposition_assistant_bot()
        self.btnAssistantBot.show()
        self.btnAssistantBot.raise_()

        # Install event filter on editor so button repositions when editor is resized
        self.monacoPlaceholder.installEventFilter(self)

    def _apply_assistant_bot_style(self, btn_size):
        """Apply the purple/navy/blue gradient style to the assistant bot button."""
        fs = 20 if self.is_small_screen else 24
        self.btnAssistantBot.setStyleSheet(f"""
            QPushButton#btnAssistantBot {{
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c3aed, stop:0.5 #6d28d9, stop:1 #3b82f6
                );
                color: white;
                border: 2px solid rgba(139, 92, 246, 0.6);
                border-radius: {btn_size // 2}px;
                font-size: {fs}px;
                padding: 0px;
            }}
            QPushButton#btnAssistantBot:hover {{
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8b5cf6, stop:0.5 #7c3aed, stop:1 #2563eb
                );
                border: 2px solid rgba(139, 92, 246, 0.9);
            }}
            QPushButton#btnAssistantBot:pressed {{
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6d28d9, stop:0.5 #5b21b6, stop:1 #1e40af
                );
            }}
        """)

    def _reposition_assistant_bot(self):
        """Position the button at the bottom-right corner inside the editor widget."""
        if not hasattr(self, 'btnAssistantBot') or not hasattr(self, 'monacoPlaceholder'):
            return
        if not self.monacoPlaceholder or not self.btnAssistantBot:
            return
        btn_size = self.btnAssistantBot.width()
        padding = 26  # Extra padding to clear the scrollbar (~10px wide)
        editor_w = self.monacoPlaceholder.width()
        editor_h = self.monacoPlaceholder.height()
        x = editor_w - btn_size - padding
        y = int(editor_h * 0.68) - btn_size // 2  # ~2/3 down the editor
        self.btnAssistantBot.move(x, y)
        self.btnAssistantBot.raise_()
        # Keep chat panel aligned too
        if hasattr(self, '_chat_panel') and self._chat_panel.isVisible():
            self._reposition_chat_panel()

    def _on_assistant_bot_clicked(self):
        """Toggle the assistant chat panel open/closed."""
        if not hasattr(self, '_chat_panel'):
            self._init_assistant_panel()
            return
        if self._chat_panel.isVisible():
            self._chat_panel.hide()
        else:
            self._reposition_chat_panel()
            target_pos = self._chat_panel.pos()
            self._chat_panel.show_animated(target_pos)

    def _init_assistant_panel(self):
        """Create the chat panel, load the LLM, and show the panel."""
        from src.modules.LLM.chat_panel import AssistantChatPanel
        from src.modules.LLM.assistant import LLMAssistant
        from src.modules.LLM import model_config as _mcfg

        # Build panel parented to the editor
        self._chat_panel = AssistantChatPanel(
            parent=self.monacoPlaceholder,
            is_small=self.is_small_screen,
        )

        # Populate model selector combobox
        models = _mcfg.get_available_models()
        active_key = next(
            (k for k, cfg in _mcfg.MODEL_REGISTRY.items()
             if cfg is _mcfg.ACTIVE_MODEL), "qwen"
        )
        self._chat_panel.populate_models(models, active_key)

        self._chat_panel.set_status("loading")
        self._chat_panel.show_loading_message(STRINGS[self.current_lang]["BOT_LOADING"].format(_mcfg.ACTIVE_MODEL['name']))
        self._reposition_chat_panel()
        target_pos = self._chat_panel.pos()
        self._chat_panel.show_animated(target_pos)

        # Connect signals
        self._chat_panel.ask_requested.connect(self._bot_ask)
        self._chat_panel.fix_requested.connect(self._bot_fix)
        self._chat_panel.explain_requested.connect(self._bot_explain)
        self._chat_panel.close_requested.connect(self._chat_panel.hide)
        self._chat_panel.model_changed.connect(self._bot_switch_model)

        # Load LLM in background
        self._llm_first_load = True
        self._llm_assistant = LLMAssistant()
        self._llm_assistant.load(
            on_ready=self._on_llm_ready,
            on_error=self._on_llm_error,
        )

    def _on_llm_ready(self):
        """Called from background thread — use signal for thread-safe delivery."""
        if hasattr(self, '_chat_panel'):
            self._chat_panel._streaming_done.emit()
        QTimer.singleShot(0, self._llm_ready_ui)

    def _llm_ready_ui(self):
        if not hasattr(self, '_chat_panel'):
            return
        from src.modules.LLM import model_config as _mcfg
        if getattr(self, '_llm_first_load', False):
            # First launch — no warmup needed, show ready immediately
            self._llm_first_load = False
            self._chat_panel.set_status("ready")
            bubble = self._chat_panel.start_assistant_message()
            bubble.set_text(STRINGS[self.current_lang]["BOT_READY"].format(_mcfg.ACTIVE_MODEL['name']))
            self._chat_panel.finish_streaming()
        else:
            # Model switch — silent 3s delay while previous model cleans up
            QTimer.singleShot(3000, self._llm_stabilized_ui)

    def _llm_stabilized_ui(self):
        if not hasattr(self, '_chat_panel'):
            return
        from src.modules.LLM import model_config as _mcfg
        self._chat_panel.set_status("ready")
        bubble = self._chat_panel.start_assistant_message()
        bubble.set_text(STRINGS[self.current_lang]["BOT_READY"].format(_mcfg.ACTIVE_MODEL['name']))
        self._chat_panel.finish_streaming()

    def _on_llm_error(self, msg: str):
        if hasattr(self, '_chat_panel'):
            self._chat_panel._error_received.emit(msg)

    def _llm_error_ui(self, msg: str):
        if not hasattr(self, '_chat_panel'):
            return
        self._chat_panel.set_status("error")
        self._chat_panel.show_error(msg)

    def _bot_switch_model(self, model_key: str):
        """Handle model switch from the combobox."""
        from src.modules.LLM import model_config as _mcfg

        # Check if already on this model
        current_key = next(
            (k for k, cfg in _mcfg.MODEL_REGISTRY.items()
             if cfg is _mcfg.ACTIVE_MODEL), None
        )
        if model_key == current_key:
            return

        # Cancel + unload old model (non-blocking — won't freeze GUI)
        if hasattr(self, '_llm_assistant'):
            self._llm_assistant.cancel()
            self._llm_assistant.unload()

        # Clear any active streaming state
        if hasattr(self, '_chat_panel'):
            self._chat_panel._streaming_bubble = None
            self._chat_panel._token_count = 0

        # Switch the active model config
        new_cfg = _mcfg.set_active_model(model_key)

        # Update UI
        self._chat_panel.set_status("loading")
        self._chat_panel.show_loading_message(STRINGS[self.current_lang]["BOT_LOADING"].format(new_cfg['name']))

        # Create fresh assistant and load new model
        from src.modules.LLM.assistant import LLMAssistant
        self._llm_assistant = LLMAssistant()
        self._llm_assistant.load(
            on_ready=self._on_llm_ready,
            on_error=self._on_llm_error,
        )

    def _bot_ask(self, question: str):
        if not hasattr(self, '_llm_assistant'):
            return
        self._chat_panel.add_user_message(question)

        code = self.monacoPlaceholder.toPlainText() if hasattr(self, 'monacoPlaceholder') else ""
        console = self.consoleBody.toPlainText() if hasattr(self, 'consoleBody') else ""

        # Short-circuit: check for missing workflow steps and answer directly
        from src.modules.LLM.prompt_builder import _detect_missing_workflow
        workflow_hint = _detect_missing_workflow(code, self.current_lang)
        if workflow_hint:
            # Check if the question is about the missing step
            q_lower = question.lower()
            display_keywords = ["display", "show", "camera", "feed", "screen", "hiển thị",
                                "màn hình", "xem", "missing", "thiếu", "không thấy"]
            if any(kw in q_lower for kw in display_keywords):
                bubble = self._chat_panel.start_assistant_message()
                bubble.set_text(workflow_hint)
                self._chat_panel.finish_streaming()
                return

        self._chat_panel.set_status("thinking")
        self._chat_panel.start_assistant_message()

        panel = self._chat_panel
        assistant = self._llm_assistant  # capture current instance

        def on_token(t):
            if self._llm_assistant is not assistant:
                return  # stale callback from old model
            panel._token_received.emit(t)

        def on_done(full):
            if self._llm_assistant is not assistant:
                return
            panel._streaming_done.emit()

        def on_error(msg):
            if self._llm_assistant is not assistant:
                return
            panel._error_received.emit(msg)

        self._llm_assistant.ask(
            question=question,
            editor_code=code,
            console_output=console,
            lang=self.current_lang,
            on_token=on_token,
            on_done=on_done,
            on_error=on_error,
        )

    def _bot_fix(self):
        if not hasattr(self, '_llm_assistant'):
            return
        code = self.monacoPlaceholder.toPlainText() if hasattr(self, 'monacoPlaceholder') else ""
        console = self.consoleBody.toPlainText() if hasattr(self, 'consoleBody') else ""
        # Grab the full traceback — include "File" lines (contain line numbers),
        # "error"/"traceback" lines, and indented code context lines
        error_lines = [
            l for l in console.splitlines()
            if "error" in l.lower() or "traceback" in l.lower()
            or l.strip().startswith("File ") or l.strip().startswith("line ")
            or (l.startswith("    ") and l.strip())  # indented traceback context
        ]
        error_text = "\n".join(error_lines[-10:]) if error_lines else ""

        # Short-circuit: if no console error AND code compiles, skip LLM entirely
        if not error_text.strip() and code.strip():
            try:
                compile(code, "<student>", "exec")
                # Code is valid — no need to waste LLM inference
                s = STRINGS[self.current_lang]
                no_err = "Tuyệt vời! Không tìm thấy lỗi nào. 🎉" if self.current_lang == "vi" else "Great job! No errors found. 🎉"
                self._chat_panel.add_user_message(s["BOT_FIX_MSG"])
                bubble = self._chat_panel.start_assistant_message()
                bubble.set_text(no_err)
                self._chat_panel.finish_streaming()
                return
            except SyntaxError:
                pass  # there IS an error — fall through to LLM

        # If no error_text from console but compile failed, let build_fix_prompt handle it
        if not error_text.strip():
            error_text = ""

        self._chat_panel.add_user_message(STRINGS[self.current_lang]["BOT_FIX_MSG"])
        self._chat_panel.set_status("thinking")
        self._chat_panel.start_assistant_message()

        panel = self._chat_panel
        assistant = self._llm_assistant

        def on_token(t):
            if self._llm_assistant is not assistant:
                return
            panel._token_received.emit(t)

        def on_done(full):
            if self._llm_assistant is not assistant:
                return
            panel._fix_done.emit(full)

        def on_error(msg):
            if self._llm_assistant is not assistant:
                return
            panel._error_received.emit(msg)

        self._llm_assistant.fix_error(
            error_text=error_text,
            editor_code=code,
            lang=self.current_lang,
            on_token=on_token,
            on_done=on_done,
            on_error=on_error,
        )

    def _bot_explain(self):
        if not hasattr(self, '_llm_assistant'):
            return
        code = self.monacoPlaceholder.toPlainText() if hasattr(self, 'monacoPlaceholder') else ""
        if not code.strip():
            self._chat_panel.show_error(STRINGS[self.current_lang]["BOT_NO_CODE"])
            return

        self._chat_panel.add_user_message(STRINGS[self.current_lang]["BOT_EXPLAIN_MSG"])
        self._chat_panel.set_status("thinking")
        self._chat_panel.start_assistant_message()

        panel = self._chat_panel
        assistant = self._llm_assistant

        def on_token(t):
            if self._llm_assistant is not assistant:
                return
            panel._token_received.emit(t)

        def on_done(full):
            if self._llm_assistant is not assistant:
                return
            panel._streaming_done.emit()

        def on_error(msg):
            if self._llm_assistant is not assistant:
                return
            panel._error_received.emit(msg)

        self._llm_assistant.explain_code(
            editor_code=code,
            lang=self.current_lang,
            on_token=on_token,
            on_done=on_done,
            on_error=on_error,
        )

    def _reposition_chat_panel(self):
        """Position chat panel on the right side of the editor."""
        if not hasattr(self, '_chat_panel') or not hasattr(self, 'btnAssistantBot'):
            return
        btn = self.btnAssistantBot
        panel = self._chat_panel
        editor_w = self.monacoPlaceholder.width()
        panel_w = panel.width()
        panel_h = panel.minimumHeight()

        # Align right edge of panel with right edge of editor, clear scrollbar
        x = editor_w - panel_w - 20
        # Place panel above the button with a small gap
        y = btn.y() - panel_h - 10
        # Clamp so it doesn't go above the editor top
        y = max(8, y)
        panel.move(x, y)

    def resizeEvent(self, event):
        """Handle window resize to reposition floating assistant bot button."""
        super().resizeEvent(event)
        if hasattr(self, 'btnAssistantBot'):
            QTimer.singleShot(10, self._reposition_assistant_bot)

    def eventFilter(self, obj, event):
        """Reposition assistant bot button when the editor widget is resized."""
        from PyQt5.QtCore import QEvent
        if hasattr(self, 'monacoPlaceholder') and obj is self.monacoPlaceholder:
            if event.type() == QEvent.Resize:
                QTimer.singleShot(0, self._reposition_assistant_bot)
        return super().eventFilter(obj, event)

    # --- Language Support ---
    def set_language(self, lang_code):
        """Switch application language and refresh UI labels."""
        if self.current_lang == lang_code: return
        self.current_lang = lang_code
        # Sync language to the code editor for tooltip translations
        if hasattr(self, 'monacoPlaceholder') and hasattr(self.monacoPlaceholder, '_lang'):
            self.monacoPlaceholder._lang = lang_code
        self.retranslate_ui()
        # Update Level Navigation badge labels
        if hasattr(self, '_level_badges'):
            s = STRINGS[self.current_lang]
            for badge in self._level_badges.values():
                badge.retranslate(s)
        # Full refresh of dynamic content
        self.populate_curriculum_hub()
        self.update_workspace_counts()
        # Refresh function library with new language
        try:
            from src.modules.function_library import populate_functions_tab
            populate_functions_tab(self.running_mode_widget, is_small=self.is_small_screen, lang=self.current_lang)
        except Exception:
            pass

    def toggle_resolution(self, checked):
        """Toggle between standard and small (10-inch) screen layout."""
        self.is_small_screen = checked
        
        if checked:
            # Small Screen (16:9 / 16:10 for Jetson)
            self.setMinimumSize(800, 480)
            self.resize(1024, 600)
        else:
            self.setMinimumSize(900, 600)
            self.resize(1280, 800)
            
        self.refresh_ui_resolution(is_transition=True)
        try:
            self.log_to_console(f"Layout changed to {'Small Screen' if checked else 'Standard'}")
        except Exception:
            pass
    def refresh_ui_resolution(self, is_transition=False):
        """Update font sizes and dimensions across the application."""
        is_small = self.is_small_screen
        
        # 1. Update Core Header/Footer font sizes via Variables from CLEAN Template
        style = getattr(self, "base_style", self.styleSheet())
        
        title_font = 11 if is_small else 22
        subtitle_font = 7 if is_small else 12
        footer_font = 8 if is_small else 13
        
        # Regex replacement for specific font sizes in stylesheet
        import re
        style = re.sub(r"(#appTitle\s*\{\s*color:\s*white;\s*font-size:\s*)\d+px", rf"\g<1>{title_font}px", style)
        style = re.sub(r"(#appSubtitle\s*\{\s*color:\s*rgba\(255,255,255,0.8\);\s*font-size:\s*)\d+px", rf"\g<1>{subtitle_font}px", style)
        style = re.sub(r"(#footerHints,\s*#footerCredit\s*\{\s*color:\s*white;\s*font-size:\s*)\d+px", rf"\g<1>{footer_font}px", style)

        # Mode toggle buttons padding/font/radius
        _mode_fs = 9 if is_small else 14
        _mode_pad = '2px 6px' if is_small else '6px 16px'
        _mode_br = 8 if is_small else 14
        
        # We ensure border is set and radius is correct to prevent "sharp corners"
        style = re.sub(
            r"(#btnRunMode,\s*#btnTrainMode\s*\{[^}]*?)padding:\s*[\d\w\s]+;",
            rf"\g<1>padding: {_mode_pad};", style)
        style = re.sub(
            r"(#btnRunMode,\s*#btnTrainMode\s*\{[^}]*?)border-radius:\s*\d+px",
            rf"\g<1>border-radius: {_mode_br}px", style)
            
        # Insert/Update font-size (Use more robust approach: replace if exists, else insert before })
        if "font-size:" in re.search(r"#btnRunMode,\s*#btnTrainMode\s*\{([^}]*)\}", style).group(1):
            style = re.sub(r"(#btnRunMode,\s*#btnTrainMode\s*\{[^}]*?)font-size:\s*\d+px", rf"\g<1>font-size: {_mode_fs}px", style)
        else:
            style = re.sub(r"(#btnRunMode,\s*#btnTrainMode\s*\{[^}]*?)(\s*\})", rf"\g<1>font-size: {_mode_fs}px;\g<2>", style)

        # Language toggle font-size and padding
        _lang_fs = 9 if is_small else 16
        _lang_pad = '2px 5px' if is_small else '4px 10px'
        _lang_br = 8 if is_small else 14
        style = re.sub(
            r"(#btnLangEN,\s*#btnLangVN\s*\{[^}]*?)font-size:\s*\d+px",
            rf"\g<1>font-size: {_lang_fs}px", style)
        style = re.sub(
            r"(#btnLangEN,\s*#btnLangVN\s*\{[^}]*?)padding:\s*[\d\w\s]+;",
            rf"\g<1>padding: {_lang_pad};", style)
        style = re.sub(
            r"(#btnLangEN,\s*#btnLangVN\s*\{[^}]*?)border-radius:\s*\d+px",
            rf"\g<1>border-radius: {_lang_br}px", style)

        # Toggle containers border-radius
        _cont_br = 10 if is_small else 18
        style = re.sub(r"(#toggleContainer\s*\{[^}]*?)border-radius:\s*\d+px", rf"\g<1>border-radius: {_cont_br}px", style)
        style = re.sub(r"(#langToggleContainer\s*\{[^}]*?)border-radius:\s*\d+px", rf"\g<1>border-radius: {_cont_br}px", style)

        # Resolution toggle button sizing
        _res_sz = 22 if is_small else 34
        _res_fs = 11 if is_small else 18
        _res_br = 11 if is_small else 17
        style = re.sub(r"(#btnResToggle\s*\{[^}]*?)border-radius:\s*\d+px", rf"\g<1>border-radius: {_res_br}px", style)
        style = re.sub(r"(#btnResToggle\s*\{[^}]*?)font-size:\s*\d+px", rf"\g<1>font-size: {_res_fs}px", style)
        style = re.sub(r"(#btnResToggle\s*\{[^}]*?)min-width:\s*\d+px", rf"\g<1>min-width: {_res_sz}px", style)
        style = re.sub(r"(#btnResToggle\s*\{[^}]*?)min-height:\s*\d+px", rf"\g<1>min-height: {_res_sz}px", style)

        try:
            self.setStyleSheet(style)
        except Exception as e:
            print(f"Error applying stylesheet: {e}")

        # Header and Footer frame height scaling - LOOSEN CONSTRAINTS to fix setGeometry errors
        if hasattr(self, 'headerFrame') and self.headerFrame:
            h_min = 36 if is_small else 56
            h_max = 42 if is_small else 64
            self.headerFrame.setMinimumHeight(h_min)
            self.headerFrame.setMaximumHeight(h_max)
            # Scale header layout margins for small screen
            h_layout = self.headerFrame.layout()
            if h_layout:
                h_layout.setContentsMargins(8 if is_small else 20, 4 if is_small else 6, 6 if is_small else 12, 4 if is_small else 6)
        if hasattr(self, 'footerFrame') and self.footerFrame:
            f_min = 20 if is_small else 26
            f_max = 24 if is_small else 32
            self.footerFrame.setMinimumHeight(f_min)
            self.footerFrame.setMaximumHeight(f_max)
        
        # 2. Update Splitter Sizes (Only during transition)
        if is_transition:
            if is_small:
                if self.mainSplitter: self.mainSplitter.setSizes([180, 564, 280])
                if self.runningEditorSplitter: self.runningEditorSplitter.setSizes([380, 150])
                if self.rightSplitter: self.rightSplitter.setSizes([300, 300])
            else:
                if self.mainSplitter: self.mainSplitter.setSizes([280, 720, 280])
                if self.runningEditorSplitter: self.runningEditorSplitter.setSizes([600, 200])
                if self.rightSplitter: self.rightSplitter.setSizes([400, 400])
                
        # Override minimum widths from .ui files to allow more aggressive shrinking
        # We use 100 instead of 0 to prevent "snapping" / total collapse which feels broken
        min_w = 100 if is_small else 200
        # Ensure splitters don't snap to zero
        if self.mainSplitter: self.mainSplitter.setChildrenCollapsible(False)
        if hasattr(self, 'leftSplitter') and self.leftSplitter: self.leftSplitter.setChildrenCollapsible(False)
        if self.runningEditorSplitter: self.runningEditorSplitter.setChildrenCollapsible(False)
        if self.rightSplitter: self.rightSplitter.setChildrenCollapsible(False)

        # Training Mode
        if hasattr(self, 'training_mode_widget') and self.training_mode_widget:
            for p_name in ["leftPanel", "rightPanel", "configPanel", "progressPanel"]:
                p = self.training_mode_widget.findChild(QFrame, p_name)
                if p: p.setMinimumWidth(min_w)
                
        # Running Mode
        if hasattr(self, 'running_mode_widget') and self.running_mode_widget:
            for p_name in ["hubContainer", "middlePanel", "monacoPlaceholder", "rightSplitter", "camContainer", "resContainer"]:
                p = self.running_mode_widget.findChild(QWidget, p_name)
                if p: p.setMinimumWidth(min_w)
        

        # 3. Refresh Dynamic Components
        if hasattr(self, '_cards_layout'):
            # Small delay to allow layout engine to settle before re-populating complex widgets
            QTimer.singleShot(100, self.populate_curriculum_hub)
        
        # Update Level Navigation badges for resolution
        if hasattr(self, '_level_badges'):
            for badge in self._level_badges.values():
                try:
                    badge.update_resolution(is_small)
                except RuntimeError:
                    pass  # Widget may have been deleted during layout transition
            # Resize the nav container bar
            if hasattr(self, '_nav_container') and self._nav_container:
                bar_h = 36 if is_small else 50
                bar_br = bar_h // 2
                self._nav_container.setFixedHeight(bar_h)
                self._nav_container.setStyleSheet(f"""
                    QFrame#levelNavBar {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(139, 92, 246, 0.35),
                            stop:0.4 rgba(109, 40, 217, 0.25),
                            stop:0.7 rgba(59, 130, 246, 0.25),
                            stop:1 rgba(6, 182, 212, 0.2));
                        border-radius: {bar_br}px;
                        border: 1.5px solid rgba(139, 92, 246, 0.3);
                    }}
                """)
        
        # Refresh Training charts if they exist
        if hasattr(self, '_charts') and self._charts:
            for chart in self._charts:
                if chart:
                    chart.set_small_mode(is_small)
                    # Scale chart frame height
                    parent_frame = chart.parent()
                    if parent_frame:
                        parent_frame.setMinimumHeight(160 if is_small else 300)
        
        # 4. Handle Training Mode scaling if possible
        if hasattr(self, 'training_mode_widget') and self.training_mode_widget:
            w = self.training_mode_widget
            
            # Panel Titles — all headers uniform
            t_size = 12 if is_small else 22
            t_pad = '2px 6px' if is_small else '6px 16px'
            _title_ss = f"font-weight: bold; font-size: {t_size}px; color: white; padding: {t_pad}; background: transparent;"
            for header_name in ["leftHeader", "configHeader", "progressHeader", "rightHeader"]:
                header = w.findChild(QFrame, header_name)
                if header:
                    # Use layout to get the direct first label — avoids duplicate objectName issues
                    lay = header.layout()
                    if lay and lay.count() > 0:
                        item = lay.itemAt(0)
                        if item and item.widget() and isinstance(item.widget(), QLabel):
                            item.widget().setStyleSheet(_title_ss)
            
            # Webcam / Upload / Label buttons and capture size toggles in Data Collection
            btn_font = 11 if is_small else 17
            btn_pad = 2 if is_small else 6
            btn_fw = "normal" if is_small else "600"
            btn_h = 24 if is_small else 34
            cap_font = 8 if is_small else 13
            for btn in w.findChildren(QPushButton):
                txt = btn.text()
                if "Webcam" in txt or "Upload" in txt or ("Label" in txt and "Save" not in txt and "Continue" not in txt):
                    import re as _re
                    ss = _re.sub(r"font-size:\s*\d+px", f"font-size: {btn_font}px", btn.styleSheet())
                    ss = _re.sub(r"padding:\s*\d+px", f"padding: {btn_pad}px", ss)
                    ss = _re.sub(r"font-weight:\s*\w+", f"font-weight: {btn_fw}", ss)
                    btn.setStyleSheet(ss)
                    if btn_h: btn.setFixedHeight(btn_h)
            _cap_pad = '1px 6px' if is_small else '3px 8px'
            _cap_h = 18 if is_small else 28
            for cap_name in ["btnCapSize320", "btnCapSize640"]:
                cap_btn = w.findChild(QPushButton, cap_name)
                if cap_btn:
                    _radius_l = "border-top-left-radius: 8px; border-bottom-left-radius: 8px; border-right: none;" if "320" in cap_name else ""
                    _radius_r = "border-top-right-radius: 8px; border-bottom-right-radius: 8px;" if "640" in cap_name else ""
                    cap_btn.setFixedHeight(_cap_h)
                    cap_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.2);
                            padding: {_cap_pad}; font-weight: bold; font-size: {cap_font}px; color: #cbd5e1;
                            {_radius_l}{_radius_r}
                        }}
                        QPushButton:hover:!checked {{ background: rgba(255, 255, 255, 0.25); }}
                        QPushButton:checked {{ background: white; color: #3b82f6; border-color: white; }}
                    """)

            # Recognition / Detection toggle buttons
            _tog_fs = 8 if is_small else 14 
            _tog_pad = '1px 2px' if is_small else '5px 13px'
            _tog_br = 4 if is_small else 8
            for _tog_name in ["btnRecognition", "btnDetection"]:
                _tog_btn = w.findChild(QPushButton, _tog_name)
                if _tog_btn:
                    _tog_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: rgba(255, 255, 255, 0.2); border: 1px solid rgba(255, 255, 255, 0.3);
                            border-radius: {_tog_br}px; padding: {_tog_pad}; font-weight: 800; color: #e0e7ff; font-size: {_tog_fs}px;
                        }}
                        QPushButton:hover:!checked {{ background: rgba(255, 255, 255, 0.3); }}
                        QPushButton:checked {{ background: white; color: #4338ca; border-color: white; }}
                    """)

            # Project name row — bigger for normal resolution
            _proj_h = 18 if is_small else 26
            _proj_fs = 10 if is_small else 16
            _proj_btn_fs = 10 if is_small else 14
            if hasattr(self, 'lblProjName') and self.lblProjName:
                self.lblProjName.setFixedHeight(_proj_h)
                self.lblProjName.setStyleSheet(f"#lblProjName {{ color: white; font-weight: bold; font-size: {_proj_fs}px; padding: 0; margin: 0; min-height: 0; max-height: {_proj_h}px; }}")
            if hasattr(self, 'editProjName') and self.editProjName and self.editProjName.isEnabled():
                self.editProjName.setFixedHeight(_proj_h)
                self.editProjName.setStyleSheet(f"""
                    #editProjName {{
                        background: rgba(255, 255, 255, 0.9); border: 1px solid #ef4444;
                        border-radius: 4px; padding: 0px 4px; font-size: {_proj_fs - 1}px;
                        min-height: 0px; max-height: {_proj_h}px;
                    }}
                """)
            if hasattr(self, 'btnProjCheck') and self.btnProjCheck:
                self.btnProjCheck.setFixedSize(_proj_h, _proj_h)
                self.btnProjCheck.setStyleSheet(f"""
                    #btnProjCheck {{
                        background: #10b981; color: white; border-radius: 4px; font-weight: bold; font-size: {_proj_btn_fs}px;
                        min-height: 0px; max-height: {_proj_h}px; padding: 0;
                    }}
                    #btnProjCheck:hover {{ background: #059669; }}
                    #btnProjCheck:disabled {{ background: #94a3b8; }}
                """)
            if hasattr(self, 'btnProjReload') and self.btnProjReload:
                _is_new = self.btnProjReload.text() == "New"
                _reload_w = (32 if is_small else 50) if _is_new else _proj_h
                self.btnProjReload.setFixedSize(_reload_w, _proj_h)
                if not self.btnProjReload.isEnabled() or _is_new:
                    self.btnProjReload.setStyleSheet(f"QPushButton {{ background: #64748b; color: white; border-radius: 6px; font-weight: bold; font-size: {_proj_btn_fs - 1}px; }} QPushButton:hover {{ background: #475569; }}")
                else:
                    self.btnProjReload.setStyleSheet(f"""
                        #btnProjReload {{
                            background: #f59e0b; color: white; border-radius: 4px; font-size: {_proj_btn_fs}px;
                            min-height: 0px; max-height: {_proj_h}px; padding: 0;
                        }}
                        #btnProjReload:hover {{ background: #d97706; }}
                        #btnProjReload:disabled {{ background: #94a3b8; }}
                    """)

            # Detection mode class card scaling (scroll area, thumbnails, badges, hints)
            if hasattr(self, '_class_data'):
                _badge_w = 48 if is_small else 68
                _badge_font = 10 if is_small else 16
                _hint_font = 10 if is_small else 16
                for info in self._class_data:
                    if info is None: continue
                    # Scroll area min height
                    scroll = info.get("scroll")
                    if scroll and scroll.minimumHeight() > 100:
                        scroll.setMinimumHeight(180 if is_small else 300)
                    # Hint label
                    hint = info.get("hint_lbl")
                    if hint:
                        hint.setStyleSheet(f"color: #94a3b8; font-size: {_hint_font}px; font-weight: 50; padding: 0; margin: 0;")
                    # Hint icon
                    hint_icon = info.get("hint_icon")
                    if hint_icon:
                        _ico_sz = 48 if is_small else 108
                        hint_icon.setStyleSheet(f"font-size: {_ico_sz}px; color: rgba(203, 213, 225, 0.4); padding: 0; margin: 0;")
                    # Hint container
                    hint_cont = info.get("hint_container")
                    if hint_cont and hint_cont.minimumHeight() > 80:
                        hint_cont.setMinimumHeight(100 if is_small else 240)
                    # Count badge
                    badge = info.get("count_badge")
                    if badge:
                        badge.setFixedWidth(_badge_w)
                        badge.setStyleSheet(f"background: #e2e8f0; color: #64748b; border-radius: 10px; padding: 2px 2px; font-size: {_badge_font}px; font-weight: bold;")
                    # Tag panel
                    tag_panel = info.get("tag_panel")
                    if tag_panel:
                        tag_panel.set_small_mode(is_small)

            # Form Labels and Inputs
            lbl_size = 8 if is_small else 17
            input_size = 8 if is_small else 17

            # Target specific label types via name or class
            all_labels = w.findChildren(QLabel)
            target_labels = ["lblBackbone", "lblEpochs", "lblBatch", "lblLR", "lblOpt", "lblImgSize"]
            static_labels = ["lblStaticBackbone", "lblStaticImgSize"]
            for lbl in all_labels:
                if lbl.objectName() in target_labels:
                    lbl.setStyleSheet(f"font-weight: bold; font-size: {lbl_size}px; color: #1e293b; background: transparent;")
                elif lbl.objectName() in static_labels:
                    _sl_fs = 8 if is_small else 15
                    _sl_pad = '1px' if is_small else '6px'
                    lbl.setStyleSheet(f"QLabel {{ font-weight: bold; color: #16a34a; background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 3px; padding: {_sl_pad}; font-size: {_sl_fs}px;}}")
                elif lbl.objectName() == "lblValueAccuracy" or lbl.objectName() == "lblValueLoss" or lbl.objectName() == "metricValue":
                    mv_size = 10 if is_small else 20
                    lbl.setStyleSheet(f"color: #0f172a; font-size: {mv_size}px; font-weight: bold; background: transparent;")
                elif lbl.objectName() == "metricTitle":
                    mt_size = 8 if is_small else 14
                    lbl.setStyleSheet(f"color: rgba(0,0,0,0.6); font-size: {mt_size}px; font-weight: bold; background: transparent;")

            # Epoch progress labels
            _ep_fs = 8 if is_small else 14
            _ep_prog = w.findChild(QLabel, "lblEpochProgTitle")
            if _ep_prog: _ep_prog.setStyleSheet(f"font-weight: 600; color: #475569; font-size: {_ep_fs}px;")
            _ep_cnt = w.findChild(QLabel, "lblEpochCounter")
            if _ep_cnt: _ep_cnt.setStyleSheet(f"font-family: 'Consolas'; color: #475569; font-size: {_ep_fs}px;")

            # Dataset card labels
            _ds_title = w.findChild(QLabel, "dsTitle")
            if _ds_title: _ds_title.setStyleSheet(f"font-weight: bold; color: #1e3a8a; font-size: {8 if is_small else 17}px;")
            _ds_hint = w.findChild(QLabel, "lblDsHint")
            if _ds_hint: _ds_hint.setStyleSheet(f"color: #3b82f6; font-size: {6 if is_small else 14}px; font-weight: normal;")
            _ds_count = w.findChild(QLabel, "lblImageCountLarge")
            if _ds_count: _ds_count.setStyleSheet(f"font-size: {12 if is_small else 28}px; font-weight: bold; color: #2563eb;")
            _ds_icon = w.findChild(QLabel, "dsIcon")
            if _ds_icon and is_small: _ds_icon.setStyleSheet(f"color: #1e40af; font-size: 8px;")

            # Status icon scaling
            _status_icon = w.findChild(QLabel, "statusIcon")
            if _status_icon:
                _ico_sz = 51 if is_small else 115
                _status_icon.setStyleSheet(f"font-size: {_ico_sz}px; color: rgba(203, 213, 225, 0.4);")
                from PyQt5.QtWidgets import QGraphicsOpacityEffect
                _op = QGraphicsOpacityEffect(_status_icon)
                _op.setOpacity(0.45)
                _status_icon.setGraphicsEffect(_op)

            # Input fields (skip widgets with their own custom styling)
            from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit
            _skip_inputs = {"editProjName", "classNameEdit"}
            for field in w.findChildren((QComboBox, QLineEdit)):
                if field.objectName() in _skip_inputs:
                    continue
                # Skip tag panel colored inputs (MultiClassTagPanel)
                _parent = field.parent()
                if _parent and _parent.objectName() == "MultiClassTagPanel":
                    continue
                _inp_pad = '1px' if is_small else '2px 10px'
                field.setStyleSheet(f"border: 1px solid #e2e8f0; border-radius: 3px; padding: {_inp_pad}; "
                                  f"background-color: #f8fafc; font-size: {input_size}px; color: #0f172a;")
            # SpinBoxes — fancy arrows for normal, .ui default for small
            for field in w.findChildren((QSpinBox, QDoubleSpinBox)):
                if is_small:
                    _obj = field.objectName() or "QSpinBox"
                    field.setStyleSheet(
                        f"#{_obj} {{ border: 1px solid #e2e8f0; border-radius: 3px; padding: 1px 4px; "
                        f"background-color: #f8fafc; font-size: 8px; color: #0f172a; min-height: 0px; }}"
                    )
                else:
                    _spin_h = 32
                    field.setMinimumHeight(0)
                    field.setMaximumHeight(_spin_h)
                    field.setFixedHeight(_spin_h)
                    _arrow_up, _arrow_down = self._get_spin_arrow_paths()
                    _obj = field.objectName() or "QSpinBox"
                    field.setStyleSheet(
                        f"#{_obj} {{ border: 1px solid #e2e8f0; border-radius: 6px; padding: 0px 10px; "
                        f"background-color: #f8fafc; font-size: 17px; color: #0f172a; min-height: 0px; max-height: {_spin_h}px; }}\n"
                        f"#{_obj}::up-button {{ subcontrol-origin: border; subcontrol-position: top right; width: 20px; background: #e2e8f0; border-left: 1px solid #cbd5e1; border-top-right-radius: 6px; }}\n"
                        f"#{_obj}::down-button {{ subcontrol-origin: border; subcontrol-position: bottom right; width: 20px; background: #e2e8f0; border-left: 1px solid #cbd5e1; border-bottom-right-radius: 6px; }}\n"
                        f"#{_obj}::up-button:hover {{ background: #cbd5e1; }}\n"
                        f"#{_obj}::down-button:hover {{ background: #cbd5e1; }}\n"
                        f"#{_obj}::up-arrow {{ image: url({_arrow_up}); width: 8px; height: 8px; }}\n"
                        f"#{_obj}::down-arrow {{ image: url({_arrow_down}); width: 8px; height: 8px; }}"
                    )

            # Config scroll area margins
            config_scroll = w.findChild(QWidget, "configContent")
            if config_scroll and config_scroll.layout():
                _cm = 3 if is_small else 20
                config_scroll.layout().setContentsMargins(_cm, _cm, _cm, 0)
                config_scroll.layout().setSpacing(3 if is_small else 10)

            # Training Log
            if hasattr(self, 'txtTrainLog') and self.txtTrainLog:
                log_font = 5 if is_small else 10
                self.txtTrainLog.setMaximumHeight(30 if is_small else 120)
                self.txtTrainLog.setStyleSheet(f"background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; \n"
                                             f"font-family: 'Consolas'; font-size: {log_font}px; padding: 2px; border-radius: 0 0 3px 3px;")

            # Action Buttons
            btn_add_size = 4 if is_small else 16
            btn_start_size = 8 if is_small else 16
            btn_add = w.findChild(QPushButton, "btnAddClass")
            if btn_add:
                btn_add.setStyleSheet(f"border: 2px dashed #cbd5e1; background: #f8fafc; color: #64748b; "
                                     f"border-radius: 4px; padding: {'1px' if is_small else '12px'}; font-weight: bold; margin: 1px; font-size: {btn_add_size}px;")
            btn_start = w.findChild(QPushButton, "btnStartTraining")
            if btn_start:
                btn_start.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #16a34a, stop:1 #059669); "
                                       f"color: white; border-radius: 4px; font-weight: bold; border: none; "
                                       f"min-height: {'18px' if is_small else '36px'}; font-size: {btn_start_size}px; margin: {'1px' if is_small else '8px'};")

            # Validation buttons
            if hasattr(self, 'btnStopValidation') and self.btnStopValidation:
                _vb_fs = 8 if is_small else 14
                _vb_h = 16 if is_small else 36
                self.btnStopValidation.setFixedHeight(_vb_h)
                import re as _re
                _ss = _re.sub(r"font-size:\s*\d+px", f"font-size: {_vb_fs}px", self.btnStopValidation.styleSheet())
                self.btnStopValidation.setStyleSheet(_ss)
            if hasattr(self, 'btnSaveModel') and self.btnSaveModel:
                _vb_fs = 8 if is_small else 14
                _vb_h = 16 if is_small else 36
                self.btnSaveModel.setFixedHeight(_vb_h)
                import re as _re
                _ss = _re.sub(r"font-size:\s*\d+px", f"font-size: {_vb_fs}px", self.btnSaveModel.styleSheet())
                self.btnSaveModel.setStyleSheet(_ss)

            # Status messages
            msg_size = 7 if is_small else 15
            hint_size = 6 if is_small else 14
            status_msg = w.findChild(QLabel, "statusMsg")
            if status_msg: status_msg.setStyleSheet(f"font-weight: bold; font-size: {msg_size}px; color: #94a3b8;")
            status_hint = w.findChild(QLabel, "statusHint")
            if status_hint: status_hint.setStyleSheet(f"color: #94a3b8; font-size: {hint_size}px; padding: 0 10px;")

            # BBox editor panel elements — built with is_small_screen=True default, must rescale
            if hasattr(self, '_bbox_panel'):
                _bt_fs = 8 if is_small else 16
                _bh_fs = 7 if is_small else 13
                _bcls_sz = 20 if is_small else 32
                _bcls_fs = 11 if is_small else 18
                _bnav_sz = 18 if is_small else 34
                _bnav_fs = 8 if is_small else 16
                _bsave_fs = 8 if is_small else 14
                _bsave_pad = '3px 8px' if is_small else '8px 20px'
                _bsave_min = 60 if is_small else 140
                _bsave_br = 4 if is_small else 6
                _bprog_fs = 7 if is_small else 13
                _bsc_fs = 6 if is_small else 10
                _bcam_fs = 7 if is_small else 14

                # Title
                _bt = self._bbox_panel.findChild(QLabel, "bboxTitle")
                if _bt:
                    _bt.setStyleSheet(f"color: white; font-weight: bold; font-size: {_bt_fs}px;")
                # Hint
                if hasattr(self, '_bbox_hint'):
                    self._bbox_hint.setStyleSheet(f"color: #94a3b8; font-size: {_bh_fs}px;")
                # Close button
                for btn in self._bbox_panel.findChildren(QPushButton):
                    if btn.text() == "✕":
                        btn.setFixedSize(_bcls_sz, _bcls_sz)
                        btn.setStyleSheet(f"QPushButton {{ background: transparent; color: #64748b; border: none; font-size: {_bcls_fs}px; border-radius: {_bcls_sz // 2}px; }} QPushButton:hover {{ color: #f87171; background: rgba(248,113,113,0.1); }}")
                # Nav buttons
                if hasattr(self, '_btn_prev_annotation'):
                    self._btn_prev_annotation.setFixedSize(_bnav_sz, _bnav_sz)
                    self._btn_prev_annotation.setStyleSheet(f"""
                        QPushButton {{ background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: {_bnav_sz // 2}px; font-weight: bold; font-size: {_bnav_fs}px; }}
                        QPushButton:hover {{ background: #334155; border-color: #8b5cf6; color: white; }}
                        QPushButton:disabled {{ color: #334155; border-color: #1e293b; }}
                    """)
                if hasattr(self, '_btn_next_annotation'):
                    self._btn_next_annotation.setFixedSize(_bnav_sz, _bnav_sz)
                    self._btn_next_annotation.setStyleSheet(f"""
                        QPushButton {{ background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: {_bnav_sz // 2}px; font-weight: bold; font-size: {_bnav_fs}px; }}
                        QPushButton:hover {{ background: #334155; border-color: #8b5cf6; color: white; }}
                        QPushButton:disabled {{ color: #334155; border-color: #1e293b; }}
                    """)
                # Save button
                if hasattr(self, '_bbox_save_btn'):
                    self._bbox_save_btn.setStyleSheet(f"""
                        QPushButton {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6);
                                     color: white; border: none; border-radius: {_bsave_br}px;
                                     font-weight: bold; font-size: {_bsave_fs}px; padding: {_bsave_pad}; min-width: {_bsave_min}px; }}
                        QPushButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6d28d9, stop:1 #7c3aed); }}
                    """)
                # Camera shutter
                if hasattr(self, '_cam_shutter_btn'):
                    _cam_pad = '3px 8px' if is_small else '10px 32px'
                    _cam_min = 50 if is_small else 120
                    self._cam_shutter_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: white; color: #1e293b; border: 4px solid #94a3b8;
                            border-radius: 20px; font-weight: bold; font-size: {_bcam_fs}px;
                            padding: {_cam_pad}; min-width: {_cam_min}px;
                        }}
                        QPushButton:hover {{ background: #f0f9ff; border-color: #3b82f6; color: #1d4ed8; }}
                    """)
                # Progress label
                if hasattr(self, '_lbl_batch_progress'):
                    self._lbl_batch_progress.setStyleSheet(f"color: #94a3b8; font-size: {_bprog_fs}px; font-weight: bold;")
                # Floating capture frame button
                if hasattr(self, '_tr_shutter_btn'):
                    _sh_w = 90 if is_small else 135
                    _sh_h = 24 if is_small else 36
                    _sh_fs = 8 if is_small else 12
                    self._tr_shutter_btn.setFixedSize(_sh_w, _sh_h)
                    self._tr_shutter_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: #3b82f6; color: white; border: 2px solid white;
                            border-radius: {_sh_h // 2}px; font-weight: bold; font-size: {_sh_fs}px;
                        }}
                        QPushButton:hover {{ background: #2563eb; }}
                    """)
                # Drag handle
                if hasattr(self, '_bbox_drag_handle'):
                    self._bbox_drag_handle.setFixedHeight(12 if is_small else 20)
                # Panel min height
                if is_small:
                    self._bbox_panel.setFixedHeight(200)
                else:
                    self._bbox_panel.setMinimumHeight(450)
                    self._bbox_panel.setMaximumHeight(16777215)

        # 5. Handle Running Mode scaling if possible
        if hasattr(self, 'running_mode_widget') and self.running_mode_widget:
            rw = self.running_mode_widget
            title_size = 12 if is_small else 20
            _t_fw = "bold"

            # Panel headers — use #id selector to override .ui global stylesheet
            for t_name in ["hubTitle", "editorTitle", "camTitle", "resTitle"]:
                t_lbl = rw.findChild(QLabel, t_name)
                if t_lbl:
                    t_lbl.setStyleSheet(f"#{t_name} {{ font-weight: {_t_fw}; font-size: {title_size}px; color: white; background: transparent; padding: 1px 4px; }}")

            # Console titles (slightly smaller)
            console_title_size = title_size - 2
            for t_name in ["lblCT", "lblCCT"]:
                t_lbl = rw.findChild(QLabel, t_name)
                if t_lbl:
                    t_lbl.setStyleSheet(f"#{t_name} {{ font-weight: {_t_fw}; font-size: {console_title_size}px; color: white; background: transparent; padding: 1px 4px; }}")

            # Hub header height/padding — shrink for small screen
            hubHeader = rw.findChild(QFrame, "hubHeader")
            if hubHeader:
                _hh_pad = '2px 0px' if is_small else '8px 0px'
                hubHeader.setStyleSheet(f"QFrame#hubHeader {{ background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #2563eb); border: none; padding: {_hh_pad}; }}")

            # Hub tab buttons scaling — use unified frosted bubble style
            if hasattr(self, 'hubStackedWidget') and self.hubStackedWidget:
                active_idx = self.hubStackedWidget.currentIndex()
                self._update_hub_tab_styles(active_idx)

            # Console Body
            if hasattr(self, 'consoleBody') and self.consoleBody:
                c_font = 8 if is_small else 14
                self.consoleBody.setStyleSheet(f"background-color: transparent; color: #334155; font-family: 'Consolas', 'Courier New'; font-size: {c_font}px;")

            # Console Header and buttons scaling
            console_header = rw.findChild(QFrame, "consoleHeader")
            if console_header:
                console_header.setFixedHeight(36 if is_small else 44)
            collapsed_bar = rw.findChild(QFrame, "collapsedConsoleBar")
            if collapsed_bar:
                collapsed_bar.setFixedHeight(34 if is_small else 40)
            btn_clear = rw.findChild(QPushButton, "btnClearConsole")
            if btn_clear:
                _cc_fs = 8 if is_small else 16
                btn_clear.setStyleSheet(f"QPushButton {{ color: #d0d8e5; background: transparent; border: none; font-family: 'Consolas', monospace; font-size: {_cc_fs}px;}} QPushButton:hover {{ color: white; background: rgba(255,255,255,0.1); border-radius: 4px; }}")
            btn_collapse = rw.findChild(QPushButton, "btnCollapseConsole")
            if btn_collapse:
                _bc_fs = 9 if is_small else 18
                btn_collapse.setStyleSheet(f"QPushButton {{ color: #d0d8e5; background: transparent; border: none; font-family: 'Consolas', monospace; font-size: {_bc_fs}px;}} QPushButton:hover {{ color: white; background: rgba(255,255,255,0.1); border-radius: 4px; }}")

            # Footer labels scaling
            _ft_fs = 11 if is_small else 14
            for _ft_name in ["lblStatus", "lblTimestamp"]:
                _ft_lbl = rw.findChild(QLabel, _ft_name)
                if _ft_lbl:
                    _ft_lbl.setStyleSheet(f"color: #94a3b8; font-size: {_ft_fs}px;")
            _var_lbl = rw.findChild(QLabel, "lblVarCount")
            if _var_lbl:
                _var_lbl.setStyleSheet(f"color: white; background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 8px; font-size: {_ft_fs}px;")

            # Monaco Placeholder (for now it's a QTextEdit)
            if hasattr(self, 'monacoPlaceholder') and self.monacoPlaceholder:
                e_font = 8 if is_small else 17
                self.monacoPlaceholder.setStyleSheet(f"background-color: white; border: none; font-family: 'Consolas', 'Courier New'; font-size: {e_font}px; color: #1e293b;")
                # Scale QScintilla font directly (stylesheet doesn't affect Scintilla rendering)
                from PyQt5.QtGui import QFont as _QFont
                _ef = _QFont("Consolas", 8 if is_small else 11)
                if hasattr(self.monacoPlaceholder, 'lexer') and self.monacoPlaceholder.lexer:
                    self.monacoPlaceholder.lexer.setDefaultFont(_ef)
                    for i in range(128):
                        self.monacoPlaceholder.setMarginsFont(_ef)
                        self.monacoPlaceholder.setMarginWidth(0, "000" if is_small else "0000")
                        self.monacoPlaceholder.lexer.setFont(_ef, i)

            # Footer Workspace Label
            if hasattr(self, 'lblCurrentFolder') and self.lblCurrentFolder:
                wf_size = 10 if is_small else 15
                self.lblCurrentFolder.setStyleSheet(f"font-weight: bold; color: #475569; font-size: {wf_size}px;")

            # Refresh Function Library with scaling
            from src.modules.function_library import populate_functions_tab
            populate_functions_tab(self.running_mode_widget, is_small=is_small, lang=self.current_lang)

            # Workspace Dashboard Scaling
            if hasattr(self, 'workspaceDashboard') and self.workspaceDashboard:
                d = self.workspaceDashboard
                card_title_font = 6 if is_small else 9
                card_count_font = 8 if is_small else 20
                for card_name, color in [("cardCode", "#2563eb"), ("cardData", "#16a34a"), ("cardModel", "#9333ea")]:
                    card = d.findChild(QFrame, card_name)
                    if card:
                        # Scale cards height
                        card.setMinimumHeight(50 if is_small else 100)
                        card.setMaximumHeight(70 if is_small else 130)
                        for lbl in card.findChildren(QLabel):
                            if lbl.objectName().startswith("count"):
                                lbl.setStyleSheet(f"font-size: {card_count_font}px; font-weight: bold; color: {color}; background: transparent;")
                            elif lbl.text() in ("📄", "🖼️", "💻"):
                                pass  # Skip icon labels
                            else:
                                lbl.setWordWrap(True)
                                lbl.setStyleSheet(f"font-size: {card_title_font}px; font-weight: bold; color: {color}; background: transparent;")

            # Editor Tab Bar scaling (Minimal)
            editorTabBar = rw.findChild(QFrame, "editorTabBar")
            if editorTabBar:
                editorTabBar.setFixedHeight(20 if is_small else 30)
                
            tabContainer = rw.findChild(QWidget, "tabContainer")
            if tabContainer:
                if tabContainer.layout():
                    tabContainer.layout().setContentsMargins(0, 0, 0, 0)
                    tabContainer.layout().setSpacing(1 if is_small else 4)
                
                # Scale individual tab items (file buttons)
                # Height increased to 26px to prevent clipping of 'p' and other descenders
                _et_fs = 6 if is_small else 8
                _et_h = 14 if is_small else 20
                for child_btn in tabContainer.findChildren(QPushButton):
                    child_btn.setFixedHeight(_et_h)
                    child_btn.setFont(QFont("Segoe UI", _et_fs, QFont.Weight.Bold))
            # Editor header padding
            editorHeader = rw.findChild(QFrame, "editorHeader")
            if editorHeader and editorHeader.layout():
                editorHeader.layout().setContentsMargins(6 if is_small else 10, 2 if is_small else 6, 6 if is_small else 10, 2 if is_small else 6)

            if hasattr(self, 'btnRunCode') and self.btnRunCode:
                r_size = 10 if is_small else 14
                self.btnRunCode.setFixedHeight(30 if is_small else 40)
                self.btnRunCode.setStyleSheet(f"background-color: #12b54d; color: white; border-radius: 4px; font-size: {r_size}px; font-weight: bold; padding: {'3px 6px' if is_small else '6px 15px'};")
            if hasattr(self, 'btnSaveFile') and self.btnSaveFile:
                s_size = 10 if is_small else 14
                self.btnSaveFile.setFixedHeight(30 if is_small else 40)
                self.btnSaveFile.setStyleSheet(f"background-color: rgba(255,255,255,0.15); color: white; border-radius: 4px; padding: {'3px 6px' if is_small else '4px 10px'}; font-weight: bold; font-size: {s_size}px;")

            # Camera Start button scaling
            if hasattr(self, 'btnStartCamHeader') and self.btnStartCamHeader:
                _cam_fs = 9 if is_small else 14
                _cam_h = 20 if is_small else 32
                self.btnStartCamHeader.setFixedHeight(_cam_h)
                self.btnStartCamHeader.setStyleSheet(f"QPushButton#btnStartCamHeader {{ background-color: #22c55e; color: white; border-radius: 4px; font-weight: bold; padding: 2px 8px; font-size: {_cam_fs}px; }} QPushButton#btnStartCamHeader:hover {{ background-color: #16a34a; }}")

            # Assistant Bot Button Scaling
            if hasattr(self, 'btnAssistantBot') and self.btnAssistantBot:
                btn_size = 48 if is_small else 56
                self.btnAssistantBot.setFixedSize(btn_size, btn_size)
                self._apply_assistant_bot_style(btn_size)
                QTimer.singleShot(50, self._reposition_assistant_bot)

            # Chat panel scaling
            if hasattr(self, '_chat_panel') and self._chat_panel:
                self._chat_panel.set_small_mode(is_small)
                QTimer.singleShot(60, self._reposition_chat_panel)

    def retranslate_ui(self):
        """Update all core UI strings from the translation dictionary."""
        s = STRINGS[self.current_lang]
        
        # main_window.ui elements
        if hasattr(self, 'appSubtitle'): self.appSubtitle.setText(s["APP_SUBTITLE"])
        if hasattr(self, 'btnRunMode'): self.btnRunMode.setText(s["MODE_RUNNING"])
        if hasattr(self, 'btnTrainMode'): self.btnTrainMode.setText(s["MODE_TRAINING"])
        if hasattr(self, 'footerHints'): self.footerHints.setText(s["FOOTER_HINTS"])
        if hasattr(self, 'footerCredit'): self.footerCredit.setText(s["FOOTER_CREDIT"])
        if hasattr(self, 'btnResToggle') and self.btnResToggle: self.btnResToggle.setToolTip(s["TIP_RES_TOGGLE"])

        # AI Assistant chat panel
        if hasattr(self, '_chat_panel') and self._chat_panel:
            self._chat_panel.retranslate(s)
        
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

        # Workspace card titles (Code / Data / Model)
        _card_label_map = {
            "cardCode": ("Code", s.get("CODE", "Code")),
            "cardData": ("Data", s.get("DATA", "Data")),
            "cardModel": ("Model", s.get("MODEL", "Model")),
        }
        for card_name, (fallback, translated) in _card_label_map.items():
            card = getattr(self, card_name, None)
            if card:
                for lbl in card.findChildren(QLabel):
                    txt = lbl.text()
                    if txt in ("Code", "Data", "Model", "Thư mục Code", "Dữ liệu", "Mô hình"):
                        lbl.setText(translated)
                        break
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
                i_f_size = 10 if self.is_small_screen else 12
                icon_lbl.setFont(QFont("Segoe UI", i_f_size))
                icon_lbl.setFixedWidth(20 if self.is_small_screen else 24)
                icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                icon_lbl.setStyleSheet(f"color: {theme['text']}; background: transparent;")
                
                name_lbl = QLabel(file_path.name)
                n_f_size = 10 if self.is_small_screen else 13
                name_lbl.setStyleSheet(f"color: {theme['text']}; font-weight: bold; font-size: {n_f_size}px; background: transparent;")
                
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
        rel_path = f"'projects/{folder_name}/{path.name}'"

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
    def _switch_hub_tab(self, index):
        """Switch hub tab and update button styles — active gets frosted white bubble."""
        if self.hubStackedWidget:
            self.hubStackedWidget.setCurrentIndex(index)
        self._update_hub_tab_styles(index)

    def _update_hub_tab_styles(self, active_index=0):
        """Apply frosted bubble style to active hub tab, gradient to inactive."""
        is_small = self.is_small_screen
        fs = 8 if is_small else 14
        pad = '3px 8px' if is_small else '6px 16px'
        br = 4 if is_small else 14

        tabs = [
            (0, self.tabExamples),
            (1, self.tabFunctions),
            (2, self.tabWorkspace),
        ]
        for idx, btn in tabs:
            if not btn:
                continue
            if idx == active_index:
                # Active — frosted white bubble (matches level nav active style)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: rgba(255, 255, 255, 0.92);
                        color: #6d28d9;
                        border-radius: {br}px;
                        font-weight: bold;
                        font-size: {fs}px;
                        padding: {pad};
                        border: 2px solid rgba(255, 255, 255, 0.7);
                    }}
                """)
            else:
                # Inactive — transparent with white text on the purple header
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: rgba(255, 255, 255, 0.15);
                        color: rgba(255, 255, 255, 0.85);
                        border-radius: {br}px;
                        font-weight: bold;
                        font-size: {fs}px;
                        padding: {pad};
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }}
                    QPushButton:hover {{
                        background: rgba(255, 255, 255, 0.3);
                        color: white;
                    }}
                """)

    def _setup_level_navigation(self):
        """Replace flat hubContentLayout with Level_Navigation_Bar + QScrollArea."""
        if not self.hubStackedWidget:
            return
        
        page = self.hubStackedWidget.widget(0)  # pageExamples
        if not page:
            return

        # Remove existing layout if any
        old_layout = page.layout()
        if old_layout:
            while old_layout.count():
                child = old_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            QWidget().setLayout(old_layout)  # Orphan old layout

        # New main layout
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(4, 4, 4, 0)
        main_layout.setSpacing(6)

        # ── Frosted pill container bar (like the reference designs) ──
        is_small = self.is_small_screen
        bar_h = 36 if is_small else 50
        bar_br = bar_h // 2

        nav_container = QFrame()
        nav_container.setObjectName("levelNavBar")
        nav_container.setFixedHeight(bar_h)
        nav_container.setStyleSheet(f"""
            QFrame#levelNavBar {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139, 92, 246, 0.35),
                    stop:0.4 rgba(109, 40, 217, 0.25),
                    stop:0.7 rgba(59, 130, 246, 0.25),
                    stop:1 rgba(6, 182, 212, 0.2));
                border-radius: {bar_br}px;
                border: 1.5px solid rgba(139, 92, 246, 0.3);
            }}
        """)

        nav_bar = QHBoxLayout(nav_container)
        nav_bar.setContentsMargins(8, 4, 8, 4)
        nav_bar.setSpacing(12 if is_small else 20)
        nav_bar.setAlignment(Qt.AlignCenter)

        self._level_badges = {}
        self._active_level = "Beginner"
        self._curriculum_cards = []
        self._nav_container = nav_container

        s = STRINGS[self.current_lang]
        for level_key, cfg in LEVEL_CONFIG.items():
            badge = LevelBadge(level_key, cfg["color"], cfg["icon"], is_small=is_small)
            badge.retranslate(s)
            badge.level_clicked.connect(self._on_level_selected)
            self._level_badges[level_key] = badge
            nav_bar.addWidget(badge)

        main_layout.addWidget(nav_container, 0, Qt.AlignCenter)

        # Scroll Area
        self._examples_scroll = QScrollArea()
        self._examples_scroll.setWidgetResizable(True)
        self._examples_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._examples_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._examples_scroll.setFrameShape(QFrame.NoFrame)
        self._examples_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QScrollArea > QWidget > QWidget { background: transparent; }")

        scroll_contents = QWidget()
        scroll_contents.setStyleSheet("background: transparent;")
        scroll_contents.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._cards_layout = QVBoxLayout(scroll_contents)
        self._cards_layout.setContentsMargins(4, 0, 4, 0)
        self._cards_layout.setSpacing(6)
        self._cards_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)
        self._examples_scroll.setWidget(scroll_contents)

        main_layout.addWidget(self._examples_scroll)

        # Set Beginner active
        self._level_badges["Beginner"].set_active(True)

    def populate_curriculum_hub(self):
        """Scan curriculum folder, group by level, create cards, apply active filter."""
        if not hasattr(self, '_cards_layout'):
            return

        # 1. Clear existing cards
        self._curriculum_cards = []
        while self._cards_layout.count():
            child = self._cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 2. Scan curriculum directory
        curr_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "curriculum")
        if not os.path.exists(curr_dir):
            return

        counts = {"Beginner": 0, "Intermediate": 0, "Advanced": 0}

        for name in sorted(os.listdir(curr_dir)):
            if name.endswith(".py"):
                file_path = os.path.join(curr_dir, name)
                metadata = self._parse_lesson_metadata(file_path)

                title = metadata.get(f"TITLE_{self.current_lang.upper()}", metadata.get("TITLE", name))
                desc = metadata.get(f"DESC_{self.current_lang.upper()}", metadata.get("DESC", "Custom curriculum script."))
                level = metadata.get("LEVEL", "Beginner")

                card = CurriculumCard(
                    filename=name,
                    title=title,
                    level=level,
                    icon=metadata.get("ICON", "📄"),
                    color=metadata.get("COLOR", "#7c3aed"),
                    desc=desc,
                    on_load_click=self.load_curriculum_example,
                    is_small=self.is_small_screen
                )
                self._curriculum_cards.append((level, card))
                self._cards_layout.addWidget(card)

                if level in counts:
                    counts[level] += 1

        # Add spacer
        self._cards_layout.addStretch()

        # Update badge counts
        if hasattr(self, '_level_badges'):
            for lvl, badge in self._level_badges.items():
                badge.set_count(counts.get(lvl, 0))

        # Apply filter
        self._apply_level_filter()

    def _on_level_selected(self, level):
        """Handle level badge click."""
        if level == self._active_level:
            return
        self._active_level = level
        for lvl, badge in self._level_badges.items():
            badge.set_active(lvl == level)
        self._apply_level_filter()
        # Scroll to top
        if hasattr(self, '_examples_scroll'):
            self._examples_scroll.verticalScrollBar().setValue(0)

    def _apply_level_filter(self):
        """Show/hide cards based on active level."""
        for level, card in self._curriculum_cards:
            card.setVisible(level == self._active_level)

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
        self._show_new_file_dialog(source="workspace")

    def _show_new_file_dialog(self, source="workspace"):
        """Show a dialog with filename input and template radio buttons."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QDialogButtonBox, QButtonGroup, QFrame
        
        s = STRINGS[self.current_lang]
        is_small = self.is_small_screen

        dlg = QDialog(self)
        dlg.setWindowTitle(s.get("DLG_NEW_FILE_TITLE", "Create New File"))
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dlg.setMinimumWidth(280 if is_small else 380)
        dlg.setStyleSheet("""
            QDialog { background: #1e1e2f; }
            QLabel { color: #e2e8f0; font-size: 13px; background: transparent; }
            QLineEdit { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px 10px; font-size: 13px; color: #0f172a; }
            QLineEdit:focus { border: 1px solid #7c3aed; }
            QRadioButton { color: #e2e8f0; font-size: 12px; spacing: 6px; background: transparent; }
            QRadioButton::indicator { width: 14px; height: 14px; }
            QFrame#tmplFrame { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; }
        """)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        # Filename input
        lbl_name = QLabel(s.get("DLG_NEW_FILE_NAME", "Filename (without .py):"))
        edit_name = QLineEdit()
        edit_name.setPlaceholderText("my_script")
        layout.addWidget(lbl_name)
        layout.addWidget(edit_name)

        # Template selection
        lbl_tmpl = QLabel(s.get("DLG_NEW_FILE_TMPL", "Template:"))
        layout.addWidget(lbl_tmpl)

        tmpl_frame = QFrame()
        tmpl_frame.setObjectName("tmplFrame")
        tmpl_layout = QVBoxLayout(tmpl_frame)
        tmpl_layout.setContentsMargins(12, 8, 12, 8)
        tmpl_layout.setSpacing(6)

        rb_instructive = QRadioButton(s.get("DLG_TMPL_INSTRUCTIVE", "📘 Instructive — full guided template with comments"))
        rb_blank = QRadioButton(s.get("DLG_TMPL_BLANK", "📄 Blank — minimal setup + loop skeleton"))
        rb_instructive.setChecked(True)

        tmpl_group = QButtonGroup(dlg)
        tmpl_group.addButton(rb_instructive, 0)
        tmpl_group.addButton(rb_blank, 1)

        tmpl_layout.addWidget(rb_instructive)
        tmpl_layout.addWidget(rb_blank)
        layout.addWidget(tmpl_frame)

        # OK / Cancel
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.setStyleSheet("""
            QPushButton { background: #7c3aed; color: white; border-radius: 6px; padding: 6px 18px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background: #6d28d9; }
        """)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addWidget(btn_box)

        if dlg.exec_() != QDialog.Accepted:
            return

        filename = edit_name.text().strip()
        if not filename:
            return

        use_blank = tmpl_group.checkedId() == 1
        content = self._get_blank_template() if use_blank else None  # None = default instructive

        result = self.file_manager.create_file(filename, content=content, folder='Code')
        if result['success']:
            full_name = filename if filename.endswith('.py') else filename + '.py'
            self.add_tab(full_name)
            if source == "tab":
                self.load_file_by_tab(full_name)
            self.log_to_console(f"File created: {result['path']}")
        else:
            self.log_to_console(f"Error: {result['message']}", True)

    def _get_blank_template(self):
        return (
            "# ============================================================\n"
            "# Setup section\n"
            "# ============================================================\n"
            "\n"
            "\n"
            "while True:\n"
            "    # ========================================================\n"
            "    # Main Loop section\n"
            "    # ========================================================\n"
            "    \n"
            "\n"
        )

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
        # Match the sizes from refresh_ui_resolution
        _tab_fs = 6 if self.is_small_screen else 8
        _tab_h = 14 if self.is_small_screen else 20
        btn_title.setFont(QFont("Segoe UI", _tab_fs, QFont.Weight.Bold))
        btn_title.setFixedHeight(_tab_h)
        btn_title.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_title.clicked.connect(lambda _, n=filename: self.load_file_by_tab(n))
        
        # Close Button
        btn_close = QPushButton("×")
        btn_close.setObjectName("TabClose")
        _close_sz = 6 if self.is_small_screen else 18
        btn_close.setFixedSize(_close_sz, _close_sz)
        btn_close.setFixedHeight(_tab_h)
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
        self._show_new_file_dialog(source="tab")
                

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
        update_results_panel(self, var_list, is_small=self.is_small_screen)
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
            # If the line is empty, replace it with the snippet and keep the newline
            self.monacoPlaceholder.setSelection(line, 0, line, len(self.monacoPlaceholder.text(line)))
            self.monacoPlaceholder.replaceSelectedText(snippet_formatted + "\n")
            
        self.log_to_console(STRINGS[self.current_lang]["HINT_INJECTED"].format(function_id))
            
    # --- New Drop Event Handlers ---

    def switch_mode(self, index):
        """Toggle between Running Mode (0) and Training Mode (1)."""
        self.mainStack.setCurrentIndex(index)
        if index == 1:
            self.setup_training_mode_logic()
            # Free LLM memory when entering Training Mode (YOLO needs the RAM)
            if hasattr(self, '_llm_assistant'):
                self._llm_assistant.unload()
            if hasattr(self, '_chat_panel'):
                self._chat_panel.hide()

    def setup_training_mode_logic(self):
        """Configure all signals for the Training Mode UI."""
        if hasattr(self, '_training_init_done'): return
        
        # Mode state
        self._training_task = "detection"  # 'recognition' or 'detection'
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
        self._convert_process = None
        self._training_is_running = False
        self._last_exported_engine = None
        self._last_exported_onnx = None
        self._selected_backbone = "yolov8n.pt"
        self._train_dot_count = 0
        self._train_dot_timer = QTimer(self)
        self._train_dot_timer.setInterval(500)
        self._train_dot_timer.timeout.connect(self._animate_training_dots)
        self._convert_dot_count = 0
        self._convert_dot_timer = QTimer(self)
        self._convert_dot_timer.setInterval(400)
        self._convert_dot_timer.timeout.connect(self._animate_convert_dots)

        
        # Wire Recognition / Detection toggle (Group 1 - Task)
        from PyQt5.QtWidgets import QButtonGroup
        self.task_group = QButtonGroup(self)
        btnRec = self.training_mode_widget.findChild(QPushButton, "btnRecognition")
        btnDet = self.training_mode_widget.findChild(QPushButton, "btnDetection")
        
        if btnRec and btnDet:
            self.task_group.addButton(btnRec)
            self.task_group.addButton(btnDet)
            self.task_group.setExclusive(True)

            # Hide Recognition button — only Detection mode is available
            btnRec.setVisible(False)
            btnDet.setChecked(True)

            btnRec.clicked.connect(lambda: self._set_task_type("recognition"))
            btnDet.clicked.connect(lambda: self._set_task_type("detection"))

        # ─── 🏗️ PROJECT NAME SECTION (New) ───
        lhLayout = self.training_mode_widget.findChild(QVBoxLayout, "lhLayout")
        if lhLayout:
            # Create Project Name Row (bare layout, same as tLayout/sizeLayout in .ui)
            self.projLayout = QHBoxLayout()
            self.projLayout.setContentsMargins(0, 0, 0, 0)
            self.projLayout.setSpacing(4)

            self.lblProjName = QLabel("Project name:")
            self.lblProjName.setObjectName("lblProjName")
            self.lblProjName.setStyleSheet("#lblProjName { color: white; font-weight: bold; font-size: 12px; padding: 0; margin: 0; min-height: 0; max-height: 20px; }")
            self.lblProjName.setFixedHeight(20)
            lblProj = self.lblProjName

            self.editProjName = QLineEdit()
            self.editProjName.setObjectName("editProjName")
            self.editProjName.setPlaceholderText("Enter name...")
            self.editProjName.setFixedHeight(20)
            self.editProjName.setStyleSheet("""
                #editProjName {
                    background: rgba(255, 255, 255, 0.9); border: 1px solid #ef4444;
                    border-radius: 4px; padding: 0px 4px; font-size: 11px;
                    min-height: 0px; max-height: 20px;
                }
            """)

            self.btnProjCheck = QPushButton("✓")
            self.btnProjCheck.setObjectName("btnProjCheck")
            self.btnProjCheck.setFixedSize(20, 20)
            self.btnProjCheck.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btnProjCheck.setStyleSheet("""
                #btnProjCheck {
                    background: #10b981; color: white; border-radius: 4px; font-weight: bold; font-size: 12px;
                    min-height: 0px; max-height: 20px; padding: 0;
                }
                #btnProjCheck:hover { background: #059669; }
                #btnProjCheck:disabled { background: #94a3b8; }
            """)

            self.btnProjReload = QPushButton("📂")
            self.btnProjReload.setObjectName("btnProjReload")
            self.btnProjReload.setFixedSize(20, 20)
            self.btnProjReload.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btnProjReload.setToolTip("Reload existing project")
            self.btnProjReload.setStyleSheet("""
                #btnProjReload {
                    background: #f59e0b; color: white; border-radius: 4px; font-size: 12px;
                    min-height: 0px; max-height: 20px; padding: 0;
                }
                #btnProjReload:hover { background: #d97706; }
                #btnProjReload:disabled { background: #94a3b8; }
            """)

            self.projLayout.addWidget(lblProj)
            self.projLayout.addWidget(self.editProjName, 1)
            self.projLayout.addWidget(self.btnProjCheck)
            self.projLayout.addWidget(self.btnProjReload)

            # Insert as layout (not widget) — same as tLayout/sizeLayout in .ui
            lhLayout.insertLayout(2, self.projLayout)

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


        # Wire Backbone Model combobox
        self._backbone_map = {"YOLOv8 Nano": "yolov8n.pt", "YOLOv11 Nano": "yolo11n.pt"}
        self.cmbBackbone = self.training_mode_widget.findChild(QComboBox, "cmbBackbone")
        if self.cmbBackbone:
            self.cmbBackbone.setCurrentIndex(0)
            self.cmbBackbone.currentTextChanged.connect(
                lambda text: setattr(self, '_selected_backbone', self._backbone_map.get(text, "yolov8n.pt"))
            )

        # Wire Add Class
        self.btnAddClass = self.training_mode_widget.findChild(QPushButton, "btnAddClass")
        if self.btnAddClass:
            self.btnAddClass.clicked.connect(self.add_training_class)
            # Hide Add Class button in detection mode (classes defined via tag panel)
            if hasattr(self, '_training_task') and self._training_task == "detection":
                self.btnAddClass.setVisible(False)


        
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
        _tc_h = 14 if self.is_small_screen else 22
        _tc_fs = 7 if self.is_small_screen else 10
        self.btnToggleConsole.setFixedHeight(_tc_h)
        self.btnToggleConsole.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnToggleConsole.setStyleSheet(f"""
            QPushButton {{
                background: #e2e8f0; color: #475569; border: 1px solid #cbd5e1;
                border-radius: 3px; font-size: {_tc_fs}px; font-weight: bold; padding: 1px 4px;
            }}
            QPushButton:hover {{ background: #cbd5e1; }}
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
            self.canvasAcc = TrainingCanvas(chart_acc_frame, title="Accuracy Over Epochs", ylabel="Accuracy (%)", color_train="#10b981", color_val="#f59e0b")
            chart_acc_frame.layout().addWidget(self.canvasAcc)
            self._charts = [self.canvasAcc]
        else:
            self._charts = []

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
        
        # Add default classes based on mode
        self.add_training_class("Class 1")
        if self._training_task != "detection":
            self.add_training_class("Class 2")
        
        self._training_init_done = True
        
        # Initially lock features until project is named
        if not hasattr(self, '_project_initialized') or not self._project_initialized:
            QTimer.singleShot(100, self._update_project_ui_lock)

        
        # Initially lock features until project is named
        QTimer.singleShot(100, self._update_project_ui_lock)

    def _proj_h(self):
        """Return project row height based on current resolution."""
        return 20 if getattr(self, 'is_small_screen', False) else 26

    def _proj_fs(self):
        """Return project row font size based on current resolution."""
        return 11 if getattr(self, 'is_small_screen', False) else 14

    def _validate_project_name_visual(self, text):
        """Highlight red if empty, normal if has text."""
        h = self._proj_h()
        fs = self._proj_fs()
        if not text.strip():
            self.editProjName.setStyleSheet(f"#editProjName {{ background: rgba(255, 255, 255, 0.9); border: 1px solid #ef4444; border-radius: 4px; padding: 0px 4px; font-size: {fs}px; min-height: 0px; max-height: {h}px; }}")
        else:
            self.editProjName.setStyleSheet(f"#editProjName {{ background: white; border: 1px solid #3b82f6; border-radius: 4px; padding: 0px 4px; font-size: {fs}px; min-height: 0px; max-height: {h}px; }}")

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
            
            # Lock project entry and transform Reload -> New
            self.editProjName.setDisabled(True)
            self.btnProjCheck.setDisabled(True)
            if hasattr(self, 'btnProjReload'):
                self.btnProjReload.setText("New")
                h = self._proj_h()
                fs = self._proj_fs()
                _new_w = 32 if self.is_small_screen else 50
                self.btnProjReload.setFixedSize(_new_w, h)
                self.btnProjReload.setStyleSheet(f"QPushButton {{ background: #64748b; color: white; border-radius: 6px; font-weight: bold; font-size: {fs}px; }} QPushButton:hover {{ background: #475569; }}")
                self.btnProjReload.setToolTip("Discard current and start a new project")
                try: self.btnProjReload.clicked.disconnect()
                except: pass
                self.btnProjReload.clicked.connect(self._reset_project_state)

            h = self._proj_h()
            fs = self._proj_fs()
            self.editProjName.setStyleSheet(f"#editProjName {{ background: #f1f5f9; border: 1px solid #cbd5e1; color: #64748b; border-radius: 4px; padding: 0px 4px; font-size: {fs}px; min-height: 0px; max-height: {h}px; }}")

            self.log_to_console(f"Project '{name}' initialized. Data will be saved in: /projects/data/{name}/")
            self._update_project_ui_lock()
            
        except Exception as e:
            self.log_to_console(f"Error creating project folder: {str(e)}")

    def _reset_project_state(self):
        """Wipe current project session and allow starting over."""
        reply = QMessageBox.question(
            self, "Start New Project?",
            "This will clear the current session. Images on disk will NOT be deleted.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._project_initialized = False
        self._current_project_name = ""
        
        # Restore Project UI
        self.editProjName.setDisabled(False)
        self.editProjName.setText("")
        self.btnProjCheck.setDisabled(False)
        self._validate_project_name_visual("")
        
        # Restore Reload Button
        if hasattr(self, 'btnProjReload'):
            self.btnProjReload.setText("📂")
            h = self._proj_h()
            fs = self._proj_fs()
            self.btnProjReload.setFixedSize(h, h)
            self.btnProjReload.setStyleSheet(f"""
                #btnProjReload {{
                    background: #f59e0b; color: white; border-radius: 4px; font-size: {fs + 1}px;
                    min-height: 0px; max-height: {h}px; padding: 0;
                }}
                #btnProjReload:hover {{ background: #d97706; }}
                #btnProjReload:disabled {{ background: #94a3b8; }}
            """)
            self.btnProjReload.setToolTip("Reload existing project")
            try: self.btnProjReload.clicked.disconnect()
            except: pass
            self.btnProjReload.clicked.connect(self._show_reload_dialog)

        # Wipe Data Collection
        self._reset_training_classes()
        self.log_to_console("Project reset. Ready for new input.")
        self._update_project_ui_lock()

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

        # Lock project name UI and transform Reload -> New
        self.editProjName.setText(project_name)
        self.editProjName.setDisabled(True)
        self.btnProjCheck.setDisabled(True)
        
        if hasattr(self, 'btnProjReload'):
            self.btnProjReload.setText("New")
            h = self._proj_h()
            fs = self._proj_fs()
            _new_w = 32 if self.is_small_screen else 50
            self.btnProjReload.setFixedSize(_new_w, h)
            self.btnProjReload.setStyleSheet(f"QPushButton {{ background: #64748b; color: white; border-radius: 6px; font-weight: bold; font-size: {fs}px; }} QPushButton:hover {{ background: #475569; }}")
            self.btnProjReload.setToolTip("Discard current and start a new project")
            try: self.btnProjReload.clicked.disconnect()
            except: pass
            self.btnProjReload.clicked.connect(self._reset_project_state)

        h = self._proj_h()
        fs = self._proj_fs()
        self.editProjName.setStyleSheet(
            f"#editProjName {{ background: #f1f5f9; border: 1px solid #cbd5e1; color: #64748b; border-radius: 4px; padding: 0px 4px; font-size: {fs}px; min-height: 0px; max-height: {h}px; }}"
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
        if self.is_small_screen:
            self._bbox_panel.setFixedHeight(200)
        else:
            self._bbox_panel.setMinimumHeight(450)
            self._bbox_panel.setMaximumHeight(16777215)
        self._bbox_panel.setStyleSheet("""
            QFrame#bboxPanel {
                background: #0f172a;
                border-top: 3px solid #8b5cf6;
                border-radius: 8px 8px 0px 0px;
            }
        """)
        
        panel_layout = QVBoxLayout(self._bbox_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # Drag handle
        drag_handle = QFrame()
        drag_handle.setObjectName("bboxHandle")
        drag_handle.setFixedHeight(12 if self.is_small_screen else 20)
        drag_handle.setCursor(Qt.CursorShape.SizeVerCursor)
        drag_handle.setStyleSheet("""
            QFrame#bboxHandle { background: rgba(139,92,246,0.25); }
            QFrame#bboxHandle:hover { background: rgba(139,92,246,0.5); }
        """)
        handle_layout = QHBoxLayout(drag_handle)
        pip = QLabel()
        pip.setFixedSize(40, 4)
        pip.setStyleSheet("background: rgba(255,255,255,0.6); border-radius: 2px;")
        handle_layout.addStretch()
        handle_layout.addWidget(pip)
        handle_layout.addStretch()
        panel_layout.addWidget(drag_handle)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e293b, stop:1 #1a2332); border-bottom: 1px solid #334155;")
        header_layout = QHBoxLayout(header)
        _hm = 6 if self.is_small_screen else 12
        header_layout.setContentsMargins(_hm, 2 if self.is_small_screen else 4, _hm, 2 if self.is_small_screen else 4)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        lbl_title = QLabel()
        lbl_title.setObjectName("bboxTitle")
        _bbox_title_fs = 8 if self.is_small_screen else 16
        _bbox_hint_fs = 7 if self.is_small_screen else 13
        lbl_title.setStyleSheet(f"color: white; font-weight: bold; font-size: {_bbox_title_fs}px;")
        self._bbox_hint = QLabel("Click an image above to annotate it.")
        self._bbox_hint.setStyleSheet(f"color: #94a3b8; font-size: {_bbox_hint_fs}px;")
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(self._bbox_hint)
        
        btn_close_bbox = QPushButton("✕")
        _cls_sz = 20 if self.is_small_screen else 32
        btn_close_bbox.setFixedSize(_cls_sz, _cls_sz)
        btn_close_bbox.setCursor(Qt.CursorShape.PointingHandCursor)
        _cls_fs = 11 if self.is_small_screen else 18
        btn_close_bbox.setStyleSheet(f"QPushButton {{ background: transparent; color: #64748b; border: none; font-size: {_cls_fs}px; border-radius: {_cls_sz // 2}px; }} QPushButton:hover {{ color: #f87171; background: rgba(248,113,113,0.1); }}")
        btn_close_bbox.clicked.connect(self._close_bbox_panel)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(btn_close_bbox)
        panel_layout.addWidget(header)
        
        # Canvas area
        self._bbox_canvas = AnnotationLabel()
        self._bbox_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bbox_canvas.setStyleSheet("background: #000; color: #475569; font-size: 13px;")
        self._bbox_canvas.setText("Select an image to annotate")
        self._bbox_canvas.save_requested.connect(self._save_bbox_annotation)
        self._bbox_canvas.close_requested.connect(self._close_bbox_panel)
        panel_layout.addWidget(self._bbox_canvas, 1)
        
        # Floating Shutter Button for the right-panel webcam (visible when cam active)
        self._tr_shutter_btn = QPushButton("📸 Capture Frame")
        self._tr_shutter_btn.setParent(self) # Floating
        _shutter_w = 90 if self.is_small_screen else 135
        _shutter_h = 24 if self.is_small_screen else 36
        _shutter_fs = 8 if self.is_small_screen else 12
        self._tr_shutter_btn.setFixedSize(_shutter_w, _shutter_h)
        self._tr_shutter_btn.setVisible(False)
        self._tr_shutter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tr_shutter_btn.setStyleSheet(f"""
            QPushButton {{
                background: #3b82f6; color: white; border: 2px solid white;
                border-radius: {_shutter_h // 2}px; font-weight: bold; font-size: {_shutter_fs}px;
            }}
            QPushButton:hover {{ background: #2563eb; }}
        """)
        self._tr_shutter_btn.clicked.connect(self._capture_image)
        
        # Bottom action area — enhanced with navigation and info
        bottom_bar = QFrame()
        bottom_bar.setStyleSheet("background: #0f172a; border-top: 1px solid #1e293b; padding-top: 2px;")
        bottom_bar_layout = QVBoxLayout(bottom_bar)
        _bb_m = 6 if self.is_small_screen else 16
        bottom_bar_layout.setContentsMargins(_bb_m, 2 if self.is_small_screen else 4, _bb_m, 2 if self.is_small_screen else 6)
        bottom_bar_layout.setSpacing(2 if self.is_small_screen else 4)

        # Row 1: Status and Navigation Info
        info_row = QHBoxLayout()
        _prog_fs = 7 if self.is_small_screen else 13
        self._lbl_batch_progress = QLabel("Image 0 of 0")
        self._lbl_batch_progress.setStyleSheet(f"color: #94a3b8; font-size: {_prog_fs}px; font-weight: bold;")

        _sc_fs = 6 if self.is_small_screen else 10
        shortcut_hint = QLabel("[Enter] Save  [Del] Clear  [Esc] Close")
        shortcut_hint.setStyleSheet(f"color: #64748b; font-size: {_sc_fs}px;")
        
        info_row.addWidget(self._lbl_batch_progress)
        info_row.addStretch()
        info_row.addWidget(shortcut_hint)
        bottom_bar_layout.addLayout(info_row)

        # Row 2: Navigation and Action Buttons
        action_row = QHBoxLayout()
        
        _nav_sz = 18 if self.is_small_screen else 34
        btn_prev = QPushButton("◀")
        btn_prev.setFixedSize(_nav_sz, _nav_sz)
        btn_prev.setToolTip("Previous Image")
        btn_prev.setStyleSheet(f"""
            QPushButton {{ background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: {_nav_sz // 2}px; font-weight: bold; font-size: {8 if self.is_small_screen else 16}px; }}
            QPushButton:hover {{ background: #334155; border-color: #8b5cf6; color: white; }}
            QPushButton:disabled {{ color: #334155; border-color: #1e293b; }}
        """)
        btn_prev.clicked.connect(lambda: self._navigate_annotation(-1))
        self._btn_prev_annotation = btn_prev

        btn_next = QPushButton("▶")
        btn_next.setFixedSize(_nav_sz, _nav_sz)
        btn_next.setToolTip("Next Image / Skip")
        btn_next.setStyleSheet(f"""
            QPushButton {{ background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: {_nav_sz // 2}px; font-weight: bold; font-size: {8 if self.is_small_screen else 16}px; }}
            QPushButton:hover {{ background: #334155; border-color: #8b5cf6; color: white; }}
            QPushButton:disabled {{ color: #334155; border-color: #1e293b; }}
        """)
        btn_next.clicked.connect(lambda: self._navigate_annotation(1))
        self._btn_next_annotation = btn_next

        # BBox Save button
        _save_fs = 8 if self.is_small_screen else 14
        _save_pad = "3px 8px" if self.is_small_screen else "8px 20px"
        _save_min = 60 if self.is_small_screen else 140
        self._bbox_save_btn = QPushButton("Save & Continue ▶")
        _save_br = 4 if self.is_small_screen else 6
        self._bbox_save_btn.setStyleSheet(f"""
            QPushButton {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6);
                         color: white; border: none; border-radius: {_save_br}px;
                         font-weight: bold; font-size: {_save_fs}px; padding: {_save_pad}; min-width: {_save_min}px; }}
            QPushButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6d28d9, stop:1 #7c3aed); }}
        """)
        self._bbox_save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._bbox_save_btn.clicked.connect(self._save_bbox_annotation)
        
        # Camera shutter button
        _cam_fs = 7 if self.is_small_screen else 14
        _cam_pad = "3px 8px" if self.is_small_screen else "10px 32px"
        _cam_min = 50 if self.is_small_screen else 120
        self._cam_shutter_btn = QPushButton("⬤  Capture")
        self._cam_shutter_btn.setStyleSheet(f"""
            QPushButton {{
                background: white; color: #1e293b; border: 4px solid #94a3b8;
                border-radius: 20px; font-weight: bold; font-size: {_cam_fs}px;
                padding: {_cam_pad}; min-width: {_cam_min}px;
            }}
            QPushButton:hover {{ background: #f0f9ff; border-color: #3b82f6; color: #1d4ed8; }}
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
        self._bbox_class_selector.setStyleSheet("background: #0f172a; border-top: 1px solid rgba(139,92,246,0.2);")
        self._class_selector_layout = QHBoxLayout(self._bbox_class_selector)
        _cs_m = 4 if self.is_small_screen else 12
        self._class_selector_layout.setContentsMargins(_cs_m, 2 if self.is_small_screen else 4, _cs_m, 2 if self.is_small_screen else 4)
        self._class_selector_layout.setSpacing(3 if self.is_small_screen else 6)
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
            # CRITICAL: Set fixed height to 0 to fully collapse the panel and reclaim space
            # Just setVisible(False) leaves the space reserved in the layout
            self._bbox_panel.setFixedHeight(0)
            # Restore scroll area max height so it reclaims full space
            if not self.is_small_screen:
                scroll = self.training_mode_widget.findChild(QWidget, "classScrollArea")
                if scroll:
                    scroll.setMaximumHeight(16777215)

    def _bbox_handle_press(self, event):
        self._bbox_drag_start_y = event.globalPos().y()
        self._bbox_drag_start_h = self._bbox_panel.height()
        # When user starts dragging, uncap scroll area so both can resize freely
        if not self.is_small_screen:
            scroll = self.training_mode_widget.findChild(QWidget, "classScrollArea")
            if scroll:
                scroll.setMaximumHeight(16777215)

    def _bbox_handle_move(self, event):
        delta = int(self._bbox_drag_start_y - event.globalPos().y())
        # Dynamically cap to leftPanel height so bottom bar never clips off screen
        left_panel = self.training_mode_widget.findChild(QFrame, "leftPanel")
        if left_panel:
            # Reserve space for the header above the bbox panel (~80px for small, ~120px normal)
            _reserve = 60 if self.is_small_screen else 100
            _max_h = left_panel.height() - _reserve
        else:
            _max_h = 350 if self.is_small_screen else 500
        new_h = max(100, min(_max_h, self._bbox_drag_start_h + delta))
        if self.is_small_screen:
            self._bbox_panel.setFixedHeight(new_h)
        else:
            self._bbox_panel.setMinimumHeight(new_h)
            self._bbox_panel.setMaximumHeight(new_h)

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
        h_margin = 5 if self.is_small_screen else 12
        header_layout.setContentsMargins(h_margin, 3 if self.is_small_screen else 6, h_margin, 3 if self.is_small_screen else 6)
        header_layout.setSpacing(3 if self.is_small_screen else 6)
        
        # Editable class name
        name_edit = QLineEdit(label)
        name_edit.setObjectName("classNameEdit")
        if hasattr(self, '_training_task') and self._training_task == "detection":
            name_edit.setVisible(False)
            
        _name_font = 12 if self.is_small_screen else 20
        name_edit.setStyleSheet(f"""

            QLineEdit {{
                font-weight: bold; font-size: {_name_font}px; color: #1e293b;
                border: 1px solid transparent; border-radius: 4px;
                background: transparent; padding: 2px 6px;
            }}
            QLineEdit:focus {{
                border: 1px solid #3b82f6; background: white;
            }}
            QLineEdit:hover {{ border: 1px solid #cbd5e1; }}
        """)
        
        count_badge = QLabel("0 imgs")
        _badge_font = 8 if self.is_small_screen else 14
        count_badge.setFixedWidth(38 if self.is_small_screen else 68)
        count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_badge.setStyleSheet(f"""
            background: #e2e8f0; color: #64748b;
            border-radius: 10px; padding: 2px 2px;
            font-size: {_badge_font}px; font-weight: bold;
        """)
        
        status_check = QLabel("")
        status_check.setFixedWidth(14 if self.is_small_screen else 20)
        status_check.setStyleSheet(f"color: #10b981; font-weight: bold; font-size: {11 if self.is_small_screen else 16}px;")
        
        btn_del = QPushButton("🗑")
        _del_sz = 18 if self.is_small_screen else 26
        btn_del.setFixedSize(_del_sz, _del_sz)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; color: #94a3b8; font-size: {11 if self.is_small_screen else 16}px; }}
            QPushButton:hover {{ color: #ef4444; }}
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
        _b_margin = 4 if self.is_small_screen else 12
        body_layout.setContentsMargins(_b_margin, _b_margin, _b_margin, _b_margin)
        body_layout.setSpacing(3 if self.is_small_screen else 8)
        
        # Image thumbnail area (Scroll Area)
        scroll = QScrollArea()
        scroll.setObjectName("imgScroll")
        is_detection = (hasattr(self, '_training_task') and self._training_task == "detection")
        
        if is_detection:
            scroll.setMinimumHeight(180 if self.is_small_screen else 300)
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
        # Placeholder container (icon + hint text, tightly grouped)
        hint_container = QWidget()
        hint_container.setStyleSheet("background: transparent;")
        hint_vbox = QVBoxLayout(hint_container)
        hint_vbox.setContentsMargins(0, 0, 0, 0)
        hint_vbox.setSpacing(0)

        hint_icon = QLabel("🖼️")
        hint_icon.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        _ico_sz = 48 if self.is_small_screen else 108
        hint_icon.setStyleSheet(f"font-size: {_ico_sz}px; color: rgba(203, 213, 225, 0.4); padding: 0; margin: 0;")
        from PyQt5.QtWidgets import QGraphicsOpacityEffect
        _op = QGraphicsOpacityEffect(hint_icon)
        _op.setOpacity(0.45)
        hint_icon.setGraphicsEffect(_op)

        hint_lbl = QLabel("No images collected yet.")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        _hint_font = 10 if self.is_small_screen else 14
        hint_lbl.setStyleSheet(f"color: #94a3b8; font-size: {_hint_font}px; font-weight: 50; padding: 0; margin: 0;")

        hint_vbox.addStretch()
        hint_vbox.addWidget(hint_icon)
        hint_vbox.addWidget(hint_lbl)
        hint_vbox.addStretch()

        if is_detection:
            hint_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            # Reduce minimum height slightly to prevent squeezing the tag panel below
            hint_container.setMinimumHeight(100 if self.is_small_screen else 130)
        
        body_layout.addWidget(hint_container)
        body_layout.addWidget(scroll)
        scroll.setVisible(False)
        
        # ── Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4 if self.is_small_screen else 8)

        _btn_fs = 10 if self.is_small_screen else 15
        _btn_pad = 2 if self.is_small_screen else 6
        _btn_br = 4 if self.is_small_screen else 6
        _btn_h = 26 if self.is_small_screen else 0
        _btn_fw = "normal" if self.is_small_screen else "600"
        _cam_txt = "Webcam" if self.is_small_screen else "🎥 Webcam"
        _upl_txt = "Upload" if self.is_small_screen else "📁 Upload"
        _lbl_txt = "Label" if self.is_small_screen else "⬚ Label"
        btn_cam = QPushButton(_cam_txt)
        btn_cam.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cam.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if _btn_h: btn_cam.setFixedHeight(_btn_h)
        btn_cam.setStyleSheet(f"""
            QPushButton {{
                background: white; border: 1px solid #e2e8f0; color: #475569;
                border-radius: {_btn_br}px; padding: {_btn_pad}px; font-weight: {_btn_fw}; font-size: {_btn_fs}px;
            }}
            QPushButton:hover {{ background: #f8fafc; border-color: #3b82f6; color: #3b82f6; }}
            QPushButton[active="true"] {{ background: #eff6ff; border-color: #3b82f6; color: #2563eb; }}
        """)

        btn_upload = QPushButton(_upl_txt)
        btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if _btn_h: btn_upload.setFixedHeight(_btn_h)
        btn_upload.setStyleSheet(f"""
            QPushButton {{
                background: white; border: 1px solid #e2e8f0; color: #475569;
                border-radius: {_btn_br}px; padding: {_btn_pad}px; font-weight: {_btn_fw}; font-size: {_btn_fs}px;
            }}
            QPushButton:hover {{ background: #f8fafc; border-color: #10b981; color: #059669; }}
        """)

        btn_label = QPushButton(_lbl_txt)
        btn_label.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_label.setVisible(self._training_task == "detection")
        btn_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if _btn_h: btn_label.setFixedHeight(_btn_h)
        btn_label.setStyleSheet(f"""
            QPushButton {{
                background: white; border: 1px solid #f87171; color: #ef4444;
                border-radius: {_btn_br}px; padding: {_btn_pad}px; font-weight: {_btn_fw}; font-size: {_btn_fs}px;
            }}
            QPushButton:hover {{ background: #fef2f2; border-color: #ef4444; }}
            QPushButton:disabled {{ background: #fff5f5; color: #fca5a5; border: 1px solid #fecaca; }}
        """)

        btn_row.addWidget(btn_cam, 1)
        btn_row.addWidget(btn_upload, 1)
        btn_row.addWidget(btn_label, 1)
        
        # ── Tag Panel (Detection Mode Only)
        tag_panel = None
        if hasattr(self, '_training_task') and self._training_task == "detection":
            tag_panel = MultiClassTagPanel()
            body_layout.addWidget(tag_panel)
            # Validation logic: disable Label button until classes are defined
            tag_panel.validation_changed.connect(btn_label.setEnabled)
            btn_label.setEnabled(False) # Initial state
            btn_label.setToolTip("Please define at least 1 class name to start labeling.")
        
        # Add spacing before buttons to prevent overlap
        body_layout.addSpacing(2 if self.is_small_screen else 10)
        body_layout.addLayout(btn_row)
        
        card_layout.addWidget(body)
        
        # ── Store class data
        class_info = {
            "name_edit": name_edit,
            "count_badge": count_badge,
            "hint_lbl": hint_lbl,
            "hint_icon": hint_icon,
            "hint_container": hint_container,
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
        if info.get("hint_icon"): info["hint_icon"].setVisible(False)
        if info.get("hint_container"): info["hint_container"].setVisible(False)
        info["scroll"].setVisible(True)

        # Create thumbnail tile
        _tile_sz = 56 if self.is_small_screen else 80
        _pix_sz = _tile_sz - 4
        tile = QFrame()
        tile.setFixedSize(_tile_sz, _tile_sz)
        tile.setStyleSheet("QFrame { border-radius: 6px; border: 2px solid #e2e8f0; }")
        tile_layout = QVBoxLayout(tile)
        tile_layout.setContentsMargins(0, 0, 0, 0)

        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_lbl.setStyleSheet("border-radius: 4px;")

        pix = QPixmap(image_path)
        if not pix.isNull():
            img_lbl.setPixmap(pix.scaled(_pix_sz, _pix_sz, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))

        # If detection mode, make tile clickable to annotate via double click
        if self._training_task == "detection":
            tile.setStyleSheet("QFrame { border-radius: 6px; border: 2px solid #f87171; }")
            tile.setCursor(Qt.CursorShape.PointingHandCursor)
            tile.mouseDoubleClickEvent = lambda e, p=image_path, ci=idx: self._open_bbox_editor(p, ci)

        tile_layout.addWidget(img_lbl)

        # Delete button (top-right corner overlay)
        _del_sz = 14 if self.is_small_screen else 18
        btn_del_img = QPushButton("×", tile)
        btn_del_img.setFixedSize(_del_sz, _del_sz)
        btn_del_img.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del_img.setStyleSheet(f"""
            QPushButton {{
                background: rgba(239,68,68,0.85); color: white; border: none;
                border-radius: {_del_sz // 2}px; font-size: {_del_sz - 4}px; font-weight: bold;
                padding: 0; margin: 0;
            }}
            QPushButton:hover {{ background: rgba(220,38,38,1.0); }}
        """)
        btn_del_img.move(_tile_sz - _del_sz - 2, 2)
        btn_del_img.raise_()
        btn_del_img.clicked.connect(lambda _, p=image_path, ci=idx, t=tile: self._delete_image_tile(ci, p, t))

        # Insert into grid (wrap if Detection) or layout
        grid = info["img_grid"]
        if isinstance(grid, QGridLayout):
            cols = 5 if self.is_small_screen else 4
            grid_pos = len(info["images"]) - 1
            row, col = divmod(grid_pos, cols)
            grid.addWidget(tile, row, col)
        else:
            grid.insertWidget(grid.count() - 1, tile)

        self._update_dataset_summary()
        self._update_label_status(idx)

    def _delete_image_tile(self, class_idx, image_path, tile_widget):
        """Delete an image from disk (+ annotation) and remove its tile."""
        info = self._class_data[class_idx]
        if info is None:
            return

        # Remove image file
        if os.path.exists(image_path):
            os.remove(image_path)

        # Remove annotation file (.txt) if exists
        annotation_path = os.path.splitext(image_path)[0] + ".txt"
        if os.path.exists(annotation_path):
            os.remove(annotation_path)

        # Remove .npy cache if exists
        npy_path = os.path.splitext(image_path)[0] + ".npy"
        if os.path.exists(npy_path):
            os.remove(npy_path)

        # Remove from in-memory list
        if image_path in info["images"]:
            info["images"].remove(image_path)

        # Update badge count
        count = len(info["images"])
        info["count_badge"].setText(f"{count} imgs")
        if count == 0:
            info["hint_lbl"].setVisible(True)
            if info.get("hint_icon"): info["hint_icon"].setVisible(True)
            if info.get("hint_container"): info["hint_container"].setVisible(True)
            info["scroll"].setVisible(False)

        # Remove tile widget from UI
        tile_widget.setParent(None)
        tile_widget.deleteLater()

        self._update_dataset_summary()
        self._update_label_status(class_idx)
        self.log_to_console(f"Deleted: {os.path.basename(image_path)}")

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
            
            _cs_h = 16 if self.is_small_screen else 30
            _cs_fs = 7 if self.is_small_screen else 13
            _cs_pad = "1px 4px" if self.is_small_screen else "4px 12px"
            for i, name in enumerate(names):
                btn = QPushButton(name)
                btn.setCheckable(True)
                btn.setFixedHeight(_cs_h)
                color = colors[i % len(colors)]
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; color: {color}; border: 1.5px solid {color};
                        border-radius: {_cs_h // 2}px; font-weight: bold; font-size: {_cs_fs}px; padding: {_cs_pad};
                    }}
                    QPushButton:hover {{ background: rgba({QColor(color).red()},{QColor(color).green()},{QColor(color).blue()},25); }}
                    QPushButton:checked {{ background: {color}; color: white; border-color: {color}; }}
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
            
        was_visible = self._bbox_panel.isVisible()
        self._bbox_panel.setVisible(True)
        # CRITICAL: Restore proper height when reopening (was set to 0 when closed)
        if self.is_small_screen:
            self._bbox_panel.setFixedHeight(200)
        else:
            self._bbox_panel.setMinimumHeight(450)
            self._bbox_panel.setMaximumHeight(16777215)
        self._bbox_panel_visible = True
        self._bbox_canvas.setFocus()
        self._bbox_canvas.update()

        # Expand panel to 2/3 of column on first open only (not during navigation)
        if not self.is_small_screen and not was_visible:
            def _expand():
                parent = self._bbox_panel.parentWidget()
                if not parent: return
                avail_h = parent.height()
                if avail_h < 200: return
                target_h = max(400, int(avail_h * 2 / 3))
                # Lock the panel to the target height
                self._bbox_panel.setMinimumHeight(target_h)
                self._bbox_panel.setMaximumHeight(target_h)
                # Shrink scroll area so layout has room
                scroll = self.training_mode_widget.findChild(QWidget, "classScrollArea")
                if scroll:
                    remaining = avail_h - target_h - 80  # reserve for header + add-class btn
                    scroll.setMaximumHeight(max(60, remaining))
            QTimer.singleShot(100, _expand)

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
        
        # Update button look — match creation sizes from _add_class_card
        _ls = self.is_small_screen
        _lfs = 10 if _ls else 15
        _lpad = 2 if _ls else 6
        _lbr = 4 if _ls else 6
        _lfw = "normal" if _ls else "600"
        _lfw2 = "normal" if _ls else "600"
        if all_labeled:
            info["btn_label"].setStyleSheet(f"""
                QPushButton {{
                    background: #10b981; border: 1px solid #059669; color: white;
                    border-radius: {_lbr}px; padding: {_lpad}px; font-weight: {_lfw}; font-size: {_lfs}px;
                }}
                QPushButton:hover {{ background: #059669; }}
            """)
            info["status_check"].setText("✔")
        else:
            # Revert to standard red variant
            info["btn_label"].setStyleSheet(f"""
                QPushButton {{
                    background: white; border: 1px solid #f87171; color: #ef4444;
                    border-radius: {_lbr}px; padding: {_lpad}px; font-weight: {_lfw2}; font-size: {_lfs}px;
                }}
                QPushButton:hover {{ background: #fef2f2; border-color: #ef4444; }}
                QPushButton:disabled {{ background: #fff5f5; color: #fca5a5; border: 1px solid #fecaca; }}
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
                # Don't show yet — _update_cam_frame will position and reveal it
                self._tr_shutter_btn_pending = True
        
        self._close_bbox_panel()  # Hide annotation panel during live capture

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
        if self._tr_shutter_btn.isVisible() or getattr(self, '_tr_shutter_btn_pending', False):
            try:
                cam_rect = self.trCamDisplay.geometry()
                global_pos = self.trCamDisplay.mapToGlobal(QPoint(0,0))
                btn_x = global_pos.x() + (cam_rect.width() - self._tr_shutter_btn.width()) // 2
                btn_y = global_pos.y() + cam_rect.height() - 70
                self._tr_shutter_btn.move(self.mapFromGlobal(QPoint(btn_x, btn_y)))
                # Show only after positioned to prevent top-left flash
                if getattr(self, '_tr_shutter_btn_pending', False):
                    self._tr_shutter_btn.setVisible(True)
                    self._tr_shutter_btn_pending = False
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
            spin_epochs = self.training_mode_widget.findChild(QSpinBox, "spinEpochs")
            if spin_epochs: spin_epochs.setEnabled(True)
            self.txtTrainLog.appendPlainText("> Training Stopped by User.")
            return

        # 0. Kill any running processes and free shared memory on Jetson
        self._stop_fast_validation()
        self._stop_webcam()
        import gc, subprocess
        gc.collect()
        # Drop Linux page caches to free unified memory on Jetson
        # Use sudo -n (non-interactive) so it silently skips if no passwordless sudo
        try:
            subprocess.run(["sudo", "-n", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"],
                           timeout=5, capture_output=True)
        except Exception:
            pass
        # Free any PyTorch CUDA memory held by the main app
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except Exception:
            pass
        gc.collect()

        # 1. Validation Logic
        if not self._project_initialized:
            self.log_to_console("Error: Project not initialized.", is_error=True)
            return

        # Check for selected backbone model
        project_root = os.path.dirname(os.path.abspath(__file__))
        backbone_path = Path(project_root) / "src" / "modules" / "training" / self._selected_backbone

        if not backbone_path.exists():
            self.log_to_console(f"Error: Backbone model not found at {backbone_path}", is_error=True)
            self.log_to_console(f"Please place '{self._selected_backbone}' in the src/modules/training/ folder.")
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
        if spin_epochs: spin_epochs.setEnabled(False)
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

        # Clean stale model files from previous runs to prevent false success detection
        self._local_model_path = None
        self._last_exported_engine = None
        self._last_exported_onnx = None
        model_dir = os.path.join(project_root, "src", "modules", "training")
        for stale in ["best.pt", "best.onnx", "best.engine"]:
            stale_path = os.path.join(model_dir, stale)
            if os.path.exists(stale_path):
                try:
                    os.remove(stale_path)
                except OSError:
                    pass

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
            "--names", names,
            "--project_name", self._current_project_name
        ]
        
        self._train_process.setProgram(sys.executable)
        self._train_process.setArguments(args)

        # Connect Signals
        self._train_process.readyReadStandardOutput.connect(self._on_train_stdout)
        self._train_process.readyReadStandardError.connect(self._on_train_stderr)
        self._train_process.finished.connect(self._on_train_finished)

        self._training_is_running = True
        self._early_stopped = False
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

            elif "EarlyStopping" in line and "stopped early" in line:
                self._early_stopped = True
                self.txtTrainLog.appendPlainText(f"  [INFO] {line}")

            elif line.startswith("CONVERT:"):
                # Engine conversion progress from trainer.py
                msg = line[8:].strip()
                self.txtTrainLog.appendPlainText(f"  [CONVERT] {msg}")
                # Start converting animation on first CONVERT message
                if not self._convert_dot_timer.isActive():
                    if hasattr(self, 'btnSaveModel') and self.btnSaveModel:
                        self.btnSaveModel.setVisible(True)
                        self.btnSaveModel.setText("Converting...")
                        self.btnSaveModel.setEnabled(False)
                        self.btnSaveModel.setStyleSheet("""
                            QPushButton {
                                background: #6366f1; color: white; border-radius: 8px;
                                font-weight: bold; font-size: 14px; padding: 6px 12px;
                            }
                        """)
                        self._convert_dot_count = 0
                        self._convert_dot_timer.start()

            elif line.startswith("RESULT_MODEL_ONNX:"):
                self._last_exported_onnx = line[18:].strip()

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

    def _animate_convert_dots(self):
        """Cycle dots on Save Model button to show conversion is active."""
        self._convert_dot_count = (self._convert_dot_count % 3) + 1
        dots = "." * self._convert_dot_count
        if hasattr(self, 'btnSaveModel') and self.btnSaveModel:
            self.btnSaveModel.setText(f"Converting{dots}")

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

        # Re-enable epoch config
        spin_epochs = self.training_mode_widget.findChild(QSpinBox, "spinEpochs")
        if spin_epochs: spin_epochs.setEnabled(True)

        if exit_code == 0 or has_model:
            if getattr(self, '_early_stopped', False):
                self.btnStartTraining.setText("✅ Best weight achieved")
                self.btnStartTraining.setToolTip("Training stopped early — no improvement for 20 epochs")
                # Show small hint below button
                btn_parent = self.btnStartTraining.parentWidget()
                if btn_parent and btn_parent.layout():
                    hint = QLabel("Stopped early — best model saved")
                    hint.setObjectName("earlyStopHint")
                    hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    hint.setStyleSheet("color: #64748b; font-size: 10px; font-style: italic; background: transparent; margin: 0; padding: 0;")
                    idx = btn_parent.layout().indexOf(self.btnStartTraining)
                    btn_parent.layout().insertWidget(idx + 1, hint)
            else:
                self.btnStartTraining.setText("✅ Training Complete")
                self.btnStartTraining.setToolTip("")
            self.btnStartTraining.setEnabled(False)

            # Stop convert animation
            self._convert_dot_timer.stop()

            # Check if ONNX was produced
            project_root = os.path.dirname(os.path.abspath(__file__))
            local_onnx = os.path.join(project_root, "src", "modules", "training", "best.onnx")
            has_onnx = (self._last_exported_onnx and os.path.exists(self._last_exported_onnx)) or os.path.exists(local_onnx)

            if has_onnx:
                self.txtTrainLog.appendPlainText("> ONNX model ready. Starting validation...")
                self.log_to_console("ONNX ready. Starting live validation...")
            else:
                self.txtTrainLog.appendPlainText("> ONNX conversion failed. Validating with .pt...")
                self.log_to_console("ONNX conversion failed. Validating with .pt...")

            # Restore Save button for user to choose name and save
            if hasattr(self, 'btnSaveModel') and self.btnSaveModel:
                self.btnSaveModel.setText("💾  Save Model")
                self.btnSaveModel.setEnabled(True)
                self.btnSaveModel.setStyleSheet("""
                    QPushButton {
                        background: #10b981; color: white; border-radius: 8px;
                        font-weight: bold; font-size: 14px; padding: 6px 12px;
                    }
                    QPushButton:hover { background: #059669; }
                """)

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

        # Determine model path (prefer .onnx, fallback to .pt)
        project_root = os.path.dirname(os.path.abspath(__file__))
        local_onnx = os.path.join(project_root, "src", "modules", "training", "best.onnx")
        local_pt = os.path.join(project_root, "src", "modules", "training", "best.pt")

        if self._last_exported_onnx and os.path.exists(self._last_exported_onnx):
            model_path = self._last_exported_onnx
        elif os.path.exists(local_onnx):
            model_path = local_onnx
        elif self._local_model_path and os.path.exists(self._local_model_path):
            model_path = self._local_model_path
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
            self.btnStartTraining.setToolTip("")
            # Remove early stop hint label if present
            hint = self.btnStartTraining.parentWidget().findChild(QLabel, "earlyStopHint") if self.btnStartTraining.parentWidget() else None
            if hint: hint.deleteLater()

    def _save_trained_model(self):
        """Copy the trained .onnx model to projects/model/."""
        from PyQt5.QtWidgets import QMessageBox

        # Only save model — conversion is still running, wait for it
        if self._convert_process and self._convert_process.state() != QProcess.ProcessState.NotRunning:
            QMessageBox.information(self, "Please Wait", "ONNX conversion is still running.\nThe model will be saved automatically when done.")
            return

        project_root = os.path.dirname(os.path.abspath(__file__))
        local_onnx = os.path.join(project_root, "src", "modules", "training", "best.onnx")

        if not os.path.exists(local_onnx):
            QMessageBox.warning(self, "No ONNX Model", "No .onnx model found.\nConversion may have failed — check the console log.")
            return

        new_name, ok = QInputDialog.getText(
            self, "Save Model", "Enter model name:", text=self._current_project_name
        )
        if not ok or not new_name:
            return
        if not new_name.endswith(".onnx"):
            new_name += ".onnx"

        dest_path = os.path.join("projects", "model", new_name)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        try:
            import shutil
            shutil.copy2(local_onnx, dest_path)
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

    # Suppress noisy Qt/X11 clipboard warnings on Jetson Linux
    from PyQt5.QtCore import qInstallMessageHandler, QtMsgType
    def _qt_msg_handler(msg_type, context, msg):
        if "SelectionRequest" in msg or "XcbClipboard" in msg:
            return
        if msg_type == QtMsgType.QtWarningMsg:
            print(f"[Qt] {msg}")
    qInstallMessageHandler(_qt_msg_handler)

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