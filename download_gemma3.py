"""Download Gemma-3-1B-IT Q4_K_M GGUF from HuggingFace (bartowski quantization)."""
import os
import sys
import urllib.request

URL = (
    "https://huggingface.co/bartowski/google_gemma-3-1b-it-GGUF"
    "/resolve/main/google_gemma-3-1b-it-Q4_K_M.gguf"
)
DEST = os.path.join("src", "modules", "LLM", "llm_model", "gemma-3-1b-it-q4_k_m.gguf")

os.makedirs(os.path.dirname(DEST), exist_ok=True)

if os.path.isfile(DEST):
    size_mb = os.path.getsize(DEST) / (1024**2)
    print(f"File already exists: {DEST} ({size_mb:.0f} MB)")
    sys.exit(0)

print(f"Downloading Gemma-3-1B-IT Q4_K_M GGUF (~810 MB)...")
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
