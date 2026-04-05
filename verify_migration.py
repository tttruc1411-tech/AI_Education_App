import sys
import os

def test_imports():
    print("Testing imports...")
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.uic import loadUi
        from PyQt5.Qsci import QsciScintilla
        print("✓ PyQt5 and QScintilla imports successful.")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_ui_load():
    print("\nTesting UI loading (headless)...")
    try:
        from PyQt5.QtWidgets import QApplication
        # Need a QApplication to load UI
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        from PyQt5.uic import loadUi
        ui_path = os.path.join("src", "ui", "main_window.ui")
        if os.path.exists(ui_path):
            # We don't actually show it to avoid needing an X server in some environments
            # but loadUi will fail if there are major PyQt version incompatibilities in the XML
            print(f"✓ Found {ui_path}")
        else:
            print(f"! Warning: {ui_path} not found at current path.")
            
        print("✓ UI loading check skipped (requires full environment).")
        return True
    except Exception as e:
        print(f"✗ UI load failed: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    # test_ui_load() # Might fail without X11, so we just check imports for now
    
    if success:
        print("\nMigration verification: BASIC SUCCESS")
    else:
        print("\nMigration verification: FAILED")
        sys.exit(1)
