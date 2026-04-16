# LLM Model Comparison — Jetson Orin Nano (8GB)

## Hardware Constraints

| Spec | Value |
|------|-------|
| Device | NVIDIA Jetson Orin Nano |
| Unified RAM (CPU + GPU shared) | 8 GB |
| GPU | 1024 CUDA cores, 32 Tensor cores |
| CPU | 6-core ARM Cortex-A78AE |
| Memory Bandwidth | ~102 GB/s |
| OS | JetPack 6.x / Ubuntu 22.04 |
| Python | 3.10 |

> ⚠️ The app already uses ~1.5–2 GB RAM for PyQt5 UI + OpenCV + YOLO inference.
> This leaves roughly **5.5–6 GB** available for the LLM at runtime.

---

## Model Comparison Table

| Model | Params | Quant | RAM Usage | Tokens/sec (Orin Nano) | Code Quality | Multilingual (VI) | License | Verdict |
|-------|--------|-------|-----------|------------------------|--------------|-------------------|---------|---------|
| **Qwen2.5-Coder-1.5B-Instruct** | 1.5B | Q4_K_M | ~1.2 GB | ~35–45 tok/s | ⭐⭐⭐⭐ | ✅ Good | Apache 2.0 | ✅ **Best fit** |
| **Qwen2.5-Coder-3B-Instruct** | 3B | Q4_K_M | ~2.2 GB | ~25–35 tok/s | ⭐⭐⭐⭐⭐ | ✅ Good | Apache 2.0 | ✅ Strong choice |
| **Gemma 3 1B-Instruct** | 1B | Q4_K_M | ~0.9 GB | ~40–55 tok/s | ⭐⭐⭐ | ⚠️ Limited | Gemma ToS | ⚠️ Fast but weak code |
| **Phi-3 Mini 3.8B** | 3.8B | Q4_K_M | ~2.8 GB | ~18–25 tok/s | ⭐⭐⭐⭐ | ⚠️ Limited | MIT | ⚠️ Slower on Orin |
| **Llama 3.2 1B-Instruct** | 1B | Q4_K_M | ~0.9 GB | ~40–50 tok/s | ⭐⭐⭐ | ⚠️ Limited | Llama 3.2 | ⚠️ Weak code assist |
| **Llama 3.2 3B-Instruct** | 3B | Q4_K_M | ~2.2 GB | ~22–30 tok/s | ⭐⭐⭐ | ⚠️ Limited | Llama 3.2 | ⚠️ OK general, weak code |
| **TinyLlama 1.1B** | 1.1B | Q4_K_M | ~0.8 GB | ~50–60 tok/s | ⭐⭐ | ❌ Poor | Apache 2.0 | ❌ Too weak for code |
| **Qwen2.5-1.5B-Instruct** | 1.5B | Q4_K_M | ~1.2 GB | ~35–45 tok/s | ⭐⭐⭐ | ✅ Good | Apache 2.0 | ⚠️ General, not code-tuned |
| **DeepSeek-Coder-1.3B** | 1.3B | Q4_K_M | ~1.0 GB | ~35–45 tok/s | ⭐⭐⭐⭐ | ⚠️ Limited | MIT | ⚠️ Good code, no VI |
| **Phi-3.5 Mini 3.8B** | 3.8B | Q4_0 | ~2.5 GB | ~20–28 tok/s | ⭐⭐⭐⭐ | ⚠️ Limited | MIT | ⚠️ Slower, good quality |

---

## Recommendation

### 🥇 Primary: `Qwen2.5-Coder-1.5B-Instruct` (Q4_K_M GGUF)

```
Model: Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF
File:  qwen2.5-coder-1.5b-instruct-q4_k_m.gguf
RAM:   ~1.2 GB
Speed: ~35–45 tokens/sec on Orin Nano
```

**Why:**
- Specifically fine-tuned for code generation and explanation — perfect for a coding education app
- Leaves ~4+ GB free for the rest of the app (YOLO, PyQt5, OpenCV)
- Vietnamese language support (Qwen family trained on multilingual data)
- Apache 2.0 license — no restrictions
- Fast enough for conversational use (~35 tok/s feels real-time)
- Available in GGUF format, runs via `llama-cpp-python` with GPU offload on Jetson

### 🥈 Fallback: `Qwen2.5-Coder-3B-Instruct` (Q4_K_M GGUF)

```
Model: Qwen/Qwen2.5-Coder-3B-Instruct-GGUF
File:  qwen2.5-coder-3b-instruct-q4_k_m.gguf
RAM:   ~2.2 GB
Speed: ~25–35 tokens/sec on Orin Nano
```

**Why:** Noticeably better code quality and reasoning. Use this if the app is running standalone (no YOLO inference active simultaneously).

---

## Memory Budget at Runtime

```
App baseline (PyQt5 + OpenCV + YOLO idle):  ~1.5 GB
Qwen2.5-Coder-1.5B Q4_K_M:                 ~1.2 GB
─────────────────────────────────────────────────────
Total used:                                 ~2.7 GB
Remaining headroom:                         ~5.3 GB ✅

App baseline + YOLO active inference:       ~3.0 GB
Qwen2.5-Coder-1.5B Q4_K_M:                 ~1.2 GB
─────────────────────────────────────────────────────
Total used:                                 ~4.2 GB
Remaining headroom:                         ~3.8 GB ✅
```

---

## Inference Backend Options

| Backend | Pros | Cons | Recommended? |
|---------|------|------|--------------|
| **llama-cpp-python** | Pure Python, GPU offload, GGUF native, easy pip install | Slightly lower throughput than vLLM | ✅ Yes — simplest integration |
| **Ollama** | Easy model management, REST API | Extra process overhead, Docker preferred | ✅ Good for prototyping |
| **vLLM (Jetson container)** | Best throughput, production-grade | Docker required, complex setup | ⚠️ Overkill for this use case |
| **HuggingFace Transformers** | Flexible, familiar API | High RAM overhead, no GGUF support | ❌ Too heavy for 8GB |

**Decision: `llama-cpp-python` with GPU offload layers**

```bash
pip install llama-cpp-python \
  --extra-index-url https://pypi.jetson-ai-lab.io/jp6/cu126
```

This gives direct Python API access, GGUF model support, and CUDA GPU layer offloading — all without Docker or a separate server process.

---

## Planned Module Structure

```
src/modules/LLM/
├── __init__.py
├── MODEL_COMPARISON.md       ← this file
├── assistant.py              ← main LLM interface class
├── prompt_builder.py         ← context-aware prompt construction
└── model_config.py           ← model paths, parameters, defaults
```

## Context Strategy for Code Assistant

The assistant will receive:
1. **System prompt** — role definition (Python/AI tutor for students)
2. **Current editor code** — full content of `monacoPlaceholder`
3. **User question** — typed in the chat panel
4. **App context** — which curriculum lesson is loaded (optional)

This keeps prompts focused and avoids hitting the model's context limit (~4K tokens for 1.5B Q4).
