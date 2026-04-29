# Implementation Plan: Fill-in-the-Blank Lessons

## Overview

Transform the lesson system from free-form editing with whole-file comparison grading into a structured fill-in-the-blank approach. This involves creating two new modules (`lesson_parser.py`, `blank_validator.py`), extending the QScintilla editor with blank-mode support, migrating all lesson step files to the `# __BLANK__` format, adding translation keys, and updating the main controller to wire everything together.

## Tasks

- [x] 1. Create the Lesson Parser module
  - [x] 1.1 Create `src/modules/lesson_parser.py` with `BlankInfo` and `ParsedStep` dataclasses
    - Define `BLANK_MARKER = "# __BLANK__"`
    - Implement `BlankInfo` dataclass with `line_number`, `indentation`, and `expected_answers` fields
    - Implement `ParsedStep` dataclass with `display_lines`, `blank_map`, `is_challenge`, and `raw_content` fields
    - _Requirements: 1.1, 1.4, 1.5_

  - [x] 1.2 Implement `parse_step_file()` and `_parse_blank_line()` functions
    - `parse_step_file(file_path)` reads the file, scans each line for `# __BLANK__` prefix
    - Replace blank marker lines with indentation-only empty lines in `display_lines`
    - Preserve original indentation of each marker line
    - Store pipe-separated alternatives as list in `BlankInfo.expected_answers`
    - Set `is_challenge = True` when no blank markers found
    - Store `raw_content` for challenge fallback
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [ ]* 1.3 Write property tests for lesson parser (Property 1 & 2)
    - **Property 1: Parsing round-trip preserves blank markers**
    - **Validates: Requirements 1.1, 1.2, 1.4, 1.5, 1.6**
    - **Property 2: Challenge detection is correct**
    - **Validates: Requirements 1.3**
    - Create `tests/test_lesson_parser_props.py` using `hypothesis`
    - Generate random step file content with mix of code lines and `# __BLANK__` lines with random indentation and pipe-separated answers

  - [ ]* 1.4 Write unit tests for lesson parser edge cases
    - Create `tests/test_lesson_parser.py`
    - Test: empty file, file with only comments, file with only blank markers, marker at first/last line, marker with no answer text, pipe-separated alternatives
    - _Requirements: 1.1, 1.2, 1.3, 1.6_

- [x] 2. Create the Blank Validator module
  - [x] 2.1 Create `src/modules/blank_validator.py` with `BlankResult` dataclass and `normalize_code()` function
    - Define `BlankResult` dataclass with `line_number`, `is_correct`, `student_answer`, `expected_answers`
    - Implement `normalize_code(code)`: strip whitespace, collapse multiple spaces, remove spaces around `=` in keyword args, remove spaces inside parentheses, normalize comma spacing
    - _Requirements: 5.2_

  - [x] 2.2 Implement `validate_blank()` and `validate_blanks()` functions
    - `validate_blank(student_input, expected_answers)` normalizes both sides and checks if any expected answer matches
    - `validate_blanks(blank_contents, blank_map)` iterates all blanks and returns list of `BlankResult`
    - Step is correct only when all blanks are correct
    - _Requirements: 5.1, 5.3, 5.4_

  - [ ]* 2.3 Write property tests for blank validator (Property 3, 4, 5)
    - **Property 3: Blank validation matches any valid alternative**
    - **Validates: Requirements 5.1, 5.3**
    - **Property 4: Code normalization is idempotent**
    - **Validates: Requirements 5.2**
    - **Property 5: Step correctness requires all blanks correct**
    - **Validates: Requirements 5.4**
    - Create `tests/test_blank_validator_props.py` using `hypothesis`

  - [ ]* 2.4 Write unit tests for blank validator edge cases
    - Create `tests/test_blank_validator.py`
    - Test: empty input, whitespace-only input, exact match, extra spaces, no match, case sensitivity, normalization specifics (`param = value` → `param=value`, `( x )` → `(x)`, `a,b` → `a, b`)
    - _Requirements: 5.1, 5.2, 5.3_

