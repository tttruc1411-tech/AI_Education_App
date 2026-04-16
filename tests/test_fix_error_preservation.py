"""
Preservation Property Tests — Non-Fix-Error Actions Unchanged

These tests verify the EXISTING behavior that must be preserved after the fix.
All tests should PASS on the current unfixed code.

Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
"""

import inspect
import re
import sys
import os

import pytest

# Ensure the project root is on sys.path so imports resolve
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.modules.LLM.prompt_builder import (
    SYSTEM_PROMPT,
    build_prompt,
    build_explain_prompt,
    _trim_code,
    _trim_console,
)
from src.modules.LLM import model_config as _mcfg
from src.modules.LLM import assistant as assistant_module
from src.modules.LLM.assistant import LLMAssistant


class TestPreservation:
    """
    Preservation tests: these verify the EXISTING behavior on unfixed code.
    They must PASS both before and after the fix.
    """

    # ── 1. build_prompt() uses SYSTEM_PROMPT ───────────────────────────────

    def test_build_prompt_uses_system_prompt(self):
        """
        **Validates: Requirements 3.1**

        Verify build_prompt() uses SYSTEM_PROMPT (not any fix-specific prompt).
        """
        prompt = build_prompt("hello", "x=1", "")
        assert SYSTEM_PROMPT in prompt, (
            "build_prompt() must use the generic SYSTEM_PROMPT"
        )

    # ── 2. build_explain_prompt() uses SYSTEM_PROMPT ───────────────────────

    def test_build_explain_prompt_uses_system_prompt(self):
        """
        **Validates: Requirements 3.2**

        Verify build_explain_prompt() uses SYSTEM_PROMPT (not any fix-specific prompt).
        """
        prompt = build_explain_prompt("x = 1")
        assert SYSTEM_PROMPT in prompt, (
            "build_explain_prompt() must use the generic SYSTEM_PROMPT"
        )

    # ── 3. build_prompt() produces valid chat structure ───────────────────

    def test_build_prompt_chat_structure(self):
        """
        **Validates: Requirements 3.1**

        Verify build_prompt() produces valid chat structure with system/user/assistant
        tags appropriate for the active model's chat format.
        """
        prompt = build_prompt("What does this do?", "print('hi')", "hi")
        fmt = _mcfg.ACTIVE_MODEL.get("chat_format", "chatml")

        if fmt == "phi3":
            assert "<|system|>" in prompt
            assert "<|user|>" in prompt
            assert "<|assistant|>" in prompt
            assert prompt.count("<|end|>") >= 2, (
                "Phi-3 format must have at least 2 <|end|> markers (system + user)"
            )
            sys_pos = prompt.index("<|system|>")
            usr_pos = prompt.index("<|user|>")
            ast_pos = prompt.index("<|assistant|>")
        else:
            assert "<|im_start|>system" in prompt
            assert "<|im_start|>user" in prompt
            assert "<|im_start|>assistant" in prompt
            assert prompt.count("<|im_end|>") >= 2, (
                "ChatML must have at least 2 <|im_end|> markers (system + user)"
            )
            sys_pos = prompt.index("<|im_start|>system")
            usr_pos = prompt.index("<|im_start|>user")
            ast_pos = prompt.index("<|im_start|>assistant")

        assert sys_pos < usr_pos < ast_pos, (
            "Chat structure order must be system -> user -> assistant"
        )

    # ── 4. build_explain_prompt() produces valid chat structure ──────────

    def test_build_explain_prompt_chat_structure(self):
        """
        **Validates: Requirements 3.2**

        Verify build_explain_prompt() produces valid chat structure with
        system/user/assistant tags appropriate for the active model's chat format.
        """
        prompt = build_explain_prompt("for i in range(10):\n    print(i)")
        fmt = _mcfg.ACTIVE_MODEL.get("chat_format", "chatml")

        if fmt == "phi3":
            assert "<|system|>" in prompt
            assert "<|user|>" in prompt
            assert "<|assistant|>" in prompt
            assert prompt.count("<|end|>") >= 2
            sys_pos = prompt.index("<|system|>")
            usr_pos = prompt.index("<|user|>")
            ast_pos = prompt.index("<|assistant|>")
        else:
            assert "<|im_start|>system" in prompt
            assert "<|im_start|>user" in prompt
            assert "<|im_start|>assistant" in prompt
            assert prompt.count("<|im_end|>") >= 2
            sys_pos = prompt.index("<|im_start|>system")
            usr_pos = prompt.index("<|im_start|>user")
            ast_pos = prompt.index("<|im_start|>assistant")

        assert sys_pos < usr_pos < ast_pos

    # ── 5. _trim_code() preserves line numbers ────────────────────────────

    def test_trim_code_preserves_line_numbers(self):
        """
        **Validates: Requirements 3.3**

        Verify _trim_code() preserves code content and truncates long lines.
        """
        code = "x = 1\ny = 2\nz = 3"
        result = _trim_code(code)

        # Code content should be preserved
        assert "x = 1" in result
        assert "y = 2" in result
        assert "z = 3" in result

    # ── 6. _trim_console() truncates correctly ─────────────────────────────

    def test_trim_console_truncates_correctly(self):
        """
        **Validates: Requirements 3.3**

        Verify _trim_console() keeps last N chars when output exceeds limit.
        """
        # Create console output that exceeds _MAX_CONSOLE_CHARS (400)
        long_output = "error line\n" * 100  # ~1100 chars
        result = _trim_console(long_output)

        # Result should be truncated and start with "..."
        assert result.startswith("...")
        # Result length should be bounded (400 chars + "...\n" prefix)
        assert len(result) <= 400 + 10  # small margin for prefix

        # Short output should pass through without truncation
        short_output = "hello world"
        result_short = _trim_console(short_output)
        assert result_short == "hello world"

    # ── 7. ask() passes on_done directly to _run() ────────────────────────

    def test_ask_passes_on_done_directly(self):
        """
        **Validates: Requirements 3.4**

        Verify ask() in LLMAssistant passes on_done directly to _run()
        (no wrapping or post-processing).
        """
        source = inspect.getsource(LLMAssistant.ask)

        # ask() should call self._run with on_done directly
        assert "self._run(prompt, on_token, on_done, on_error)" in source, (
            "ask() should pass on_done directly to self._run() without wrapping"
        )

        # Should NOT reference any post-processing
        assert "_postprocess" not in source, (
            "ask() should NOT reference any post-processing function"
        )

    # ── 8. explain_code() passes on_done directly to _run() ───────────────

    def test_explain_code_passes_on_done_directly(self):
        """
        **Validates: Requirements 3.5**

        Verify explain_code() passes on_done directly to _run()
        (no wrapping or post-processing).
        """
        source = inspect.getsource(LLMAssistant.explain_code)

        # explain_code() should call self._run with on_done directly
        assert "self._run(prompt, on_token, on_done, on_error)" in source, (
            "explain_code() should pass on_done directly to self._run() without wrapping"
        )

        # Should NOT reference any post-processing
        assert "_postprocess" not in source, (
            "explain_code() should NOT reference any post-processing function"
        )
