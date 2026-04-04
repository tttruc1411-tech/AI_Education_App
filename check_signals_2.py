from PyQt6.Qsci import QsciScintilla
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
s = QsciScintilla()
attrs = [x for x in dir(s) if 'selection' in x.lower() or 'auto' in x.lower()]
print("\n".join(attrs))
sys.exit()
