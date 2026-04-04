from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
s = QsciScintilla()
print("QsciScintilla Signals:")
for attr in dir(s):
    try:
        val = getattr(s, attr)
        # Check if it's a bound signal or unbound signal
        if "pyqtSignal" in str(type(val)) or "pyqtBoundSignal" in str(type(val)):
            print(attr)
    except:
        continue
sys.exit()
