# Curriculum Tab Reopen Fix — Bugfix Design

## Overview

When a curriculum example is loaded via the Learning Hub, the file content is displayed in the editor and a tab is created, but the file is never persisted to `projects/code/`. This means `load_file_by_tab()` — which reads from `projects/code/` via `file_manager.read_file()` — fails silently on tab re-activation, leaving the editor blank. The fix is to write the curriculum file content to `projects/code/{filename}` before calling `add_tab()`, so the tab system can always re-read it.

## Glossary

- **Bug_Condition (C)**: A curriculum file tab is activated but the file does not exist in `projects/code/`, causing `load_file_by_tab()` to fail
- **Property (P)**: After loading a curriculum example, the file SHALL exist in `projects/code/` and be readable by the tab system on re-activation
- **Preservation**: All existing file operations (user-created files, save, tab switching for non-curriculum files) must remain unchanged
- **load_curriculum_example()**: The function in `main.py` (~line 3193) that reads a curriculum `.py` file and displays it in the editor
- **load_file_by_tab()**: The function in `main.py` (~line 3427) that reads a file from `projects/code/` (via `file_manager.read_file()`) when a tab is clicked
- **file_manager**: Instance of `FileManager` (from `src/modules/file_manager.py`) managing file I/O for `projects/code/`, `projects/data/`, and `projects/model/`

## Bug Details

### Bug Condition

The bug manifests when a user loads a curriculum example, switches to another tab, then clicks the curriculum tab again. `load_file_by_tab()` calls `file_manager.read_file(filename, folder='Code')` which looks in `projects/code/` — but the file was never written there. The fallback to `folder='Projects'` also fails because curriculum files live in `curriculum/`, not `projects/`.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type TabActivationEvent
  OUTPUT: boolean

  RETURN input.source = "curriculum"
         AND NOT fileExists("projects/code/" + input.filename)
END FUNCTION
```

### Examples

- User clicks "Load" on the Face Detection card → `face_detection.py` displays in editor, tab created → user clicks another tab → clicks `face_detection.py` tab → **blank editor** (expected: code re-displayed)
- User clicks "Load" on the same curriculum card again → `add_tab()` detects existing tab → calls `load_file_by_tab()` → **blank editor** (expected: code re-displayed)
- User loads `grayscale_converter.py` from curriculum → closes app → reopens → clicks the tab if restored → **blank editor** (expected: code displayed from persisted file)
- User loads a curriculum file, edits it, clicks Save → `save_file()` writes to `projects/code/` → subsequent tab clicks work fine (this path is NOT buggy because the user explicitly saved)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- User-created files in `projects/code/` must continue to load correctly via `load_file_by_tab()`
- The first-time display of curriculum content in the editor (immediate `setPlainText`) must continue to work
- Saving and editing curriculum-originated files must continue to write to `projects/code/` as normal
- Non-curriculum tab switching must continue to reload file content correctly
- The Workspace file browser must continue to reflect files in `projects/code/`

**Scope:**
All inputs that do NOT involve loading a curriculum file for the first time should be completely unaffected by this fix. This includes:
- Clicking tabs for files already in `projects/code/`
- Creating new files via the editor
- Saving files via Ctrl+S or the Save button
- Running code from any tab

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is clear:

1. **Missing File Persistence Step**: `load_curriculum_example()` reads the file from `curriculum/` and calls `self.monacoPlaceholder.setPlainText(code_content)` followed by `self.add_tab(filename)`, but never writes `code_content` to `projects/code/{filename}`. This is the sole root cause.

2. **Tab System Assumption**: `add_tab()` → `load_file_by_tab()` → `file_manager.read_file(filename, folder='Code')` assumes the file exists in `projects/code/`. This assumption is valid for user-created files but not for curriculum files that were only read from `curriculum/`.

3. **No Fallback to curriculum/ in read_file()**: `read_file()` with `folder='Code'` only checks `projects/code/` (with a legacy fallback for `face_detection.py` specifically). There is no general fallback to `curriculum/`.

## Correctness Properties

Property 1: Bug Condition — Curriculum file persisted on load

_For any_ curriculum filename loaded via `load_curriculum_example()`, the fixed function SHALL write the file content to `projects/code/{filename}` before creating the tab, such that any subsequent call to `load_file_by_tab(filename)` returns the file content (non-empty).

**Validates: Requirements 2.1, 2.2, 2.3**

Property 2: Preservation — Non-curriculum file operations unchanged

_For any_ file operation that does NOT involve loading a curriculum example (user-created files, saves, tab switches for existing `projects/code/` files), the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing file I/O and tab management functionality.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

## Fix Implementation

### Changes Required

**File**: `main.py`

**Function**: `load_curriculum_example()` (~line 3193)

**Specific Changes**:
1. **Persist curriculum content to `projects/code/`**: After reading `code_content` from the curriculum file, call `self.file_manager.save_file(filename, code_content, folder='Code')` to write it to `projects/code/{filename}`. This uses the existing `update_file()` method which creates the file if it doesn't exist.

2. **Placement**: The `save_file()` call must occur BEFORE `self.add_tab(filename)`, because `add_tab()` may call `load_file_by_tab()` if the tab already exists (which reads from `projects/code/`).

3. **No other changes needed**: The `file_manager.save_file()` method already handles the `.py` extension check and writes to `self.code_dir` when `folder='Code'` is specified. No new methods or classes are required.

**Resulting code flow:**
```python
def load_curriculum_example(self, filename: str):
    file_path = os.path.join(..., "curriculum", filename)
    with open(file_path, "r", encoding="utf-8") as f:
        code_content = f.read()
    self.monacoPlaceholder.setPlainText(code_content)
    self.current_open_file = filename
    # ... logging ...
    self.file_manager.save_file(filename, code_content, folder='Code')  # NEW LINE
    self.add_tab(filename, is_code=True)
