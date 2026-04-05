from PyQt5.Qsci import QsciScintilla
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
editor = QsciScintilla()
print("Signals in QsciScintilla:")
for attr in dir(editor):
    if "autoComp" in attr:
        print(attr)
sys.exit()