- [ ] 3. Checkpoint - Ensure parser and validator tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Extend the Advanced Editor with blank mode support
  - [x] 4.1 Add blank-mode indicator constants and state variables to `AdvancedPythonEditor`
    - Add `FIXED_LINE_INDICATOR = 14`, `BLANK_SLOT_INDICATOR = 15`, `FEEDBACK_CORRECT = 16`, `FEEDBACK_INCORRECT = 17`
    - Add instance state: `_blank_mode`, `_blank_lines` (set), `_fixed_lines` (set)
    - Configure indicator styles: dashed-border placeholder for blank slots, green/red backgrounds for feedback
    - _Requirements: 3.1, 3.2, 6.1, 6.2_

  - [x] 4.2 Implement `set_blank_mode()` and `exit_blank_mode()` methods
    - `set_blank_mode(parsed_step)`: set editor text from `display_lines`, mark fixed lines read-only, style blank slots with distinct background and placeholder text
    - `exit_blank_mode()`: clear all blank-mode indicators, reset `_blank_mode` flag, restore normal editing
    - Handle both standard (1280x800) and small (1024x600) screen resolutions for blank slot styling
    - _Requirements: 2.1, 3.1, 3.2, 3.3, 3.4_

  - [x] 4.3 Implement read-only protection for fixed lines
    - Override `keyPressEvent` to block typing, backspace, delete on fixed lines when `_blank_mode` is active
    - Block paste operations that would modify fixed lines
    - Allow cursor navigation (arrow keys, Home, End, Page Up, Page Down) through fixed lines
    - When student clicks on a fixed line, redirect cursor to nearest blank slot
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 4.4 Implement drag-and-drop restriction for blank mode
    - Modify `dragMoveEvent` to show ghost block only over blank slots when `_blank_mode` is active
    - Modify `dropEvent` to reject drops on fixed lines, accept drops on blank slots
    - When dropping on a blank slot with existing text, replace the text
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 4.5 Implement `get_blank_contents()`, `set_blank_feedback()`, `clear_blank_feedback()`, and `fill_blanks_with_answers()`
    - `get_blank_contents()`: extract text from each blank slot line, return dict keyed by line number
    - `set_blank_feedback(results)`: apply green background for correct blanks, red for incorrect
    - `clear_blank_feedback(line)`: remove highlight on a specific line when student edits it
    - `fill_blanks_with_answers(blank_map)`: populate all blank slots with first expected answer (for Solution button)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 8.4_

- [ ] 5. Checkpoint - Ensure editor blank mode works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Add translation keys for blank mode
  - [x] 6.1 Add English and Vietnamese translation keys to `src/modules/translations.py`
    - Add `BLANK_PLACEHOLDER`, `BLANK_CORRECT`, `BLANK_INCORRECT`, `BLANK_ALL_CORRECT`, `BLANK_SOME_WRONG` keys to both `en` and `vi` dictionaries
    - English: "Type or drop code here...", "✅ Correct!", "❌ Try again", "All blanks correct!", "{} of {} blanks incorrect"
    - Vietnamese: "Nhập hoặc kéo thả code vào đây...", "✅ Đúng rồi!", "❌ Thử lại", "Tất cả đều đúng!", "{} trên {} ô chưa đúng"
    - _Requirements: 9.2_

- [ ] 7. Update main.py controller for fill-in-blank integration
  - [x] 7.1 Modify `load_step()` to use `lesson_parser` for blank-marker steps
    - Import `lesson_parser` module
    - Call `parse_step_file()` on the step file path
    - If `parsed_step.is_challenge` is False, call `editor.set_blank_mode(parsed_step)` instead of `setPlainText`
    - If `parsed_step.is_challenge` is True, use existing free-form loading (setPlainText with raw_content)
    - Store `parsed_step` on the controller for use during submit
    - Load step files from language-specific folder based on `current_lang`
    - _Requirements: 1.1, 1.2, 1.3, 7.4, 9.1_

  - [x] 7.2 Modify `submit_step()` to use `blank_validator` for per-blank validation
    - Import `blank_validator` module
    - When in blank mode: extract blank contents via `editor.get_blank_contents()`, call `validate_blanks()`
    - Apply visual feedback via `editor.set_blank_feedback(results)`
    - Report step as correct only when all blanks pass
    - When not in blank mode (challenge): fall back to existing whole-file comparison
    - Integrate with existing hearts system (full heart / half heart / zero hearts logic)
    - _Requirements: 5.1, 5.4, 8.1, 8.2, 8.3, 8.5_

  - [x] 7.3 Implement `_show_solution_for_blanks()` and `_on_blank_edited()` methods
    - `_show_solution_for_blanks()`: call `editor.fill_blanks_with_answers(blank_map)` when Solution button clicked in blank mode
    - Set `lesson_solution_used = True` so no hearts are awarded
    - `_on_blank_edited(line)`: connect to editor text change signal, call `editor.clear_blank_feedback(line)` to remove highlight on edit
    - _Requirements: 6.3, 6.4, 8.4_

  - [ ] 7.4 Handle language switch during active lesson
    - When language is switched while a lesson is active, re-call `load_step(current_step)` with the new language path
    - If new language file is missing, fall back to English file and log warning
    - _Requirements: 9.1, 9.3, 9.4_

