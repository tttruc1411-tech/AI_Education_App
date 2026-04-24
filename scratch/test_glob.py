import os
from pathlib import Path

project_root = Path(r"e:\KDI\AI_Education_App")
files_dir = project_root / "projects"
code_dir = files_dir / "code"
data_dir = files_dir / "data"
model_dir = files_dir / "model"

print(f"Code Dir: {code_dir}, Exists: {code_dir.exists()}")
print(f"Data Dir: {data_dir}, Exists: {data_dir.exists()}")
print(f"Model Dir: {model_dir}, Exists: {model_dir.exists()}")

counts = {
    "Code": len(list(code_dir.glob("*"))),
    "Data": len(list(data_dir.glob("*"))),
    "Model": len(list(model_dir.glob("*")))
}

print(f"Counts: {counts}")

for item in data_dir.glob("*"):
    print(f"Data item: {item.name} (is_dir: {item.is_dir()})")
