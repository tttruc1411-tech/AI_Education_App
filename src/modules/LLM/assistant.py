# AI Code Lab — LLM Assistant (multi-model, Jetson Orin Nano)

from __future__ import annotations
import os
import sys
import re
import threading
from typing import Callable, Optional

from . import model_config as _mcfg
from .prompt_builder import build_prompt, build_fix_prompt, build_explain_prompt


# ── Neutralise llama-cpp-python's broken stdout/stderr redirect ────────────
# On Windows GUI apps (PyQt5), fd 1/2 may not be valid console handles.
# llama-cpp-python's suppress_stdout_stderr (used when verbose=False)
# does os.dup/dup2 on these fds which corrupts them permanently, causing
# hard crashes when llama.cpp's C code writes perf stats during inference.
# Fix: replace it with a no-op at import time, before any Llama() call.

if sys.platform == "win32":
    try:
        import llama_cpp.llama as _llama_mod  # type: ignore

        class _SafeSuppressStdoutStderr:
            """No-op replacement — prevents fd corruption on Windows GUI."""
            def __init__(self, disable=True):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *_):
                pass

        _llama_mod.suppress_stdout_stderr = _SafeSuppressStdoutStderr
    except ImportError:
        pass  # llama_cpp not installed yet — patch will be applied in _load_worker


# ── Post-processing for fix-error responses ────────────────────────────────

_RE_LINE = re.compile(r"(?:Line|Dòng)\s+(\d+)\s*[:：]\s*(.*)", re.IGNORECASE)
_RE_ORIG = re.compile(r"(?:Original|Gốc)\s*[:：]\s*`?(.*?)`?\s*$", re.IGNORECASE | re.MULTILINE)
_RE_FIXED = re.compile(r"(?:Fixed|Sửa)\s*[:：]\s*`?(.*?)`?\s*$", re.IGNORECASE | re.MULTILINE)


def _postprocess_fix(response: str) -> str:
    """Validate and enforce the Line/Original/Fixed (or Dòng/Gốc/Sửa) format."""
    text = response.strip()
    if not text:
        return text

    # Detect language from response
    is_vi = bool(re.search(r"Dòng\s+\d+", text))
    lbl_line = "Dòng" if is_vi else "Line"
    lbl_orig = "Gốc" if is_vi else "Original"
    lbl_fix = "Sửa" if is_vi else "Fixed"

    m_line = _RE_LINE.search(text)
    m_orig = _RE_ORIG.search(text)
    m_fixed = _RE_FIXED.search(text)

    if m_line and m_orig and m_fixed:
        orig_val = m_orig.group(1).strip()
        fixed_val = m_fixed.group(1).strip()
        if orig_val and fixed_val and orig_val != fixed_val:
            line_num = m_line.group(1)
            desc = m_line.group(2).strip()
            return (
                f"{lbl_line} {line_num}: {desc}\n"
                f"{lbl_orig}: {orig_val}\n"
                f"{lbl_fix}: {fixed_val}"
            )

    if m_line:
        line_num = m_line.group(1)
        desc = m_line.group(2).strip() or ("lỗi" if is_vi else "error")
        orig = m_orig.group(1).strip() if m_orig else ""
        fixed = m_fixed.group(1).strip() if m_fixed else ""
        if orig or fixed:
            return (
                f"{lbl_line} {line_num}: {desc}\n"
                f"{lbl_orig}: {orig}\n"
                f"{lbl_fix}: {fixed}"
            )

    return text


