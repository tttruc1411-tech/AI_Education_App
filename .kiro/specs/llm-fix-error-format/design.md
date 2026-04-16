# LLM Fix Error Format — Bugfix Design

## Overview

The "🔧 Fix Error" quick action in AI Coding Lab produces unstructured output because the Qwen2.5-Coder-1.5B model does not reliably follow the `Line X: ... / Original: ... / Fixed: ...` format instructions. The fix involves three targeted changes: (1) a dedicated fix-error system prompt that reinforces the output format, (2) a few-shot example in the user prompt to guide the small model, and (3) a post-processing fallback in `assistant.py` that enforces the format when the model deviates. All changes are scoped to the fix-error path only — general chat and explain actions remain untouched.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug — when `build_fix_prompt()` is called and the LLM response does not match the expected `Line X: ... / Original: ... / Fixed: ...` educational format
- **Property (P)**: The desired behavior — fix-error responses are always displayed in the structured educational format, either via model compliance or post-processing enforcement
- **Preservation**: Existing `build_prompt()` (chat) and `build_explain_prompt()` (explain) behavior, streaming token mechanism, model inference parameters, and chat panel display logic must remain unchanged
- **`build_fix_prompt()`**: The function in `src/modules/LLM/prompt_builder.py` that constructs the ChatML prompt for the fix-error action
- **`fix_error()`**: The method in `src/modules/LLM/assistant.py` that invokes `build_fix_prompt()` and streams the LLM response
- **`_infer()`**: The internal method in `assistant.py` that runs the llama-cpp streaming loop and delivers tokens via callbacks
- **ChatML**: The `<|im_start|>role\ncontent<|im_end|>` template format used by Qwen2.5 models
- **Few-shot example**: A concrete input/output example embedded in the prompt to demonstrate the expected response format to the model

## Bug Details

### Bug Condition

The bug manifests when the user clicks "🔧 Fix Error" and the LLM generates a response that does not follow the structured educational format. The `build_fix_prompt()` function uses the generic `SYSTEM_PROMPT` ("be concise, fix errors with code only") which does not reinforce the specific output format. The user prompt contains format instructions but zero few-shot examples, making it unreliable for a 1.5B parameter model. When the model deviates, the raw unformatted text is displayed directly to the student with no post-processing.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type FixErrorRequest (error_text: str, editor_code: str)
  OUTPUT: boolean

  llm_response := invoke_fix_error(input.error_text, input.editor_code)

  RETURN NOT matches_format(llm_response)
         WHERE matches_format(text) :=
           text contains line matching "Line \d+:.*"
           AND text contains line matching "Original:.*"
           AND text contains line matching "Fixed:.*"
