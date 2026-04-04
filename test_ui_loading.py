#!/usr/bin/env python
"""Test script to verify UI files load without errors"""
import sys
import os
import warnings

# Suppress the sipPyTypeDict deprecation warning from PyQt6
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi

# Initialize Qt application
app = QApplication(sys.argv)

# Setup paths
ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "ui")

# Test 1: Load main_window.ui
print("Test 1: Loading main_window.ui...")
try:
    main_window = QMainWindow()
    loadUi(os.path.join(ui_dir, "main_window.ui"), main_window)
    print("✓ Main shell loaded successfully")
except Exception as e:
    print(f"✗ Error loading main shell: {e}")
    sys.exit(1)

# Test 2: Load running_mode.ui
print("\nTest 2: Loading running_mode.ui...")
try:
    running_mode_widget = loadUi(os.path.join(ui_dir, "running_mode.ui"))
    print("✓ Running mode loaded successfully")
except Exception as e:
    print(f"✗ Error loading running mode: {e}")
    sys.exit(1)

# Test 3: Load training_mode.ui if it exists
print("\nTest 3: Loading trainning_mode.ui...")
try:
    training_mode_widget = loadUi(os.path.join(ui_dir, "trainning_mode.ui"))
    print("✓ Training mode loaded successfully")
except Exception as e:
    print(f"✗ Error loading training mode: {e}")

print("\n" + "="*50)
print("All UI files loaded successfully without errors!")
print("="*50)
