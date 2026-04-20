# AI Code Lab — LLM Assistant (multi-model, Jetson Orin Nano)
# Uses a subprocess worker for GPU inference so CUDA CMA is not
# shared with PyTorch/YOLO in the main app process.

from __future__ import annotations
import os
import sys
import re
import json
import subprocess
import threading
from typing import Callable, Optional

from . import model_config as _mcfg
from .prompt_builder import build_prompt, build_fix_prompt, build_explain_prompt


# ── Path to the worker script ─────────────────────────────────────────────
_WORKER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "llm_worker.py")


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
    Manages LLM inference via a subprocess worker that runs on GPU.
    The worker process is isolated from PyTorch/YOLO CUDA allocations.

    Each instance has a unique _generation id. When cancel() or unload() is
    called the id increments, causing any in-flight inference to silently stop
    delivering callbacks — no lock contention, no GUI-thread blocking.
    """

    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None
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
            # Launch worker subprocess with GPU access
            self._proc = subprocess.Popen(
                [sys.executable, _WORKER_SCRIPT],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # line-buffered
            )

            # Send load command
            load_cmd = json.dumps({
                "action": "load",
                "model_path": _mcfg.get_model_path(cfg),
                "config": {
                    "context_len": cfg["context_len"],
                    "gpu_layers": cfg["gpu_layers"],
                    "threads": cfg["threads"],
                    "max_tokens": cfg["max_tokens"],
                    "temperature": cfg["temperature"],
                    "top_p": cfg["top_p"],
                    "repeat_penalty": cfg["repeat_penalty"],
                    "stop": cfg["stop"],
                },
            })
            self._proc.stdin.write(load_cmd + "\n")
            self._proc.stdin.flush()

            # Wait for response
            response = self._proc.stdout.readline().strip()
            if response.startswith("STATUS:ready"):
                self._loaded = True
                self._loading = False
                if on_ready:
                    on_ready()
            else:
                self._loading = False
                self._kill_proc()
                err_msg = response.replace("STATUS:error:", "") if response.startswith("STATUS:error:") else response
                if on_error:
                    on_error(f"Failed to load model:\n{err_msg}")

        except Exception as e:
            self._loading = False
            self._kill_proc()
            if on_error:
                on_error(f"Failed to start LLM worker:\n{e}")

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
            if acquired:
                self._lock.release()
            return
        try:
            proc = self._proc
            if proc is None or proc.poll() is not None:
                if on_error:
                    on_error("LLM worker process died unexpectedly.")
                return

            # Send inference command
            infer_cmd = json.dumps({"action": "infer", "prompt": prompt})
            proc.stdin.write(infer_cmd + "\n")
            proc.stdin.flush()

            # Read streaming tokens
            full = ""
            while True:
                if gen != self._gen:
                    break  # cancelled or new request
                line = proc.stdout.readline()
                if not line:
                    break  # process died
                line = line.rstrip("\n")
                if line.startswith("TOKEN:"):
                    token = line[6:]
                    full += token
                    if on_token:
                        on_token(token)
                elif line == "STATUS:done":
                    break
                elif line.startswith("STATUS:error:"):
                    if gen == self._gen and on_error:
                        on_error(f"Inference error: {line[13:]}")
                    return

            if gen == self._gen and on_done:
                on_done(full.strip())
        except Exception as e:
            if gen == self._gen and on_error:
                on_error(f"Inference error: {e}")
        finally:
            self._lock.release()

    def _kill_proc(self):
        """Kill the worker subprocess if running."""
        if self._proc is not None:
            try:
                self._proc.stdin.write(json.dumps({"action": "quit"}) + "\n")
                self._proc.stdin.flush()
                self._proc.wait(timeout=3)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            self._proc = None

    def unload(self):
        """Release model and GPU memory by terminating the worker process."""
        self._gen += 1       # invalidate any in-flight inference
        self._loaded = False
        self._loading = False
        self._kill_proc()
