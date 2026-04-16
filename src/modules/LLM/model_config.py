# LLM Model Configuration — Multi-model support for Jetson Orin Nano

import os

MODELS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "llm_model"
)

# ── Model Registry ─────────────────────────────────────────────────────────

MODEL_REGISTRY = {
    "qwen": {
        "name":        "Qwen2.5-Coder-1.5B-Instruct",
        "filename":    "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "repo":        "Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF",
        "chat_format": "chatml",       # <|im_start|>role\n...<|im_end|>
        "context_len": 4096,
        "gpu_layers":  999,
        "threads":     6,
        "max_tokens":  512,
        "temperature": 0.2,
        "top_p":       0.9,
        "repeat_penalty": 1.1,
        "stop": ["<|im_end|>", "<|endoftext|>", "\n\nStudent:", "\n\nUser:"],
    },
    "phi3": {
        "name":        "Phi-3-mini-4k-instruct",
        "filename":    "Phi-3-mini-4k-instruct-q4.gguf",
        "repo":        "microsoft/Phi-3-mini-4k-instruct-gguf",
        "chat_format": "phi3",         # <|user|>\n...<|end|>\n<|assistant|>
        "context_len": 4096,
        "gpu_layers":  999,
        "threads":     6,
        "max_tokens":  512,
        "temperature": 0.2,
        "top_p":       0.9,
        "repeat_penalty": 1.1,
        "stop": ["<|end|>", "<|endoftext|>", "<|user|>", "\n\nStudent:", "\n\nUser:"],
    },
    "gemma3": {
        "name":        "Gemma-3-1B-IT",
        "filename":    "gemma-3-1b-it-q4_k_m.gguf",
        "repo":        "bartowski/google_gemma-3-1b-it-GGUF",
        "chat_format": "gemma",        # <start_of_turn>role\n...<end_of_turn>
        "context_len": 4096,           # 1B supports 32K but we cap at 4K for RAM
        "gpu_layers":  999,
        "threads":     6,
        "max_tokens":  512,
        "temperature": 0.2,
        "top_p":       0.9,
        "repeat_penalty": 1.1,
        "stop": ["<end_of_turn>", "<eos>", "\n\nStudent:", "\n\nUser:"],
    },
}

# Convenience aliases (used by tests and legacy code)
QWEN_MODEL = MODEL_REGISTRY["qwen"]
PHI3_MODEL = MODEL_REGISTRY["phi3"]
GEMMA3_MODEL = MODEL_REGISTRY["gemma3"]

# ── Default active model ───────────────────────────────────────────────────
# Qwen is the production default. Phi-3 is available for dev testing.
ACTIVE_MODEL = QWEN_MODEL


def get_model_path(config: dict) -> str:
    return os.path.join(MODELS_DIR, config["filename"])


def model_exists(config: dict) -> bool:
    return os.path.isfile(get_model_path(config))


def set_active_model(key: str):
    """Switch the active model at runtime. key must be in MODEL_REGISTRY."""
    global ACTIVE_MODEL
    if key not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model key '{key}'. Available: {list(MODEL_REGISTRY.keys())}")
    ACTIVE_MODEL = MODEL_REGISTRY[key]
    return ACTIVE_MODEL


def get_available_models():
    """Return list of (key, name, exists) for all registered models."""
    return [
        (key, cfg["name"], model_exists(cfg))
        for key, cfg in MODEL_REGISTRY.items()
    ]
