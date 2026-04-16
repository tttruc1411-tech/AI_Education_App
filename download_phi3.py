"""Download Phi-3-mini-4k-instruct Q4 GGUF from HuggingFace CDN."""
import os
import sys
import urllib.request

URL = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
DEST = os.path.join("src", "modules", "LLM", "llm_model", "Phi-3-mini-4k-instruct-q4.gguf")

os.makedirs(os.path.dirname(DEST), exist_ok=True)

if os.path.isfile(DEST):
    size_gb = os.path.getsize(DEST) / (1024**3)
    print(f"File already exists: {DEST} ({size_gb:.2f} GB)")
    sys.exit(0)

print(f"Downloading Phi-3-mini-4k-instruct-q4.gguf (~2.39 GB)...")
print(f"From: {URL}")
print(f"To:   {DEST}")

def progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    pct = downloaded / total_size * 100 if total_size > 0 else 0
    mb = downloaded / (1024**2)
    total_mb = total_size / (1024**2)
    sys.stdout.write(f"\r  {pct:.1f}% ({mb:.0f}/{total_mb:.0f} MB)")
    sys.stdout.flush()

try:
    urllib.request.urlretrieve(URL, DEST, reporthook=progress)
    print(f"\nDone! Saved to {DEST}")
except Exception as e:
    print(f"\nDownload failed: {e}")
    if os.path.isfile(DEST):
        os.remove(DEST)
    sys.exit(1)