END FUNCTION
```

### Examples

- **Example 1**: Student has `print("hello"` (missing closing paren) on line 3. Expected output: `Line 3: SyntaxError: missing closing parenthesis\nOriginal: print("hello"\nFixed: print("hello")`. Actual: model outputs a full code block with the entire corrected script.
- **Example 2**: Student has `for i in range(10)` (missing colon) on line 5. Expected: structured 3-line format. Actual: model outputs "You need to add a colon at the end of the for loop" as a conversational paragraph.
- **Example 3**: Student has `  x = 1` with wrong indentation on line 7. Expected: structured format showing the indentation fix. Actual: model outputs the fix but with inconsistent formatting like "Fix: change the indentation" without the `Line/Original/Fixed` structure.
- **Example 4 (Real observed bug)**: Student code has an IndentationError after `while True:` but the model outputs `Line 29: [IndentationError] Original: '# Main Loop (runs every frame)' Fixed: '# Main Loop (runs every frame)'` — pointing at a comment line instead of the actual broken code, and producing identical Original/Fixed text (zero educational value). This shows the model fails to identify the actual error location and produces no-op fixes.
- **Edge case**: Code has no actual error (error_text defaults to "Unknown error"). Expected: model still attempts a response; post-processing handles gracefully by passing through the raw text.

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Free-text chat via `build_prompt()` must continue to produce general conversational responses without any format enforcement
- "💡 Explain" via `build_explain_prompt()` must continue to produce free-form educational explanations without any format enforcement
- The streaming token-by-token display via `append_token()` / `MessageBubble` must continue to work in real-time for all actions
- Model inference parameters (temperature=0.2, max_tokens=512, context_len=4096, top_p=0.9, repeat_penalty=1.1) must remain unchanged
- The `_trim_code()` and `_trim_console()` helper functions must remain unchanged
- The chat panel UI layout, styling, and quick-action button behavior must remain unchanged

**Scope:**
All inputs that do NOT go through the `fix_error()` path should be completely unaffected by this fix. This includes:
- Free-text questions via `ask()`
- Code explanations via `explain_code()`
- Model loading/unloading lifecycle
- Chat panel rendering and scrolling behavior

## Hypothesized Root Cause

Based on the bug description and code analysis, the most likely issues are:

1. **Generic System Prompt**: `build_fix_prompt()` reuses the same `SYSTEM_PROMPT` as all other actions ("be concise, fix errors with code only"). This prompt does not mention the `Line/Original/Fixed` format at all, so the model has no system-level reinforcement of the expected output structure. Small models (1.5B) are especially sensitive to system prompt specificity.

2. **No Few-Shot Examples**: The user prompt contains format instructions ("Format your response exactly like this: Line X: ...") but provides zero concrete examples. Research on small language models consistently shows that 1.5B models follow format instructions far more reliably when given at least one concrete input/output example to pattern-match against.

3. **No Post-Processing Fallback**: The `_infer()` method in `assistant.py` passes the raw LLM output directly to the `on_done` callback without any validation or reformatting. When the model deviates from the format (which is frequent with a 1.5B model), the student sees unstructured text.

4. **Streaming vs Post-Processing Tension**: Tokens are streamed one-by-one to the chat panel via `on_token`. Post-processing must happen after the full response is collected (in `on_done`), which means the student will first see the raw streamed tokens and then potentially see a reformatted version. This needs careful UX handling.

## Correctness Properties

Property 1: Bug Condition - Fix Error Output Format Compliance

_For any_ fix-error request where `build_fix_prompt()` is called with valid error text and editor code, the final displayed output SHALL contain the structured educational format with a `Line N:` header, an `Original:` line, and a `Fixed:` line — either because the model produced it directly or because post-processing enforced it.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

Property 2: Preservation - Non-Fix-Error Actions Unchanged

_For any_ input that goes through `ask()` or `explain_code()` (i.e., NOT through `fix_error()`), the system SHALL produce exactly the same behavior as the original code, preserving general chat responses, explain responses, streaming behavior, and inference parameters.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `src/modules/LLM/prompt_builder.py`

**Function**: `build_fix_prompt()`

**Specific Changes**:
1. **Add a dedicated fix-error system prompt**: Create a new constant `FIX_SYSTEM_PROMPT` that explicitly describes the assistant's role as a code-fix formatter and reinforces the `Line/Original/Fixed` output structure at the system level. This replaces the generic `SYSTEM_PROMPT` only in `build_fix_prompt()`.

2. **Add a few-shot example**: Insert one concrete example in the user prompt showing an input error + code and the correctly formatted output. This gives the 1.5B model a pattern to follow. The example should be short (to conserve context tokens) but complete enough to demonstrate all three format lines.

3. **Tighten format instructions**: Simplify and strengthen the format instructions in the user prompt, removing ambiguity. Use a more directive phrasing that small models respond to better.

**File**: `src/modules/LLM/assistant.py`

**Function**: `fix_error()` and `_infer()`

**Specific Changes**:
4. **Add post-processing in `fix_error()`**: After the full response is collected via `on_done`, apply a `_postprocess_fix()` function that:
   - Checks if the response already matches the `Line N: ... / Original: ... / Fixed: ...` pattern
   - If yes, validates that Original and Fixed are NOT identical (no-op fix detection). If they are identical, treats it as a format deviation and attempts re-extraction or falls back
   - If no, attempts to extract line number, error description, original line, and fixed line from the unstructured response using regex heuristics
   - If extraction succeeds, reformats into the correct structure
   - If extraction fails, passes through the raw response as a graceful fallback (prefixed with a note)

5. **Wrap the `on_done` callback for fix_error only**: In `fix_error()`, wrap the caller's `on_done` callback with a lambda/function that applies `_postprocess_fix()` before forwarding. This keeps `_infer()` completely generic and unchanged for other actions.

6. **Handle streaming display**: Since tokens stream in real-time, the student will see the raw model output during streaming. The post-processed version replaces the bubble content via `set_text()` when streaming finishes. This is a minor UX trade-off — the student sees the raw stream briefly, then the formatted version appears. This avoids any changes to the streaming mechanism itself.

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Call `build_fix_prompt()` with various error/code combinations, feed the resulting prompt to the model, and check whether the response matches the `Line/Original/Fixed` format. Run on the UNFIXED code to observe format deviations.

**Test Cases**:
1. **SyntaxError Test**: Feed a missing-parenthesis SyntaxError with the corresponding code. Check if output matches format (will likely fail on unfixed code).
2. **IndentationError Test**: Feed an IndentationError with misindented code. Check if output matches format (will likely fail on unfixed code).
3. **NameError Test**: Feed a NameError (undefined variable) with code. Check if output matches format (will likely fail on unfixed code).
4. **Unknown Error Test**: Feed empty error text (defaults to "Unknown error") with valid code. Check behavior (may fail on unfixed code).

**Expected Counterexamples**:
- Model outputs full corrected code blocks instead of the 3-line format
- Model outputs conversational explanations instead of structured format
- Possible causes: generic system prompt, no few-shot examples, no post-processing

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := fix_error_fixed(input.error_text, input.editor_code)
  ASSERT result contains "Line \d+:"
  ASSERT result contains "Original:"
  ASSERT result contains "Fixed:"
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT ask_original(input) = ask_fixed(input)
  ASSERT explain_original(input) = explain_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Verify that `build_prompt()` and `build_explain_prompt()` produce identical output before and after the fix. Verify that `_infer()` behavior is unchanged for non-fix-error prompts.

**Test Cases**:
1. **Chat Prompt Preservation**: Generate random user questions and code snippets, verify `build_prompt()` output is identical before and after the fix
2. **Explain Prompt Preservation**: Generate random code snippets, verify `build_explain_prompt()` output is identical before and after the fix
3. **Inference Parameter Preservation**: Verify that `_infer()` passes the same parameters (temperature, max_tokens, etc.) for all action types
4. **Streaming Preservation**: Verify that `on_token` callbacks fire identically for chat and explain actions

### Unit Tests

- Test `build_fix_prompt()` output contains the few-shot example and dedicated system prompt
- Test `_postprocess_fix()` with a correctly formatted input (should pass through unchanged)
- Test `_postprocess_fix()` with an unstructured input containing extractable info (should reformat)
- Test `_postprocess_fix()` with a completely unstructured input (should fall back gracefully)
- Test that `build_prompt()` and `build_explain_prompt()` still use the original `SYSTEM_PROMPT`

### Property-Based Tests

- Generate random error text and code combinations, verify `build_fix_prompt()` always produces valid ChatML with the dedicated system prompt and few-shot example
- Generate random LLM response strings, verify `_postprocess_fix()` either produces valid format or falls back gracefully (never crashes, never produces empty output)
- Generate random user questions, verify `build_prompt()` output is unchanged from the original implementation

### Integration Tests

- End-to-end test: call `fix_error()` with a real error, verify the final `on_done` output matches the expected format
- Test that streaming tokens are delivered via `on_token` and the final formatted output is delivered via `on_done`
- Test that `ask()` and `explain_code()` still work identically after the fix
