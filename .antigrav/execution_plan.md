# 🚀 Execution Plan: KDI Story Mode Implementation

## Phase 1: Hub UI & Lesson Navigator (Column 1)
*   **Step 1.1**: Add `tabLessons` to the `hubStackedWidget` in Running Mode.
*   **Step 1.2**: Design the `LessonNavigator` widget (Navy/Gold theme) to replace the list view when a lesson is active.
*   **Step 1.3**: Implement the "Socratic Hint" and "Show Solution" buttons with Heart-penalty logic.

## Phase 2: Story Playground (Column 3)
*   **Step 2.1**: Create `StoryCanvas` (a custom QWidget) that can overlay or replace the Camera feed.
*   **Step 2.2**: Implement the **KDI Hatchling Sprite Engine**. Load the mascot as a series of states (Idle, Move, Success, Error).
*   **Step 2.3**: Build the "Action Signal" bridge. When code runs, the canvas intercepts specific commands to trigger robot animations.

## Phase 3: The Hearts & Grading System
*   **Step 3.1**: Create a `GradeManager` class to track current hearts (❤️x5) and total XP.
*   **Step 3.2**: Implement the "Strict Validation" loop. Use a QTimer to scan the Editor text and block the "Next Step" button until the condition is met.
*   **Step 3.3**: Design the "Lesson Complete" overlay with the final Star rating based on remaining hearts.

## Phase 4: Content Integration (The Story Wrapper)
*   **Step 4.1**: Create the first "Chapter Story" by wrapping the `face_detection.py` example.
*   **Step 4.2**: Test the full "Story Round" flow: Start Lesson -> Step-by-Step Code -> Robot Reactions -> Final Grade.
