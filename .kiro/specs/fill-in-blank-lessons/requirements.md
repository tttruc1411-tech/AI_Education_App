# Requirements Document

## Introduction

The Fill-in-the-Blank Lessons feature replaces the current free-form editor with whole-file comparison grading system with a structured "fill in the blank" approach. Lesson step files use `# __BLANK__` markers to define editable slots where students must type or drag-and-drop the correct function call. All non-blank lines are read-only. Validation is performed per-blank against embedded expected answers, and visual feedback (green/red highlighting) shows students exactly which blanks are correct or incorrect. Challenge steps remain free-form. The existing hearts/hint/solution system continues to work with the new per-blank validation.

## Glossary

- **Editor**: The QScintilla-based code editor widget (`AdvancedPythonEditor` in `advanced_editor.py`) that displays lesson code and handles user input
- **Blank_Slot**: An editable line in the Editor created from a `# __BLANK__` marker, where the student must enter the correct function call
- **Fixed_Line**: A non-blank line in a lesson step that is read-only and cannot be modified by the student
- **Blank_Marker**: The string `# __BLANK__` at the start of a line in a lesson step file, followed by the expected answer on the same line
- **Expected_Answer**: The correct code extracted from after the Blank_Marker in a lesson step file; a Blank_Slot may accept multiple valid Expected_Answers
- **Lesson_Parser**: The module responsible for reading lesson step files, extracting Blank_Markers and Expected_Answers, and producing the display code with empty Blank_Slots
- **Blank_Validator**: The module responsible for comparing each Blank_Slot's student input against its Expected_Answer(s) and returning per-blank pass/fail results
- **Step_File**: A Python file in `lessons/en/` or `lessons/vi/` that defines one step of a lesson, containing a mix of fixed code and Blank_Markers
- **Challenge_Step**: The final step in each lesson that uses free-form editing with no Blank_Slots, validated by whole-file comparison against a solution file
- **Function_Library**: The drag-and-drop panel containing function blocks defined in `definitions.py`
- **Ghost_Block**: The semi-transparent visual guide shown during drag-and-drop operations in the Editor
- **StepProgressBar**: The UI widget showing step indicators, navigation buttons, Submit button, and hearts display

## Requirements

### Requirement 1: Blank Marker Parsing

**User Story:** As a student, I want lesson steps to automatically show me where to write code, so that I know exactly which lines need my input.

#### Acceptance Criteria

1. WHEN a Step_File is loaded, THE Lesson_Parser SHALL scan each line for the Blank_Marker prefix `# __BLANK__` and extract the Expected_Answer from the remainder of that line
2. WHEN a Step_File contains a Blank_Marker line, THE Lesson_Parser SHALL replace that line with an empty editable Blank_Slot in the Editor
3. WHEN a Step_File contains no Blank_Marker lines, THE Lesson_Parser SHALL treat the step as a Challenge_Step and load the file in free-form editing mode
4. THE Lesson_Parser SHALL preserve the original indentation of each Blank_Marker line when creating the corresponding Blank_Slot
5. THE Lesson_Parser SHALL store each Expected_Answer mapped to its corresponding Blank_Slot line number for use during validation
6. WHEN a Blank_Marker line contains a pipe-separated list of answers (e.g., `# __BLANK__ answer1 | answer2`), THE Lesson_Parser SHALL store all alternatives as valid Expected_Answers for that Blank_Slot

### Requirement 2: Read-Only Fixed Lines

**User Story:** As a student, I want the pre-written code lines to be locked so that I cannot accidentally break the lesson structure.

#### Acceptance Criteria

1. WHEN a Step_File with Blank_Markers is loaded, THE Editor SHALL mark all non-blank lines as read-only Fixed_Lines
2. WHILE a Fixed_Line is read-only, THE Editor SHALL block all keyboard input (typing, backspace, delete) on that line
3. WHILE a Fixed_Line is read-only, THE Editor SHALL block paste operations that would modify that line
4. THE Editor SHALL allow the cursor to navigate through Fixed_Lines using arrow keys, Home, End, Page Up, and Page Down
5. WHEN the student clicks on a Fixed_Line, THE Editor SHALL move the cursor to the nearest Blank_Slot instead

### Requirement 3: Visual Blank Slot Styling

**User Story:** As a student, I want blank lines to look visually distinct so that I can immediately see where to write my code.

#### Acceptance Criteria

1. WHEN a Blank_Slot is displayed in the Editor, THE Editor SHALL render a dashed-border placeholder with a colored background on that line
2. THE Editor SHALL use a distinct background color for Blank_Slots that contrasts with both the dark theme and Fixed_Lines
3. WHEN a Blank_Slot is empty, THE Editor SHALL display placeholder text (e.g., "Drop or type code here...") in a muted color
4. THE Editor SHALL scale Blank_Slot visual styling appropriately for both standard (1280x800) and small (1024x600) screen resolutions