- [ ] 8. Checkpoint - Ensure controller integration works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Migrate lesson step files to blank marker format (English)
  - [x] 9.1 Migrate Lesson 1 (Camera Basics) English steps to `# __BLANK__` format
    - Convert `lessons/en/lesson1_camera_basics/step1_my_first_camera.py` — replace TODO lines with `# __BLANK__ <expected_answer>` using answers from `lessons/solutions/lesson1_step1_solution.py`
    - Convert `step2_save_load_pictures.py`, `step3_mirror_selfie_mode.py`, `step4_brightness_control.py`, `step5_rotate_image.py`
    - Leave `challenge_photo_booth.py` unchanged (free-form)
    - Use pipe-separated alternatives where multiple valid answers exist
    - _Requirements: 7.1, 7.3_

  - [x] 9.2 Migrate Lesson 2 (Image Processing) English steps to `# __BLANK__` format
    - Convert all 5 regular steps in `lessons/en/lesson2_image_processing/`
    - Leave `challenge_artistic_filter.py` unchanged
    - Reference solutions from `lessons/solutions/lesson2_step*_solution.py`
    - _Requirements: 7.1, 7.3_

  - [x] 9.3 Migrate Lesson 3 (Drawing & Shapes) English steps to `# __BLANK__` format
    - Convert all 4 regular steps in `lessons/en/lesson3_drawing_shapes/`
    - Leave `challenge_creative_art.py` unchanged
    - Reference solutions from `lessons/solutions/lesson3_step*_solution.py`
    - _Requirements: 7.1, 7.3_

- [ ] 10. Migrate lesson step files to blank marker format (Vietnamese)
  - [x] 10.1 Migrate Lesson 1 (Camera Basics) Vietnamese steps to `# __BLANK__` format
    - Convert all 5 regular steps in `lessons/vi/lesson1_camera_basics/`
    - Expected answers must match the corresponding English step (same code, same function calls)
    - Leave `challenge_photo_booth.py` unchanged
    - _Requirements: 7.2, 7.3_

  - [x] 10.2 Migrate Lesson 2 (Image Processing) Vietnamese steps to `# __BLANK__` format
    - Convert all 5 regular steps in `lessons/vi/lesson2_image_processing/`
    - Leave challenge unchanged
    - _Requirements: 7.2, 7.3_

  - [x] 10.3 Migrate Lesson 3 (Drawing & Shapes) Vietnamese steps to `# __BLANK__` format
    - Convert all 4 regular steps in `lessons/vi/lesson3_drawing_shapes/`
    - Leave challenge unchanged
    - _Requirements: 7.2, 7.3_

- [ ] 11. Checkpoint - Verify all migrated lesson files parse correctly
  - Ensure all tests pass, ask the user if questions arise.
  - Verify each migrated step file produces correct `ParsedStep` with expected blank count

- [ ] 12. Final integration and wiring
  - [ ] 12.1 Wire editor text-change signal to clear feedback on edit
    - Connect QScintilla `textChanged` or `SCN_MODIFIED` signal to detect edits on blank lines
    - Call `clear_blank_feedback(line)` for the edited line only
    - Maintain feedback highlights on unmodified blank slots
    - _Requirements: 6.3, 6.4_

  - [ ] 12.2 Wire Solution button to blank-mode handler
    - In `main.py`, check if `_blank_mode` is active when Solution button is clicked
    - If blank mode: call `_show_solution_for_blanks()` instead of loading solution file
    - If challenge mode: use existing solution file loading behavior
    - _Requirements: 8.4_

  - [ ]* 12.3 Write integration tests for full lesson flow
    - Test: load lesson → fill blanks correctly → submit → verify hearts awarded → navigate next step
    - Test: challenge step uses free-form mode with whole-file comparison
    - Test: Solution button populates blanks and awards 0 hearts
    - Test: language switch reloads step from correct language folder
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 9.1, 9.4_

- [ ] 13. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The project uses Python 3.9+ with PyQt5 and QScintilla — all code should be compatible
- Challenge steps (3 total) remain completely unchanged — no blank markers
- Solution files in `lessons/solutions/` are still needed for challenge steps but not for blank-marker steps