```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm that `load_file_by_tab()` fails for curriculum files.

**Test Plan**: Call `load_curriculum_example()` for a curriculum file, then call `load_file_by_tab()` for the same filename and assert the editor content is non-empty. Run on UNFIXED code to observe failure.

**Test Cases**:
1. **Tab Re-activation Test**: Load a curriculum file, switch tab, click curriculum tab again → editor blank (will fail on unfixed code)
2. **Re-load via Load Button**: Load a curriculum file, click "Load" again on same card → `add_tab()` calls `load_file_by_tab()` → editor blank (will fail on unfixed code)
3. **File Existence Check**: After `load_curriculum_example()`, check `projects/code/{filename}` exists → does NOT exist (will fail on unfixed code)

**Expected Counterexamples**:
- `file_manager.read_file(filename, folder='Code')` returns `{'success': False}` because file not in `projects/code/`
- Root cause confirmed: no write to `projects/code/` in `load_curriculum_example()`

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL filename IN curriculum_files DO
  load_curriculum_example'(filename)
  ASSERT fileExists("projects/code/" + filename)
  result := file_manager.read_file(filename, folder='Code')
  ASSERT result['success'] = True
  ASSERT result['content'] ≠ ""
  ASSERT result['content'] = originalCurriculumContent(filename)
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL filename WHERE NOT isBugCondition(filename) DO
  ASSERT load_file_by_tab(filename) = load_file_by_tab'(filename)
  ASSERT save_file(filename, content) = save_file'(filename, content)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code for user-created files (already in `projects/code/`), then write property-based tests capturing that behavior continues after the fix.

**Test Cases**:
1. **User File Tab Switch Preservation**: Verify clicking tabs for user-created files in `projects/code/` continues to load content correctly
2. **Save File Preservation**: Verify saving files via the editor continues to write to `projects/code/` correctly
3. **Create File Preservation**: Verify creating new files via the editor continues to work
4. **Workspace Browser Preservation**: Verify the file browser continues to list files correctly

### Unit Tests

- Test that `load_curriculum_example()` writes file to `projects/code/`
- Test that `load_file_by_tab()` succeeds after `load_curriculum_example()` for the same filename
- Test that re-calling `add_tab()` for an existing curriculum tab displays content correctly
- Test edge case: curriculum file with same name as existing user file (should overwrite with curriculum content)

### Property-Based Tests

- Generate random curriculum filenames and verify they are persisted to `projects/code/` after loading
- Generate random sequences of tab switches (curriculum + user files) and verify all tabs display content correctly
- Generate random file operations on non-curriculum files and verify behavior is identical before/after fix

### Integration Tests

- Full flow: Load curriculum → switch tab → click curriculum tab → verify content displayed
- Full flow: Load curriculum → click "Load" again → verify content displayed
- Full flow: Load curriculum → edit → save → switch tab → click tab → verify edited content persists
- Full flow: Load curriculum → verify file appears in Workspace file browser