### Requirement 4: Drag-and-Drop Restriction

**User Story:** As a student, I want drag-and-drop from the Function_Library to only work on blank lines, so that I cannot accidentally place code on locked lines.

#### Acceptance Criteria

1. WHEN a function block is dragged from the Function_Library over a Blank_Slot, THE Editor SHALL show the Ghost_Block drop indicator on that Blank_Slot
2. WHEN a function block is dragged from the Function_Library over a Fixed_Line, THE Editor SHALL hide the Ghost_Block and indicate the drop is not allowed
3. WHEN a function block is dropped on a Blank_Slot, THE Editor SHALL insert the function call text into that Blank_Slot
4. WHEN a function block is dropped on a Fixed_Line, THE Editor SHALL reject the drop and leave the Editor unchanged
5. WHEN a function block is dropped on a Blank_Slot that already contains text, THE Editor SHALL replace the existing text with the new function call

### Requirement 5: Per-Blank Validation

**User Story:** As a student, I want each blank to be checked independently when I submit, so that I know exactly which answers are right and which need fixing.

#### Acceptance Criteria

1. WHEN the student clicks Submit, THE Blank_Validator SHALL compare each Blank_Slot's content against its corresponding Expected_Answer(s)
2. THE Blank_Validator SHALL normalize both student input and Expected_Answer by removing extra whitespace and standardizing spacing around operators and parentheses before comparison
3. WHEN a Blank_Slot has multiple valid Expected_Answers, THE Blank_Validator SHALL accept the student input if it matches any one of the alternatives
4. THE Blank_Validator SHALL report the step as correct only when all Blank_Slots in the step contain correct answers
5. WHEN the step is a Challenge_Step with no Blank_Slots, THE Blank_Validator SHALL fall back to the existing whole-file comparison against the solution file

### Requirement 6: Per-Blank Visual Feedback

**User Story:** As a student, I want to see green or red highlighting on each blank after I submit, so that I know exactly which blanks to fix.

#### Acceptance Criteria

1. WHEN validation completes and a Blank_Slot is correct, THE Editor SHALL apply a green background highlight to that Blank_Slot line
2. WHEN validation completes and a Blank_Slot is incorrect, THE Editor SHALL apply a red background highlight to that Blank_Slot line
3. WHEN the student modifies a Blank_Slot after receiving feedback, THE Editor SHALL clear the green or red highlight on that specific Blank_Slot
4. THE Editor SHALL maintain feedback highlights on unmodified Blank_Slots while the student edits other Blank_Slots

### Requirement 7: Lesson File Format Migration

**User Story:** As a curriculum developer, I want to convert existing lesson step files to the new blank marker format, so that all lessons use the fill-in-the-blank system.

#### Acceptance Criteria

1. THE Step_Files in `lessons/en/` SHALL use the `# __BLANK__` marker format with embedded Expected_Answers for all regular steps (non-challenge)
2. THE Step_Files in `lessons/vi/` SHALL use the same `# __BLANK__` marker format with Expected_Answers matching the corresponding English step
3. THE Challenge_Step files SHALL remain in free-form format with no Blank_Markers
4. WHEN a Step_File uses the new Blank_Marker format, THE Lesson_Parser SHALL not require a separate solution file from `lessons/solutions/` for that step

### Requirement 8: Hearts System Integration

**User Story:** As a student, I want the hearts and hint system to work the same way with fill-in-the-blank lessons, so that my progress is tracked consistently.

#### Acceptance Criteria

1. WHEN all Blank_Slots in a step are correct and no hint or solution was used, THE StepProgressBar SHALL award one full heart
2. WHEN all Blank_Slots in a step are correct and a hint was used, THE StepProgressBar SHALL award half a heart
3. WHEN all Blank_Slots in a step are correct and the solution was used, THE StepProgressBar SHALL award zero hearts
4. WHEN the student clicks the Solution button for a fill-in-the-blank step, THE Editor SHALL populate all Blank_Slots with their Expected_Answers
5. WHEN the student submits with one or more incorrect Blank_Slots, THE StepProgressBar SHALL increment the error count and enable hint and solution buttons according to existing thresholds

### Requirement 9: Bilingual Support

**User Story:** As a student using the Vietnamese interface, I want fill-in-the-blank lessons to work identically in both languages, so that my learning experience is consistent.

#### Acceptance Criteria

1. THE Lesson_Parser SHALL load Step_Files from the language-specific folder (`lessons/en/` or `lessons/vi/`) based on the current language setting
2. THE Editor SHALL display Blank_Slot placeholder text in the current language (English or Vietnamese)
3. THE Blank_Validator SHALL validate student input against the Expected_Answers embedded in the language-specific Step_File
4. WHEN the student switches language while a lesson is active, THE Editor SHALL reload the current step from the new language folder
