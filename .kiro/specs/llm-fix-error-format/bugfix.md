# Bugfix Requirements Document

## Introduction

The AI Assistant's "Fix Error" quick action (`🔧 Fix Error`) in the educational Python IDE "AI Coding Lab" does not produce correctly formatted output. The `build_fix_prompt()` function in `prompt_builder.py` instructs the Qwen2.5-Coder-1.5B model to respond in a specific `Line X: ... / Original: ... / Fixed: ...` format, but the 1.5B parameter model does not reliably follow these instructions. The system prompt is too generic, the user prompt lacks few-shot examples to guide the small model, and there is no post-processing fallback to enforce the format when the model deviates. This results in unstructured, inconsistent responses that are confusing for students.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the user clicks "🔧 Fix Error" and the LLM generates a response THEN the system produces unstructured or inconsistent output that does not follow the required `Line X: ... / Original: ... / Fixed: ...` educational format. Observed example: the model points at a comment line (`# Main Loop (runs every frame)`) instead of the actual broken code line, and produces identical Original/Fixed text — providing zero educational value to the student

1.2 WHEN the `build_fix_prompt()` constructs the ChatML prompt THEN the system uses a generic system prompt ("be concise, fix errors with code only") that does not reinforce the specific output format, causing the 1.5B model to ignore the format instructions

1.3 WHEN the `build_fix_prompt()` constructs the ChatML prompt THEN the system provides zero few-shot examples, making it unreliable for a small 1.5B parameter model to follow the strict output template

1.4 WHEN the LLM returns a response that deviates from the expected format THEN the system displays the raw unformatted response directly to the student without any post-processing or format enforcement

### Expected Behavior (Correct)

2.1 WHEN the user clicks "🔧 Fix Error" and the LLM generates a response THEN the system SHALL display output in the structured educational format: `Line X: [error type]: [short description]` followed by `Original: [broken line]` followed by `Fixed: [corrected line]`

2.2 WHEN the `build_fix_prompt()` constructs the ChatML prompt THEN the system SHALL use a system prompt specifically tailored for the fix-error action that reinforces the exact output format expected

2.3 WHEN the `build_fix_prompt()` constructs the ChatML prompt THEN the system SHALL include at least one few-shot example demonstrating the correct output format to guide the small 1.5B model

2.4 WHEN the LLM returns a response that deviates from the expected format THEN the system SHALL apply post-processing to extract and reformat the key information (line number, error description, original line, fixed line) into the correct educational format, or display the raw response as a graceful fallback if extraction is not possible

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the user sends a free-text question via the chat input THEN the system SHALL CONTINUE TO use `build_prompt()` and produce general conversational responses without any format enforcement

3.2 WHEN the user clicks "💡 Explain" THEN the system SHALL CONTINUE TO use `build_explain_prompt()` and produce free-form educational explanations without any format enforcement

3.3 WHEN the code has no errors and the user clicks "🔧 Fix Error" THEN the system SHALL CONTINUE TO handle the case gracefully (the error text defaults to "Unknown error")

3.4 WHEN the LLM is streaming tokens to the chat panel THEN the system SHALL CONTINUE TO display tokens incrementally in real-time via the existing `append_token()` / `MessageBubble` mechanism

3.5 WHEN the model configuration parameters (temperature=0.2, max_tokens=512, context_len=4096) are used for fix-error inference THEN the system SHALL CONTINUE TO use these same inference parameters without modification
