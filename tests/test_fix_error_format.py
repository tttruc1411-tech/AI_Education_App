"""
Bug Condition Exploration Test — Fix Error Output Format Non-Compliance

These tests encode the EXPECTED behavior (what we want AFTER the fix).
They are EXPECTED TO FAIL on the current unfixed code, which proves the bug exists.

Validates: Requirements 1.1, 1.2, 1.3, 1.4
"""

import inspect
import re
import sys
import os

import pytest

# Ensure the project root is on sys.path so imports resolve
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.modules.LLM.prompt_builder import build_fix_prompt, SYSTEM_PROMPT
from src.modules.LLM import assistant as assistant_module


class TestBugConditionExploration:
    """
    Bug condition exploration: these tests assert the EXPECTED (fixed) behavior.
    On unfixed code they MUST FAIL — failure confirms the bug exists.
    """

    # ── 1. build_fix_prompt() should use a dedicated FIX_SYSTEM_PROMPT ─────

    def test_build_fix_prompt_uses_dedicated_fix_system_prompt(self):
        """
        **Validates: Requirements 1.2**

        After the fix, build_fix_prompt() should use a dedicated FIX_SYSTEM_PROMPT
        that is different from the generic SYSTEM_PROMPT.
        On unfixed code this FAILS because build_fix_prompt() uses the generic SYSTEM_PROMPT.
        """
        from src.modules.LLM import prompt_builder

        # The module should export a FIX_SYSTEM_PROMPT constant
        assert hasattr(prompt_builder, "FIX_SYSTEM_PROMPT"), (
            "prompt_builder module should have a FIX_SYSTEM_PROMPT constant"
        )

        fix_system_prompt = prompt_builder.FIX_SYSTEM_PROMPT

        # FIX_SYSTEM_PROMPT must be different from the generic SYSTEM_PROMPT
        assert fix_system_prompt != SYSTEM_PROMPT, (
            "FIX_SYSTEM_PROMPT should differ from the generic SYSTEM_PROMPT"
        )

        # build_fix_prompt output should contain FIX_SYSTEM_PROMPT, not SYSTEM_PROMPT
        prompt_output = build_fix_prompt("SyntaxError: unexpected EOF", "print('hello'")
        assert fix_system_prompt in prompt_output, (
            "build_fix_prompt() output should contain FIX_SYSTEM_PROMPT"
        )
        assert SYSTEM_PROMPT not in prompt_output, (
            "build_fix_prompt() output should NOT contain the generic SYSTEM_PROMPT"
        )

    # ── 2. build_fix_prompt() should contain a few-shot example ────────────

    def test_build_fix_prompt_contains_few_shot_example(self):
        """
        **Validates: Requirements 1.3**

        After the fix, build_fix_prompt() should include at least one few-shot
        example demonstrating the correct Line/Original/Fixed format.
        On unfixed code this FAILS because no few-shot example exists.
        """
        prompt_output = build_fix_prompt(
            "SyntaxError: unexpected EOF while parsing",
            "x = int(input('Enter a number'"
        )

        # The prompt should contain a few-shot example with the expected format
        assert re.search(r"Line \d+:", prompt_output), (
            "build_fix_prompt() output should contain a few-shot example with 'Line N:' pattern"
        )
        assert "Original:" in prompt_output, (
            "build_fix_prompt() output should contain a few-shot example with 'Original:' line"
        )
        assert "Fixed:" in prompt_output, (
            "build_fix_prompt() output should contain a few-shot example with 'Fixed:' line"
        )

    # ── 3. assistant.py should have a _postprocess_fix function ────────────

    def test_assistant_has_postprocess_fix_function(self):
        """
        **Validates: Requirements 1.4**

        After the fix, assistant.py should contain a _postprocess_fix() function
        that validates and reformats LLM responses.
        On unfixed code this FAILS because no such function exists.
        """
        assert hasattr(assistant_module, "_postprocess_fix"), (
            "assistant module should have a _postprocess_fix function"
        )
        assert callable(getattr(assistant_module, "_postprocess_fix", None)), (
            "_postprocess_fix should be callable"
        )

    # ── 4. fix_error() should wrap on_done with post-processing ────────────

    def test_fix_error_wraps_on_done_with_postprocessing(self):
        """
        **Validates: Requirements 1.4**

        After the fix, fix_error() should NOT pass on_done directly to _run().
        Instead it should wrap on_done with _postprocess_fix logic.
        On unfixed code this FAILS because fix_error passes on_done directly.
        """
        source = inspect.getsource(assistant_module.LLMAssistant.fix_error)

        # The fix_error method should reference _postprocess_fix or wrap on_done
        assert "_postprocess_fix" in source or "wrapped" in source.lower(), (
            "fix_error() should wrap on_done with post-processing logic "
            "(references _postprocess_fix or a wrapper)"
        )

        # It should NOT simply pass on_done directly to self._run
        # After the fix, the on_done argument to _run should be wrapped
        # We check that the source doesn't just do a plain pass-through
        lines = [l.strip() for l in source.splitlines()]
        direct_passthrough = any(
            "self._run(prompt, on_token, on_done, on_error)" in l
            for l in lines
        )
        assert not direct_passthrough, (
            "fix_error() should NOT pass on_done directly to _run(); "
            "it should wrap on_done with post-processing"
        )
