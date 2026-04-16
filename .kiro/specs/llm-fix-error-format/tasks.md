# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Fix Error Output Format Non-Compliance
  - **CRITICAL**: This test MUST FAIL on unfixed code — failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior — it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the model does not follow the `Line N: / Original: / Fixed:` format
  - **Scoped PBT Approach**: Scope the property to concrete failing cases — call `build_fix_prompt()` with known error/code pairs, then validate the prompt structure and simulate format checking on representative LLM outputs
  - Test that `build_fix_prompt()` currently uses the generic `SYSTEM_PROMPT` (not a dedicated fix system prompt)
  - Test that `build_fix_prompt()` output contains NO few-shot example
  - Test that `fix_error()` passes `on_done` directly without any post-processing wrapper
  - For format validation: assert that a response matching `Line \d+:.*`, `Original:.*`, `Fixed:.*` with non-identical Original/Fixed is the expected behavior (from `isBugCondition` in design)
  - Property: for any `(error_text, editor_code)` input, `build_fix_prompt()` should produce a prompt with a dedicated `FIX_SYSTEM_PROMPT` and a few-shot example — this will FAIL on unfixed code
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct — it proves the bug exists: generic system prompt, no few-shot, no post-processing)
  - Document counterexamples found (e.g., "build_fix_prompt uses SYSTEM_PROMPT instead of FIX_SYSTEM_PROMPT", "no few-shot example in prompt", "fix_error has no post-processing")
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Non-Fix-Error Actions Unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - Observe: `build_prompt("hello", "x=1", "")` produces ChatML with `SYSTEM_PROMPT` on unfixed code
  - Observe: `build_explain_prompt("x=1")` produces ChatML with `SYSTEM_PROMPT` on unfixed code
  - Observe: `_trim_code()` and `_trim_console()` produce identical output on unfixed code
  - Observe: `ask()` and `explain_code()` in `assistant.py` call `_run()` without any callback wrapping on unfixed code
  - Write property-based test: for all `(user_question, editor_code, console_output)` string inputs, `build_prompt()` output is identical before and after the fix (uses `SYSTEM_PROMPT`, same ChatML structure)
  - Write property-based test: for all `editor_code` string inputs, `build_explain_prompt()` output is identical before and after the fix (uses `SYSTEM_PROMPT`, same ChatML structure)
  - Write property-based test: for all string inputs, `_trim_code()` and `_trim_console()` produce identical output before and after the fix
  - Write unit test: verify `ask()` and `explain_code()` do NOT wrap `on_done` with any post-processing (only `fix_error` should)
  - Verify tests PASS on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Implement the fix for LLM fix-error format non-compliance

  - [x] 3.1 Add dedicated `FIX_SYSTEM_PROMPT` and few-shot example in `prompt_builder.py`
    - Create `FIX_SYSTEM_PROMPT` constant: a system prompt specifically tailored for the fix-error action that reinforces the exact `Line X: / Original: / Fixed:` output format
    - Update `build_fix_prompt()` to use `FIX_SYSTEM_PROMPT` instead of `SYSTEM_PROMPT`
    - Add one concrete few-shot example in the user prompt showing an input error + code and the correctly formatted 3-line output
    - Tighten format instructions to be more directive for the 1.5B model
    - Do NOT modify `build_prompt()` or `build_explain_prompt()` — they must continue using `SYSTEM_PROMPT`
    - Do NOT modify `_trim_code()` or `_trim_console()`
    - _Bug_Condition: isBugCondition(input) where build_fix_prompt uses generic SYSTEM_PROMPT and no few-shot example_
    - _Expected_Behavior: build_fix_prompt uses FIX_SYSTEM_PROMPT and includes a few-shot example in the user prompt_
    - _Preservation: build_prompt() and build_explain_prompt() continue using SYSTEM_PROMPT unchanged_
    - _Requirements: 1.2, 1.3, 2.2, 2.3_

  - [x] 3.2 Add `_postprocess_fix()` and wrap `on_done` in `assistant.py`
    - Add `_postprocess_fix(response: str) -> str` function that:
      - Checks if response matches `Line \d+:` / `Original:` / `Fixed:` pattern
      - If matched, validates Original and Fixed are NOT identical (no-op fix detection); if identical, treats as format deviation
      - If not matched, attempts regex extraction of line number, error description, original line, and fixed line from unstructured text
      - If extraction succeeds, reformats into the correct `Line N: / Original: / Fixed:` structure
      - If extraction fails, returns the raw response as graceful fallback
    - In `fix_error()`, wrap the caller's `on_done` callback so `_postprocess_fix()` is applied before forwarding
    - The wrapped callback should also call `set_text()` on the streaming bubble to replace raw streamed content with the post-processed version
    - Do NOT modify `_infer()` — it must remain generic for all action types
    - Do NOT modify `ask()` or `explain_code()` — they must NOT have any post-processing
    - Do NOT modify streaming mechanism or `on_token` behavior
    - _Bug_Condition: isBugCondition(input) where LLM response deviates from format and no post-processing exists_
    - _Expected_Behavior: _postprocess_fix validates and reformats the response; fix_error wraps on_done with post-processing_
    - _Preservation: ask() and explain_code() pass on_done directly without wrapping; _infer() unchanged_
    - _Requirements: 1.4, 2.1, 2.4_

  - [x] 3.3 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Fix Error Output Format Compliance
    - **IMPORTANT**: Re-run the SAME test from task 1 — do NOT write a new test
    - The test from task 1 encodes the expected behavior (dedicated system prompt, few-shot example, post-processing)
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.4 Verify preservation tests still pass
    - **Property 2: Preservation** - Non-Fix-Error Actions Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 — do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm `build_prompt()` and `build_explain_prompt()` still use `SYSTEM_PROMPT`
    - Confirm `_trim_code()` and `_trim_console()` are unchanged
    - Confirm `ask()` and `explain_code()` have no post-processing wrapping
    - Confirm streaming mechanism is unchanged

- [x] 4. Checkpoint — Ensure all tests pass
  - Run the full test suite (exploration + preservation + any unit tests)
  - Ensure all tests pass, ask the user if questions arise
