"""
File Manager Module for AI Education App
Handles Python file creation, reading, deletion, and management
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime


class FileManager:
    """Manages Python files in the project directory"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.files_dir = self.project_root / "projects"
        
        # Define the specific subdirectories
        self.code_dir = self.files_dir / "code"
        self.data_dir = self.files_dir / "data"
        self.model_dir = self.files_dir / "model"
        
        self._ensure_projects_dir()
    
    def _ensure_projects_dir(self) -> None:
        """Ensure 'projects' and its subdirectories exist"""
        self.files_dir.mkdir(exist_ok=True)
        self.code_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.model_dir.mkdir(exist_ok=True)
        
        print(f"[OK] Projects directory: {self.files_dir}")
        print(f"  - Code: {self.code_dir}")
        print(f"  - Data: {self.data_dir}")
        print(f"  - Model: {self.model_dir}")
    
    def list_files(self) -> List[Dict[str, str]]:
        """
        List all Python files in projects directory and code files from root
        
        Returns:
            List of dicts with file info: {'name': str, 'path': str, 'size': str, 'modified': str, 'folder': str}
        """
        files = []
        
        # List files from projects directory
        try:
            for file in sorted(self.files_dir.glob("*.py")):
                stat = file.stat()
                files.append({
                    'name': file.name,
                    'path': str(file),
                    'size': f"{stat.st_size} bytes",
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    'folder': 'Projects',
                    'editable': True
                })
        except Exception as e:
            print(f"Error listing project files: {e}")
        
        # List important code files from code directory (new structure) or root (legacy)
        code_files = [
            'main.py'
        ]
        
        # Check new code directory first (now that files are moved there)
        for code_file in code_files:
            file_path = self.code_dir / code_file
            if file_path.exists():
                try:
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': f"{stat.st_size} bytes",
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        'folder': 'Code',
                        'editable': False  # Mark as read-only
                    })
                except Exception as e:
                    print(f"Error listing code file {code_file}: {e}")
        
        # Fallback to legacy locations if not found in new location
        legacy_files = [
            ('main.py', self.project_root / 'main.py'),
            ('face_detection.py', self.project_root / 'curriculum' / 'face_detection.py')
        ]
        
        for name, file_path in legacy_files:
            if file_path.exists() and not any(f['name'] == name and f['folder'] == 'Code' for f in files):
                try:
                    stat = file_path.stat()
                    files.append({
                        'name': name,
                        'path': str(file_path),
                        'size': f"{stat.st_size} bytes",
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        'folder': 'Code',
                        'editable': False  # Mark as read-only
                    })
                except Exception as e:
                    print(f"Error listing legacy code file {name}: {e}")
        
        return files

    def get_run_file_path(self, filename: str) -> Optional[Path]:
        """Return the best path to run a file from.

        Priority:
        1. projects/code/{filename} (modified copy)
        2. projects/{filename} (user-created/edited file)
        3. curriculum/{filename} (example source)
        4. project root/{filename} (main.py)
        """
        if not filename.endswith('.py'):
            filename += '.py'

        # Modified copy in code folder
        code_copy = self.code_dir / filename
        if code_copy.exists():
            return code_copy

        # User project file
        project_file = self.files_dir / filename
        if project_file.exists():
            return project_file

        # Curriculum fallback
        curriculum_file = self.project_root / 'curriculum' / filename
        if curriculum_file.exists():
            return curriculum_file

        # Root fallback (main.py, etc.)
        root_file = self.project_root / filename
        if root_file.exists():
            return root_file

        return None

    def save_run_copy(self, filename: str, content: str) -> Dict[str, any]:
        """Save modified example into code folder for run-time use."""
        if not filename.endswith('.py'):
            filename += '.py'

        self.code_dir.mkdir(parents=True, exist_ok=True)
        code_path = self.code_dir / filename

        try:
            code_path.write_text(content, encoding='utf-8')
            return {
                'success': True,
                'message': f"Modified copy saved to {code_path}",
                'path': str(code_path)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error saving modified copy: {str(e)}",
                'path': str(code_path)
            }
    
    def create_file(self, filename: str, content: str = None, folder: str = 'Projects') -> Dict[str, any]:
        """
        Create a new Python file in Projects or Code directory
        
        Args:
            filename: Name of the file (with or without .py extension)
            content: Initial file content (default: empty template)
            folder: 'Projects' or 'Code'
        
        Returns:
            Dict with 'success': bool, 'message': str, 'path': str
        """
        # Ensure .py extension
        if not filename.endswith('.py'):
            filename += '.py'

        # Validate filename
        if not self._is_valid_filename(filename):
            return {
                'success': False,
                'message': "Invalid filename. Use alphanumeric, underscores, and hyphens only.",
                'path': None
            }

        destination = self.code_dir if folder == 'Code' else self.files_dir

        # Ensure folder exists
        destination.mkdir(parents=True, exist_ok=True)

        file_path = destination / filename

        # Check if file exists
        if file_path.exists():
            return {
                'success': False,
                'message': f"File '{filename}' already exists in {folder}.",
                'path': str(file_path)
            }

        try:
            # Use default template if no content provided
            if content is None:
                content = self._get_template(filename)

            file_path.write_text(content, encoding='utf-8')
            return {
                'success': True,
                'message': f"File '{filename}' created successfully in {folder}.",
                'path': str(file_path),
                'content': content
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error creating file: {str(e)}",
                'path': str(file_path)
            }
    
    def save_file(self, filename: str, content: str, folder: str = None) -> Dict[str, any]:
        """
        Save/Update content of an existing Python file.
        Alias for update_file to match main.py usage.
        """
        return self.update_file(filename, content, folder)

    def read_file(self, filename: str, folder: str = None) -> Dict[str, any]:
        """
        Read content of a Python file from projects or code directory
        
        Args:
            filename: Name of the file
            folder: 'Projects' or 'Code' to specify which directory
        
        Returns:
            Dict with 'success': bool, 'content': str, 'message': str
        """
        if not filename.endswith('.py'):
            filename += '.py'
        
        # Determine which directory to use
        if folder == 'Code':
            # Check new code directory first (now that files are moved there)
            file_path = self.code_dir / filename
            if not file_path.exists():
                # Fallback to legacy locations
                if filename == 'main.py':
                    file_path = self.project_root / 'main.py'
                elif filename == 'face_detection.py':
                    file_path = self.project_root / 'curriculum' / 'face_detection.py'
        else:
            file_path = self.files_dir / filename
        
        if not file_path.exists():
            return {
                'success': False,
                'content': None,
                'message': f"File '{filename}' not found."
            }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            return {
                'success': True,
                'content': content,
                'message': f"File '{filename}' read successfully."
            }
        except Exception as e:
            return {
                'success': False,
                'content': None,
                'message': f"Error reading file: {str(e)}"
            }
    
    def update_file(self, filename: str, content: str, folder: str = None) -> Dict[str, any]:
        """
        Update content of an existing Python file
        
        Args:
            filename: Name of the file
            content: New file content
            folder: 'Projects' or 'Code' to specify which directory
        
        Returns:
            Dict with 'success': bool, 'message': str
        """
        if not filename.endswith('.py'):
            filename += '.py'
        
        # Determine which directory to use
        if folder == 'Code':
            file_path = self.code_dir / filename
        else:
            file_path = self.files_dir / filename
        
        # If it doesn't exist, we allow creating it as a save operation
        # This handles scratchpad copies of system files (like main.py)
        
        try:
            file_path.write_text(content, encoding='utf-8')
            return {
                'success': True,
                'message': f"File '{filename}' saved successfully."
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error saving file: {str(e)}"
            }
    
    def _is_editable_file(self, filename: str) -> bool:
        """All files in projects/code or projects/ are considered editable."""
        return True
    
    def delete_file(self, filename: str) -> Dict[str, any]:
        """
        Delete a Python file
        
        Args:
            filename: Name of the file
        
        Returns:
            Dict with 'success': bool, 'message': str
        """
        if not filename.endswith('.py'):
            filename += '.py'
        
        file_path = self.files_dir / filename
        
        if not file_path.exists():
            return {
                'success': False,
                'message': f"File '{filename}' not found."
            }
        
        try:
            file_path.unlink()
            return {
                'success': True,
                'message': f"File '{filename}' deleted successfully."
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error deleting file: {str(e)}"
            }
    
    def rename_file(self, old_filename: str, new_filename: str) -> Dict[str, any]:
        """
        Rename a Python file
        
        Args:
            old_filename: Current filename
            new_filename: New filename
        
        Returns:
            Dict with 'success': bool, 'message': str, 'path': str
        """
        if not old_filename.endswith('.py'):
            old_filename += '.py'
        if not new_filename.endswith('.py'):
            new_filename += '.py'
        
        if not self._is_valid_filename(new_filename):
            return {
                'success': False,
                'message': "Invalid filename. Use alphanumeric, underscores, and hyphens only.",
                'path': None
            }
        
        old_path = self.files_dir / old_filename
        new_path = self.files_dir / new_filename
        
        if not old_path.exists():
            return {
                'success': False,
                'message': f"File '{old_filename}' not found.",
                'path': None
            }
        
        if new_path.exists():
            return {
                'success': False,
                'message': f"File '{new_filename}' already exists.",
                'path': str(new_path)
            }
        
        try:
            old_path.rename(new_path)
            return {
                'success': True,
                'message': f"File renamed from '{old_filename}' to '{new_filename}'.",
                'path': str(new_path)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error renaming file: {str(e)}",
                'path': str(new_path)
            }
    
    @staticmethod
    def _is_valid_filename(filename: str) -> bool:
        """
        Validate filename
        
        Args:
            filename: The filename to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Remove .py extension if present
        name = filename.replace('.py', '')
        
        # Check if empty
        if not name:
            return False
        
        # Allow alphanumeric, underscores, hyphens
        import re
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, name))
    
    @staticmethod
    def _get_template(filename: str) -> str:
        """
        Get template content based on filename
        
        Args:
            filename: The filename
        
        Returns:
            Template content as string
        """
        # AI Education Template — concise step-by-step guide for students
        template = '''# ============================================================
# Import Libraries
# ============================================================
import cv2
import numpy as np

# ============================================================
# Setup (runs once)
# ============================================================
# Step 1: Open the camera (Init_Camera)


# Step 2: Load your trained AI model (Load_Engine_Model)


# Step 3: Define the detection class name (CLASSES = ["class1", "class2", "class3"])


print("[OK] Ready! Starting detection loop...")
while True:
    # ========================================================
    # Main Loop (runs every frame)
    # ========================================================
    # Step 4: Get a camera frame (Get_Camera_Frame)


    # Step 5: Run AI detection on frame (Run_Engine_Model)


    # Step 6: Draw boxes on detected objects (Draw_Engine_Detections)


    # Step 7: Show results on Dashboard (Update_Dashboard)


    # [ENDLOOP]


# Shut down camera and close windows (Close_Camera)

'''
        
        return template


# Example usage for testing
if __name__ == "__main__":
    fm = FileManager()
    
    # List all files (projects + code)
    print("\n📁 All Files:")
    for file in fm.list_files():
        folder_icon = "📂" if file['folder'] == 'Projects' else "💻"
        edit_icon = "✏️" if file.get('editable', True) else "👁️"
        print(f"  {folder_icon} {file['folder']}/{file['name']} ({file['size']}) {edit_icon}")
    
    # Test reading main.py
    print("\n📖 Reading main.py...")
    result = fm.read_file("main.py", "Code")
    if result['success']:
        print(f"  First 200 chars: {result['content'][:200]}...")
    
    # Test creating a new project file
    print("\n✏️  Creating new project file...")
    result = fm.create_file("my_project", "print('Hello from my project!')\n")
    print(f"  {result['message']}")
    
    # List again
    print("\n📁 Files after creation:")
    for file in fm.list_files():
        folder_icon = "📂" if file['folder'] == 'Projects' else "💻"
        edit_icon = "✏️" if file.get('editable', True) else "👁️"
        print(f"  {folder_icon} {file['folder']}/{file['name']} ({file['size']}) {edit_icon}")
