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
        "context_len": 2048,
        "gpu_layers":  999,           # Full GPU offload via subprocess worker
        "threads":     6,
        "max_tokens":  150,            # Short answers only — was 512, trimmed for concise tutoring
        "temperature": 0.2,
        "top_p":       0.9,
        "repeat_penalty": 1.2,         # Slightly higher to reduce repetitive filler text
        "stop": ["<|im_end|>", "<|endoftext|>", "\n\nStudent:", "\n\nUser:", "\n\n\n"],
    },
    "gemma3": {
        "name":        "Gemma-3-1B-IT",
        "filename":    "gemma-3-1b-it-q4_k_m.gguf",
        "repo":        "bartowski/google_gemma-3-1b-it-GGUF",
        "chat_format": "gemma",        # <start_of_turn>role\n...<end_of_turn>
        "context_len": 4096,           # 1B supports 32K but we cap at 4K for RAM
        "gpu_layers":  999,           # Full GPU offload via subprocess worker
        "threads":     6,
        "max_tokens":  150,            # Short answers only — was 512, trimmed for concise tutoring
        "temperature": 0.2,
        "top_p":       0.9,
        "repeat_penalty": 1.2,         # Slightly higher to reduce repetitive filler text
        "stop": ["<end_of_turn>", "<eos>", "\n\nStudent:", "\n\nUser:", "\n\n\n"],
    },
}

# Convenience aliases (used by tests and legacy code)
QWEN_MODEL = MODEL_REGISTRY["qwen"]
GEMMA3_MODEL = MODEL_REGISTRY["gemma3"]

# ── Default active model ───────────────────────────────────────────────────
# Qwen is the production default (best for code). Gemma is lighter.
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
