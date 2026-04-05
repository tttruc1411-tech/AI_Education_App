from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag

class DraggableFunctionWidget(QFrame):
    def __init__(self, function_name, parent=None):
        super().__init__(parent)
        self.function_name = function_name

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        # Only start drag if they move at least 5 pixels
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < 5:
            return

        # Prepare the data to be dragged
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # We store the function name so the editor knows what was dropped
        mime_data.setText(self.function_name) 
        drag.setMimeData(mime_data)

        # Start the drag operation
        drag.exec_(Qt.CopyAction)