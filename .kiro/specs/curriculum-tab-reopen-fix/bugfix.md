# Bugfix Requirements Document

## Introduction

When a curriculum example is loaded via the Learning Hub "Load" button, the file content is displayed in the editor and a tab is created. However, switching away from that tab and clicking it again (or re-clicking "Load") results in a blank editor. This happens because `load_file_by_tab()` reads from `projects/code/` via `file_manager.read_file()`, but the curriculum file was never copied there — it was only read directly from the `curriculum/` folder into the editor.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a curriculum example tab is clicked after switching to another tab THEN the system shows a blank editor because `load_file_by_tab()` fails to find the file in `projects/code/`

1.2 WHEN the user clicks "Load" again on a curriculum card that already has an open tab THEN the system calls `load_file_by_tab()` (via `add_tab()` detecting the existing tab) which fails to read the file, resulting in a blank editor

1.3 WHEN a curriculum file is loaded THEN the system does not persist it to `projects/code/`, making it invisible in the Workspace file browser and unavailable for the tab system to re-read

### Expected Behavior (Correct)

2.1 WHEN a curriculum example tab is clicked after switching to another tab THEN the system SHALL display the curriculum file content in the editor by reading it from `projects/code/` where it was persisted on load

2.2 WHEN the user clicks "Load" again on a curriculum card that already has an open tab THEN the system SHALL re-read the file from `projects/code/` and display it correctly in the editor

2.3 WHEN a curriculum file is loaded via the Learning Hub THEN the system SHALL copy the file content to `projects/code/{filename}` before creating the tab, ensuring it is available for subsequent reads and visible in the Workspace file browser

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a user-created file tab in `projects/code/` is clicked THEN the system SHALL CONTINUE TO load the file content correctly via `file_manager.read_file()`

3.2 WHEN a curriculum example is loaded for the first time THEN the system SHALL CONTINUE TO display the file content immediately in the editor

3.3 WHEN a user edits and saves a curriculum-originated file THEN the system SHALL CONTINUE TO save it to `projects/code/` as normal

3.4 WHEN a non-curriculum tab is switched to and from THEN the system SHALL CONTINUE TO reload file content correctly without any blank editor state

---

## Bug Condition (Formal)

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type TabActivationEvent
  OUTPUT: boolean
  
  // Returns true when the file originated from curriculum/ and has not been
  // persisted to projects/code/ before the tab system tries to read it
  RETURN X.source = "curriculum" AND NOT exists("projects/code/" + X.filename)
END FUNCTION
```

### Property: Fix Checking

```pascal
// After the fix, loading a curriculum example always persists it to projects/code/
FOR ALL X WHERE isBugCondition(X) DO
  result ← load_curriculum_example'(X.filename)
  ASSERT exists("projects/code/" + X.filename)
  ASSERT load_file_by_tab'(X.filename).content ≠ ""
END FOR
```

### Property: Preservation Checking

```pascal
// For all non-curriculum files (already in projects/code/), behavior is unchanged
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT load_file_by_tab(X.filename) = load_file_by_tab'(X.filename)
END FOR
```