class LLMAssistant:
    """
    Wraps llama-cpp-python for on-device LLM inference.
    All blocking work runs in daemon threads — never blocks the PyQt5 UI.

    Each instance has a unique _generation id. When cancel() or unload() is
    called the id increments, causing any in-flight inference to silently stop
    delivering callbacks — no lock contention, no GUI-thread blocking.
    """

    def __init__(self):
        self._llm = None
        self._lock = threading.Lock()
        self._loaded = False
        self._loading = False
        self._gen = 0          # generation counter — incremented on cancel/unload

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def is_loading(self) -> bool:
        return self._loading

    # ── Load ───────────────────────────────────────────────────────────────────

    def load(self,
             on_ready: Optional[Callable] = None,
             on_error: Optional[Callable[[str], None]] = None):
        if self._loaded or self._loading:
            return
        self._loading = True
        threading.Thread(target=self._load_worker,
                         args=(on_ready, on_error), daemon=True).start()

    def _load_worker(self, on_ready, on_error):
        try:
            from llama_cpp import Llama  # type: ignore
            # Re-apply patch in case it wasn't applied at module level
            if sys.platform == "win32":
                try:
                    import llama_cpp.llama as _lm
                    if getattr(_lm.suppress_stdout_stderr, '__name__', '') != '_SafeSuppressStdoutStderr':
                        class _SafeSuppressStdoutStderr:
                            def __init__(self, disable=True): pass
                            def __enter__(self): return self
                            def __exit__(self, *_): pass
                        _lm.suppress_stdout_stderr = _SafeSuppressStdoutStderr
                except Exception:
                    pass
        except ImportError:
            self._loading = False
            if on_error:
                on_error(
                    "llama-cpp-python not installed.\n"
                    "Run:\n  pip install llama-cpp-python \\\n"
                    "    --extra-index-url https://pypi.jetson-ai-lab.io/jp6/cu126"
                )
            return

        cfg = _mcfg.ACTIVE_MODEL
        if not _mcfg.model_exists(cfg):
            self._loading = False
            if on_error:
                on_error(
                    f"Model file not found:\n  {_mcfg.get_model_path(cfg)}\n\n"
                    f"Download from HuggingFace:\n  {cfg['repo']}\n"
                    f"Place the .gguf file in:\n  src/modules/LLM/llm_model/"
                )
            return

        try:
            self._llm = Llama(
                model_path=_mcfg.get_model_path(cfg),
                n_ctx=cfg["context_len"],
                n_gpu_layers=cfg["gpu_layers"],
                n_threads=cfg["threads"],
                use_mmap=True,
                use_mlock=False,
                verbose=False,
            )
            self._loaded = True
            self._loading = False
            if on_ready:
                on_ready()
        except OSError:
            # Safety fallback — if suppress_stdout_stderr patch didn't
            # take effect, the model may still have loaded successfully.
            if self._llm is not None:
                self._loaded = True
                self._loading = False
                if on_ready:
                    on_ready()
            else:
                self._loading = False
                if on_error:
                    on_error("Failed to load model (OS handle error).")
        except Exception as e:
            self._loading = False
            if on_error:
                on_error(f"Failed to load model:\n{e}")

    # ── Inference helpers ──────────────────────────────────────────────────────

    def ask(self,
            question: str,
            editor_code: str = "",
            console_output: str = "",
            lang: str = "en",
            on_token: Optional[Callable[[str], None]] = None,
            on_done: Optional[Callable[[str], None]] = None,
            on_error: Optional[Callable[[str], None]] = None):
        prompt = build_prompt(question, editor_code, console_output, lang=lang)
        self._run(prompt, on_token, on_done, on_error)

    def fix_error(self,
                  error_text: str,
                  editor_code: str,
                  lang: str = "en",
                  on_token: Optional[Callable[[str], None]] = None,
                  on_done: Optional[Callable[[str], None]] = None,
                  on_error: Optional[Callable[[str], None]] = None):
        prompt = build_fix_prompt(error_text, editor_code, lang=lang)

        def _wrapped_done(raw: str):
            processed = _postprocess_fix(raw)
            if on_done:
                on_done(processed)

        self._run(prompt, on_token, _wrapped_done, on_error)

    def explain_code(self,
                     editor_code: str,
                     lang: str = "en",
                     on_token: Optional[Callable[[str], None]] = None,
                     on_done: Optional[Callable[[str], None]] = None,
                     on_error: Optional[Callable[[str], None]] = None):
        prompt = build_explain_prompt(editor_code, lang=lang)
        self._run(prompt, on_token, on_done, on_error)

    def cancel(self):
        """Invalidate any in-flight inference. Non-blocking."""
        self._gen += 1

    # ── Internal ───────────────────────────────────────────────────────────────

    def _run(self, prompt, on_token, on_done, on_error):
        if not self._loaded:
            if on_error:
                on_error("Model not loaded yet — please wait a moment.")
            return
        self._gen += 1  # invalidate any previous inference
        gen = self._gen  # snapshot for this run
        threading.Thread(
            target=self._infer,
            args=(prompt, on_token, on_done, on_error, gen),
            daemon=True,
        ).start()

    def _infer(self, prompt, on_token, on_done, on_error, gen):
        acquired = self._lock.acquire(timeout=5)
        if not acquired or gen != self._gen:
            # Another request or cancel happened — abort silently
            if acquired:
                self._lock.release()
            return
        try:
            llm = self._llm
            if llm is None:
                return
            cfg = _mcfg.ACTIVE_MODEL
            full = ""
            stream = llm(
                prompt,
                max_tokens=cfg["max_tokens"],
                temperature=cfg["temperature"],
                top_p=cfg["top_p"],
                repeat_penalty=cfg["repeat_penalty"],
                stop=cfg["stop"],
                stream=True,
            )
            for chunk in stream:
                if gen != self._gen:
                    break  # cancelled or new request
                token = chunk["choices"][0]["text"]
                full += token
                if on_token:
                    on_token(token)
            if gen == self._gen and on_done:
                on_done(full.strip())
        except Exception as e:
            if gen == self._gen and on_error:
                on_error(f"Inference error: {e}")
        finally:
            self._lock.release()

    def unload(self):
        """Release model from memory. Non-blocking — does NOT wait for inference."""
        self._gen += 1       # invalidate any in-flight inference
        self._loaded = False
        self._loading = False
        # Release the model object — if _infer is running it holds its own
        # local reference (llm) so it won't crash, it just finishes silently.
        self._llm = None
