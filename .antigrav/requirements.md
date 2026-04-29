# 📋 Requirements: Lesson Feature as a Game (Hearts & Challenge System)

## 1. Feature Overview
Migration of the complete interactive game mechanics from the April 25, 2026 backup branch into the main AI Education codebase. The curriculum turns standard steps into achievement thresholds driven by strict scoring mechanisms.

## 2. Layout & UI Restructuring
*   **Lessons Column**: 
    *   The primary "Examples" tab/column in the Learning Hub is repurposed into the main **Lessons** column.
    *   This column will serve as the host for active game modules and challenge tracking.
*   **Expandable Examples**: 
    *   The original curriculum examples will become a secondary, collapsible component tucked away at the bottom/side of the main interface to declutter focus.

## 3. Hearts System & Progression Mechanics
*   **Heart Scoring**:
    *   Completing an incremental step correctly awards **+1 Heart** (❤️).
    *   Maximum Hearts earned matches the total steps in the lesson (e.g. 5 steps = 5 ❤️).
*   **Retry Constraints**:
    *   Incorrect submissions deduct **1 Heart**.
    *   As long as Hearts > 0, the student is allowed to modify and resubmit their script safely without losing progress.
*   **Failure Threshold**:
    *   Dropping to **0 Hearts** invokes a hard "Game Over" constraint, clearing local state and resetting progression back to Step 1.

## 4. Strict Verification & UI Guardrails
*   **Smart Code Comparison**:
    *   Executes automated standard normalization algorithms mapping raw student code against hidden predefined constraints.
*   **Access Protections**:
    *   Disables access permissions for immediate "Direct Solution/Hint" lookups inside isolated core test boundaries.

## 5. Visual Completion Badges
*   **Acceptance State**:
    *   Active Checkmarks (✅) alongside customized border gradients.
