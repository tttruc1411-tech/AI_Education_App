from PyQt5.Qsci import QsciScintilla
attrs = [x for x in dir(QsciScintilla) if x.startswith('SCN_')]
print("\n".join(attrs))
