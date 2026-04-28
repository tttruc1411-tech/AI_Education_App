# Implementation Plan

- [ ] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** — Curriculum Tab Reopen Blank Editor
  - **CRITICAL**: This test MUST FAIL on unfixed code — failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior — it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Scope the property to concrete curriculum filenames (e.g., `face_detection.py`, `grayscale_converter.py`) that exist in `curriculum/`
  - Test that after calling `load_curriculum_example(filename)`, the file exists in `projects/code/` and `file_manager.read_file(filename, folder='Code')` returns `{'success': True}` with non-empty content
  - Specifically: for any curriculum filename, call `load_curriculum_example(filename)` then assert `os.path.exists(os.path.join(projects_code_dir, filename))` is `True`
  - Also assert that `file_manager.read_file(filename, folder='Code')['success']` is `True` and `result['content']` matches the original curriculum file content
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (the file is never written to `projects/code/`, confirming the bug)
  - Document counterexamples found (e.g., "`load_curriculum_example('face_detection.py')` does not persist file to `projects/code/face_detection.py`; `read_file` returns `{'success': False}`")
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** — Non-Curriculum File Operations Unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - Observe: create a file via `file_manager.save_file('test_user_file.py', 'print("hello")', folder='Code')`, then `file_manager.read_file('test_user_file.py', folder='Code')` returns `{'success': True, 'content': 'print("hello")'}`
  - Observe: `load_file_by_tab('test_user_file.py')` reads the file and sets editor content correctly on unfixed code
  - Observe: saving a file then reading it back returns identical content on unfixed code
  - Write property-based test: for all non-curriculum filenames already in `projects/code/`, `file_manager.read_file(filename, folder='Code')` returns `{'success': True}` with the expected content (from Preservation Requirements in design: 3.1, 3.4)
  - Write property-based test: for all valid Python content strings, `file_manager.save_file(filename, content, folder='Code')` followed by `file_manager.read_file(filename, folder='Code')` returns the same content (from Preservation Requirements: 3.3)
  - Verify tests pass on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 3. Fix for curriculum tab reopen blank editor

  - [ ] 3.1 Implement the fix
    - In `load_curriculum_example()` in `main.py` (~line 3193), add `self.file_manager.save_file(filename, code_content, folder='Code')` BEFORE the `self.add_tab(filename, is_code=True)` call
    - This single line persists the curriculum file content to `projects/code/{filename}` so that `load_file_by_tab()` can read it on subsequent tab activations
    - No other changes are needed — `save_file()` delegates to `update_file()` which creates the file if it doesn't exist
    - _Bug_Condition: isBugCondition(input) where input.source = "curriculum" AND NOT fileExists("projects/code/" + input.filename)_
    - _Expected_Behavior: After load_curriculum_example(filename), fileExists("projects/code/" + filename) AND read_file(filename, folder='Code').success = True_
    - _Preservation: All non-curriculum file operations (user file tab switches, saves, creates) remain unchanged per design Preservation Requirements_
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4_

  - [ ] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** — Curriculum Tab Reopen Blank Editor
    - **IMPORTANT**: Re-run the SAME test from task 1 — do NOT write a new test
    - The test from task 1 encodes the expected behavior (file persisted to `projects/code/`)
    - When this test passes, it confirms the curriculum file is now written to `projects/code/` before `add_tab()` is called
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** — Non-Curriculum File Operations Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 — do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)

- [ ] 4. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
