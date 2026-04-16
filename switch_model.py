"""
Quick model switcher for AI Code Lab's LLM Assistant.
Usage:
    python switch_model.py          # Show current model + available models
    python switch_model.py qwen     # Switch to Qwen2.5-Coder-1.5B (default)
    python switch_model.py phi3     # Switch to Phi-3-mini-4k-instruct
"""
import sys
import os

CONFIG_PATH = os.path.join("src", "modules", "LLM", "model_config.py")

MODELS = {
    "qwen": 'ACTIVE_MODEL = QWEN_MODEL',
    "phi3": 'ACTIVE_MODEL = PHI3_MODEL',
}

DESCRIPTIONS = {
    "qwen": "Qwen2.5-Coder-1.5B  (~1.12 GB, fast, production default)",
    "phi3": "Phi-3-mini-4k        (~2.39 GB, slower, better reasoning, dev only)",
}

def get_current():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("ACTIVE_MODEL") and "=" in stripped and not stripped.startswith("#"):
                if "PHI3_MODEL" in stripped:
                    return "phi3"
                return "qwen"
    return "qwen"

def switch_to(key):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace the ACTIVE_MODEL assignment line
    import re
    content = re.sub(
        r'^ACTIVE_MODEL\s*=\s*\w+',
        MODELS[key],
        content,
        count=1,
        flags=re.MULTILINE,
    )
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    current = get_current()

    if len(sys.argv) < 2:
        print(f"Current: {current} — {DESCRIPTIONS[current]}")
        print(f"\nAvailable models:")
        for k, desc in DESCRIPTIONS.items():
            marker = " (active)" if k == current else ""
            print(f"  {k:6s} {desc}{marker}")
        print(f"\nUsage: python switch_model.py [qwen|phi3]")
        sys.exit(0)

    choice = sys.argv[1].lower().strip()
    if choice not in MODELS:
        print(f"Unknown model: {choice}. Options: {', '.join(MODELS.keys())}")
        sys.exit(1)

    if choice == current:
        print(f"Already set to {choice}.")
        sys.exit(0)

    switch_to(choice)
    print(f"Switched to: {choice} — {DESCRIPTIONS[choice]}")
    print(f"Restart the app for the change to take effect.")
