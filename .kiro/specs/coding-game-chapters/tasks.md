# Implementation Plan: Coding Game Chapters

## Overview

Implement a gamified lesson-based coding experience in the AI Coding Lab. The system follows a Lesson Pack → Lesson → Round hierarchy with Guided (drag-and-drop), Explore (parameter tweaking), and Challenge (build from scratch) rounds. When lesson mode is active, all 3 columns of the Running Mode layout are used: left (block palette/hints), center (game board/editor), right (pixel visualization scene with animated mascot). The implementation builds incrementally: core engine logic first, then pixel scene and mascot, then UI components and round widgets, then main.py integration with LessonModeManager, then content and translations.

## Tasks

- [x] 1. Implement Game Engine core logic (`src/modules/courses/game_engine.py`)
  - [x] 1.1 Create `StarGrader` class with `grade()` and `get_thresholds()` methods
    - Implement default thresholds (3★=0 mistakes, 2★=1-2, 1★=3+) and custom threshold support
    - Return rating 1-3 inclusive; monotonically non-increasing with mistake count
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ]* 1.2 Write property test for `StarGrader` (Property 3: Star grading monotonicity)
    - **Property 3: Star grading is monotonically non-increasing with mistakes**
    - Use Hypothesis to generate arbitrary non-negative mistake counts and valid threshold configs
    - Verify rating is 1-3 inclusive and `grade(m1) >= grade(m2)` when `m1 < m2`
    - **Validates: Requirements 3.1, 3.3**

  - [x] 1.3 Create `ProgressTracker` class with load/save/get/set methods
    - Implement `load()`, `save()`, `get_round_stars()`, `set_round_stars()` (max invariant)
    - Implement `is_lesson_complete()`, `is_round_complete()`, `get_unlocked_lessons()`, `unlock_next_lesson()`, `initialize_pack()`
    - Handle missing file (create fresh), corrupted JSON (backup + fresh), schema mismatch (merge with defaults)
    - Progress file path: `game/progress.json`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [ ]* 1.4 Write property test for `ProgressTracker` best-star persistence (Property 4)
    - **Property 4: Best star rating persistence (max invariant)**
    - Use Hypothesis to generate sequences of star ratings (1-3) applied to the same round
    - Verify stored `best_stars` always equals the maximum in the sequence
    - **Validates: Requirements 3.5, 3.6**

  - [ ]* 1.5 Write property test for aggregate star computation (Property 5)
    - **Property 5: Aggregate star computation**
    - Generate three round ratings (0-3 each), verify sum is in range 0-9
    - **Validates: Requirements 3.7**

  - [ ]* 1.6 Write property test for progress serialization round-trip (Property 13)
    - **Property 13: Progress serialization round-trip**
    - Generate valid progress states, serialize via `save()`, deserialize via `load()`, verify equivalence
    - **Validates: Requirements 8.2, 8.3, 8.4, 8.6**

  - [ ]* 1.7 Write property test for corrupted progress recovery (Property 14)
    - **Property 14: Corrupted progress recovery**
    - Generate invalid JSON strings and malformed dicts, verify `load()` returns valid default state without exception
    - **Validates: Requirements 8.7**

  - [x] 1.8 Create `LessonPackLoader` class with `load_all()` and validation methods
    - Implement `_validate_pack()`, `_validate_lesson()`, `_validate_rounds()` for all required fields
    - Scan `src/modules/courses/lessons/` directory, parse JSON, skip invalid files with console logging
    - Include `scene_effect` as required field in explore round validation
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_

  - [ ]* 1.9 Write property test for lesson definition validation (Property 1)
    - **Property 1: Lesson definition validation accepts exactly valid structures**
    - Generate dicts with/without required fields at pack, lesson, and round levels
    - Include `scene_effect` field in explore round validation
    - Verify acceptance iff all required fields present
    - **Validates: Requirements 1.3, 1.4, 1.5, 1.6, 1.7**

  - [ ]* 1.10 Write property test for invalid JSON resilience (Property 2)
    - **Property 2: Invalid JSON resilience**
    - Generate invalid JSON strings and dicts missing required fields mixed with valid entries
    - Verify invalid entries excluded without exception, valid entries still loaded
    - **Validates: Requirements 1.9**

  - [x] 1.11 Create `GameStateManager` class with navigation and round management
    - Implement `select_pack()`, `select_lesson()`, `start_round()`, `record_mistake()`, `complete_round()`, `get_current_lesson_data()`, `get_current_round_data()`, `reset_mistakes()`
    - Enforce sequential round unlock: Explore after Guided, Challenge after Explore
    - _Requirements: 7.2, 7.3, 7.4, 7.7_

  - [ ]* 1.12 Write property test for sequential round unlock enforcement (Property 10)
    - **Property 10: Sequential round unlock enforcement**
    - Generate lesson progress states, verify Explore accessible iff Guided completed, Challenge iff Explore completed
    - **Validates: Requirements 7.4**

  - [ ]* 1.13 Write property test for lesson completion triggers next unlock (Property 12)
    - **Property 12: Lesson completion triggers next unlock**
    - Verify that completing all 3 rounds unlocks the next sequential lesson in the pack
    - **Validates: Requirements 7.3**

  - [ ]* 1.14 Write property test for lesson card state computation (Property 11)
    - **Property 11: Lesson card state computation**
    - Generate lesson progress, verify state is "locked"/"available"/"completed" based on unlock list and round completion
    - **Validates: Requirements 7.1, 7.5**

- [ ] 2. Checkpoint — Ensure all game engine tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 3. Implement Pixel Mascot (`src/modules/courses/pixel_mascot.py`) — NEW
  - [ ] 3.1 Create `MascotState` enum and `PixelMascot` class
    - Define states: IDLE, HAPPY, SAD, CELEBRATING, THINKING, POINTING
    - Implement `set_state()`, `draw()`, `_advance_frame()`, `_build_frames()`, `_draw_pixel_grid()`
    - Frame-based animation with QTimer (~150ms interval, ~6.7 FPS)
    - Build pixel art frame data for each state as lists of (x, y, color) tuples
    - Standard size ~250px, small size ~180px
    - Idle: gentle breathing/bobbing loop; Happy: bounce (play once → idle); Sad: shake (play once → idle); Celebrating: victory dance (play once → idle); Thinking: head tilt with thought bubble (loop); Pointing: arm gesture (play once → idle)
    - _Requirements: 13.1, 13.2, 13.3, 13.8_

  - [ ]* 3.2 Write property test for mascot state transitions (Property 19)
    - **Property 19: Mascot state transitions**
    - Generate sequences of game events (correct_drop, incorrect_drop, round_complete, hint_revealed)
    - Verify mascot transitions to correct state for each event
    - **Validates: Requirements 13.4, 13.5, 13.6, 13.7**

- [ ] 4. Implement Pixel Visualization Scene (`src/modules/courses/pixel_scene.py`) — NEW
  - [ ] 4.1 Create `PixelScene` widget
    - QPainter-rendered pixel art game world for the right column
    - Themed backgrounds: "camera_studio", "photo_lab", "ai_lab", "robot_workshop", "default"
    - Integrate `PixelMascot` as central element, drawn via `paintEvent`
    - Support visual effect overlays: brightness (lighten/darken scene), rotation (rotate scene elements), grayscale (desaturate scene), blur (soften scene)
    - `set_effect(effect_type, value)` for real-time parameter feedback from Explore Round
    - `clear_effect()` to remove overlays
    - `set_theme(theme)` to change background per Lesson_Pack
    - Scale proportionally for Standard (1280×800) and Small (1024×600) modes
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.7_

- [ ] 5. Implement Mascot Widget and Hint Panel (text-based, for left column)
  - [x] 5.1 Create `MascotMessage` widget (`src/modules/courses/mascot_widget.py`)
    - Reusable QFrame with speech bubble text for left column panels
    - Support message styles: info, success, error, hint
    - Support `update_resolution(is_small)` — used in story and hint panels
    - _Requirements: 13.9, 13.10, 13.11_

  - [ ]* 5.2 Write property test for mascot message category selection (Property 17)
    - **Property 17: Mascot message category selection**
    - Verify 3★ → celebratory, 2★ → good, 1★ → encouraging message
    - **Validates: Requirements 13.10, 13.11**

  - [x] 5.3 Create `HintPanel` widget (`src/modules/courses/hint_panel.py`)
    - Left column widget for Challenge Round with sequential hint reveal
    - `set_hints()`, `reveal_next()`, `reset()` methods
    - Emit `hint_revealed` signal when hint shown (triggers mascot pointing in PixelScene)
    - Display `hint_categories` as persistent guidance note
    - Disable hint button when all hints revealed
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

  - [ ]* 5.4 Write property test for sequential hint reveal (Property 16)
    - **Property 16: Sequential hint reveal**
    - Generate hint arrays of length 1-3, verify K reveals show first K hints in order, N reveals → no more hints
    - **Validates: Requirements 10.2, 10.5**

- [ ] 6. Checkpoint — Ensure pixel scene, mascot, and hint panel work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement Block Palette and Drop Zone Board — NEW
  - [ ] 7.1 Create `BlockPalette` widget (`src/modules/courses/block_palette.py`)
    - Left column widget for Guided Round
    - Display draggable `DraggableFunctionBlock` widgets (correct + distractors) in shuffled order
    - Clear, attractive vertical layout with category colors
    - `setup()` creates blocks from LIBRARY_FUNCTIONS, `remove_block()` removes after correct placement
    - _Requirements: 4.3, 4.4, 14.1, 14.2_

  - [ ] 7.2 Create `DropZone` widget and `DropZoneBoard` (`src/modules/courses/drop_zone_board.py`)
    - Center column widget for Guided Round — visual puzzle-like game board
    - DropZone: large, colorful, numbered rectangle accepting MIME text drops
    - `mark_correct()` for green highlight, `mark_error()` for red flash/shake animation
    - DropZoneBoard: arranges drop zones in attractive layout, validates drops against expected order
    - Emit `correct_drop` and `incorrect_drop` signals for mascot reactions
    - Emit `all_zones_filled` when round complete
    - _Requirements: 4.1, 4.2, 4.5, 4.6, 4.7, 4.8, 4.9, 14.4, 14.6_

  - [ ]* 7.3 Write property test for drop zone block validation (Property 6)
    - **Property 6: Drop zone block validation**
    - Generate expected block IDs and dragged block IDs, verify acceptance iff exact match
    - **Validates: Requirements 4.4, 4.5, 14.6**

  - [ ]* 7.4 Write property test for guided round block set composition (Property 7)
    - **Property 7: Guided round block set composition**
    - Generate correct_blocks and distractor_blocks arrays, verify union is exact, drop zone count equals template_steps length
    - **Validates: Requirements 4.3, 4.8**

- [ ] 8. Implement Round Widgets (`src/modules/courses/round_widgets.py`)
  - [x] 8.1 Create `ExploreRoundWidget`
    - Pre-filled code in QScintilla with only editable parameters modifiable
    - Display Puzzle_Target prominently with mascot message
    - Run button to execute code, Submit button to check parameters
    - Emit `param_changed(effect_type, value)` signal for PixelScene real-time feedback
    - Increment mistakes on wrong submission, emit `mistake_made` for mascot sad reaction
    - Emit `round_complete` when parameters match target
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

  - [ ]* 8.2 Write property test for explore round parameter validation (Property 8)
    - **Property 8: Explore round parameter validation**
    - Generate parameter values and puzzle targets, verify submission succeeds iff all values match
    - **Validates: Requirements 5.6, 5.7**

  - [x] 8.3 Create `ChallengeRoundWidget`
    - Blank template in editor with placeholder comments
    - Submit validates code against expected blocks and parameters
    - Emit `mistake_made` for mascot sad reaction, `round_complete` for mascot celebration
    - Reuse existing ghost block system and smart indentation
    - _Requirements: 6.1, 6.2, 6.3, 6.5, 6.6, 6.7, 6.8, 14.3, 14.5_

  - [ ]* 8.4 Write property test for challenge round code validation (Property 9)
    - **Property 9: Challenge round code validation**
    - Generate code strings and expected block/parameter specs, verify validation passes iff correct order and values
    - **Validates: Requirements 6.6, 6.7**

- [ ] 9. Checkpoint — Ensure all round widget and board tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement Lesson Mode Manager (`src/modules/courses/lesson_mode_manager.py`) — NEW
  - [ ] 10.1 Create `LessonModeManager` class
    - Accept references to mainSplitter, hubContainer, middlePanel, camera/results panel
    - `enter_lesson_mode()`: save current column widget references, hide normal widgets, show lesson widgets (left_stack, center_stack, pixel_scene) in the splitter
    - `exit_lesson_mode()`: hide lesson widgets, restore and show saved normal widgets
    - `set_left_content(content_type)`: switch left column QStackedWidget — 'palette' (Round 1), 'hints' (Round 3), 'navigation' (Round 2), 'list' (browsing)
    - `set_center_content(content_type)`: switch center column — 'board' (Round 1), 'editor' (Rounds 2-3)
    - Track `_is_lesson_mode` flag to prevent double enter/exit
    - Handle edge cases: widget references lost, redundant calls
    - _Requirements: 9.5, 9.6, 9.8, 9.10_

- [ ] 11. Implement Lesson Panel UI (`src/modules/courses/game_panel.py`)
  - [x] 11.1 Create `CompletionDots` widget
    - Horizontal row of 3 dots (○ gray / ● green) representing Guided, Explore, Challenge round completion
    - Support `is_small` resolution scaling
    - _Requirements: 7.1_

  - [x] 11.2 Create `PackHeader` widget
    - Section header displaying pack title, icon, theme color
    - Display `story_intro` / `story_intro_vi` with mascot message
    - Support bilingual content and resolution scaling
    - _Requirements: 2.5, 9.3_

  - [x] 11.3 Create `LessonCard` widget
    - Card with title, description, CompletionDots, "Start Lesson" button
    - Three visual states: locked (grayed + lock icon), available (highlighted + clickable), completed (stars + all dots green)
    - Emit `start_clicked(pack_id, lesson_id)` signal
    - Show aggregate star count (e.g., "7/9 ★")
    - _Requirements: 3.7, 7.1, 7.5, 7.6, 9.4_

  - [x] 11.4 Create `LessonListPage` — flat scrollable list with PackHeaders and LessonCards
    - Scroll area with PackHeader section dividers and LessonCard items grouped by pack
    - Similar layout pattern to the existing Examples tab
    - _Requirements: 9.2, 9.3, 9.4_

  - [x] 11.5 Create `StoryNarrativePage`
    - Story text display in left column with narrative text and "Start" button
    - Bilingual story text support
    - Pixel mascot shows in PixelScene (right column) in pointing animation during story
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 11.6 Create `LessonPanel` main coordinator — UPDATED
    - Coordinate with `LessonModeManager` for full-layout lesson mode
    - `start_lesson()`: activate full-layout mode, set pixel scene theme, show story
    - `start_round()`: configure all 3 columns via LessonModeManager for the given round type
    - `exit_lesson()`: deactivate lesson mode, restore normal Running Mode
    - Emit `enter_lesson_mode` / `exit_lesson_mode` signals for main.py
    - Wire round completion signals → star grading → progress saving → mascot celebration → next round/lesson unlock
    - Wire `mistake_made` signals → mascot sad animation
    - Wire `correct_drop` signals → mascot happy animation
    - Wire `hint_revealed` signals → mascot pointing animation
    - Wire `param_changed` signals → PixelScene.set_effect()
    - `retranslate(strings)` for bilingual support
    - `update_resolution(is_small)` for dual resolution (updates PixelScene, mascot, all panels)
    - _Requirements: 2.4, 4.5, 4.6, 4.7, 5.4, 5.6, 5.7, 6.5, 6.6, 6.7, 9.5, 9.6, 9.7, 9.8, 9.9, 11.1, 11.4, 12.1, 12.2, 12.3, 12.4, 13.4, 13.5, 13.6, 13.7_

  - [ ]* 11.7 Write property test for bilingual content selection (Property 15)
    - **Property 15: Bilingual content selection**
    - Generate content objects with EN/VI fields, verify correct field returned for each language
    - **Validates: Requirements 2.3, 10.6, 11.3, 13.9**

  - [ ]* 11.8 Write property test for library function filtering (Property 18)
    - **Property 18: Library function filtering**
    - Generate subsets of function IDs from LIBRARY_FUNCTIONS, verify filtering returns exactly those IDs with correct colors/icons
    - **Validates: Requirements 14.2**

- [ ] 12. Checkpoint — Ensure all UI component tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Integrate Lesson Panel into `main.py` — UPDATED for full-layout mode
  - [x] 13.1 Add Lesson tab button and page to Learning Hub
    - Add `tabLesson` QPushButton with 📖 icon to `hubTabsLayout` (alongside tabExamples, tabFunctions, tabWorkspace)
    - Add `pageLesson` QWidget to `hubStackedWidget`
    - Wire tab click to `_switch_hub_tab()` with new index for pageLesson
    - _Requirements: 9.1_

  - [ ] 13.2 Create LessonModeManager and wire full-layout mode in main.py — NEW
    - Import and instantiate `LessonModeManager` with refs to `mainSplitter`, `hubContainer`, `middlePanel`, camera/results panel
    - Create `PixelScene` widget, `BlockPalette`, `DropZoneBoard`, lesson left/center QStackedWidgets
    - Connect `LessonPanel.enter_lesson_mode` → `LessonModeManager.enter_lesson_mode()`
    - Connect `LessonPanel.exit_lesson_mode` → `LessonModeManager.exit_lesson_mode()`
    - _Requirements: 9.5, 9.6, 9.10_

  - [ ] 13.3 Wire mascot reactions and pixel scene feedback in main.py — NEW
    - Connect `DropZoneBoard.correct_drop` → `PixelMascot.set_state(HAPPY)`
    - Connect `DropZoneBoard.incorrect_drop` → `PixelMascot.set_state(SAD)`
    - Connect round `round_complete` signals → `PixelMascot.set_state(CELEBRATING)`
    - Connect `HintPanel.hint_revealed` → `PixelMascot.set_state(POINTING)`
    - Connect `ExploreRoundWidget.param_changed` → `PixelScene.set_effect()`
    - Connect `mistake_made` signals → `PixelMascot.set_state(SAD)`
    - _Requirements: 4.5, 4.6, 4.7, 5.4, 5.6, 5.7, 6.5, 6.6, 10.3, 13.4, 13.5, 13.6, 13.7, 16.5_

  - [x] 13.4 Wire LessonPanel into `retranslate_ui()` and `refresh_ui_resolution()`
    - Call `lesson_panel.retranslate(strings)` in `retranslate_ui()`
    - Call `lesson_panel.update_resolution(is_small)` in `refresh_ui_resolution()`
    - Include PixelScene and PixelMascot in resolution updates
    - _Requirements: 11.1, 11.4, 12.1_

- [x] 14. Implement new Function Library blocks
  - [x] 14.1 Create `Filter_Target_Class` function in `src/modules/library/functions/ai_vision_blocks.py`
    - Filter YOLO predictions to keep only a specific target class
    - Signature: `Filter_Target_Class(predictions, target_class)` → filtered predictions list
    - _Requirements: 15.1 (supports Lesson 4 content)_

  - [x] 14.2 Create `Get_BoundingBox_Center` function in `src/modules/library/functions/ai_vision_blocks.py`
    - Extract center X,Y coordinates from bounding box predictions
    - Signature: `Get_BoundingBox_Center(predictions)` → `(center_x, center_y)`
    - _Requirements: 15.1 (supports Lesson 5 content)_

  - [x] 14.3 Create `Get_BoundingBox_Area` function in `src/modules/library/functions/ai_vision_blocks.py`
    - Calculate bounding box area from predictions
    - Signature: `Get_BoundingBox_Area(predictions)` → area (int)
    - _Requirements: 15.1 (supports Lesson 9 content)_

  - [x] 14.4 Create `Draw_Target_Dot` function in `src/modules/library/functions/drawing_blocks.py`
    - Draw a colored dot at specified coordinates on a frame
    - Signature: `Draw_Target_Dot(frame, center_x, center_y)` → frame
    - _Requirements: 15.1 (supports Lesson 5 content)_

  - [x] 14.5 Create `Init_Robot_Connection`, `Send_Robot_Command`, `Close_Robot` functions in `src/modules/library/functions/robotics.py`
    - `Init_Robot_Connection(port, baudrate)` → serial connection object
    - `Send_Robot_Command(serial, command)` → None (sends command string)
    - `Close_Robot(serial)` → None (closes serial connection)
    - _Requirements: 15.1 (supports Lessons 7-8 content)_

  - [x] 14.6 Register all 7 new functions in `src/modules/library/definitions.py`
    - Add entries for `Filter_Target_Class`, `Get_BoundingBox_Center`, `Get_BoundingBox_Area`, `Draw_Target_Dot`, `Init_Robot_Connection`, `Send_Robot_Command`, `Close_Robot`
    - Include `desc`, `desc_vi`, `params`, `returns`, `usage`, `import_statement`, `source_func`, `source_module` for each
    - Place in appropriate categories: AI Vision Core, Display & Dashboard, Robotics
    - _Requirements: 14.1, 14.2_

  - [x] 14.7 Add translation key mappings for new functions in `src/modules/function_library.py`
    - Add entries to `_FN_DESC_KEY_MAP` for all 7 new function IDs
    - _Requirements: 11.1_

- [ ] 15. Checkpoint — Ensure new library functions work and definitions are valid
  - Ensure all tests pass, ask the user if questions arise.

- [x] 16. Create Lesson Definition JSON files
  - [x] 16.1 Create Camera Basics pack (`src/modules/courses/lessons/camera_basics.json`)
    - Pack with at least 3 lessons: Hello Camera, Live Feed Loop, Camera Cleanup
    - Include `scene_theme: "camera_studio"` at pack level
    - Include `scene_effect` in each explore round definition
    - Lesson 1: Init_Camera, Get_Camera_Frame, Show_Image (distractors: Close_Camera, apply_blur)
    - Lesson 2: Add while-True loop for live feed (distractors: detect_edges)
    - Lesson 3: Full camera lifecycle with Close_Camera (distractors: resize_image)
    - Each lesson: story/story_vi, guided/explore/challenge rounds, star_thresholds, hints/hints_vi
    - Use only Camera, Display & Dashboard, and Variables category blocks
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8_

  - [x] 16.2 Create Image Processing pack (`src/modules/courses/lessons/image_processing.json`)
    - Pack covering convert_to_gray, apply_blur, detect_edges, flip_image, adjust_brightness
    - Include `scene_theme: "photo_lab"` and `scene_effect` per explore round (brightness, grayscale, blur)
    - Progressive lessons building on camera basics
    - Each lesson with bilingual stories, all three round types, hints
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 1.7_

  - [x] 16.3 Create AI Vision pack (`src/modules/courses/lessons/ai_vision.json`)
    - Pack covering Load_ONNX_Model, Run_ONNX_Model, Draw_Detections_MultiClass, Filter_Target_Class, Get_BoundingBox_Center
    - Include `scene_theme: "ai_lab"`
    - Intermediate-level lessons building toward object detection pipeline
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 1.7_

  - [x] 16.4 Create Robot Control pack (`src/modules/courses/lessons/robot_control.json`)
    - Pack covering Init_Robot_Connection, Send_Robot_Command, Get_BoundingBox_Area, Close_Robot
    - Include `scene_theme: "robot_workshop"`
    - Advanced-level lessons building toward the Smart Follow Me Robot
    - Final lesson as blank challenge (build everything from scratch)
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 17. Add translation keys to `src/modules/translations.py`
  - Add all lesson-related translation keys for both EN and VI
    - Tab and navigation: `TAB_LESSON`, `LESSON_TITLE`, `LESSON_BACK`, `LESSON_ROUND_INDICATOR`, `LESSON_MISTAKES`, `LESSON_STARS`
    - Round labels: `LESSON_ROUND_GUIDED`, `LESSON_ROUND_EXPLORE`, `LESSON_ROUND_CHALLENGE`
    - Buttons: `LESSON_START`, `LESSON_NEXT_ROUND`, `LESSON_SUBMIT`, `LESSON_RUN`, `LESSON_HINT`, `LESSON_REPLAY`, `LESSON_CONTINUE`, `LESSON_NO_MORE_HINTS`, `LESSON_EXIT`
    - Mascot messages: `MASCOT_PERFECT`, `MASCOT_GOOD`, `MASCOT_TRY_AGAIN`, `MASCOT_MISTAKE`, `MASCOT_LOCKED`, `MASCOT_HINT_CATEGORY`
    - Lesson states: `LESSON_LOCKED`, `LESSON_AVAILABLE`, `LESSON_COMPLETED`
    - Pixel scene: `PIXEL_SCENE_TITLE`
    - New function descriptions: `FN_FILTER_TARGET_CLASS`, `FN_GET_BOUNDINGBOX_CENTER`, `FN_GET_BOUNDINGBOX_AREA`, `FN_DRAW_TARGET_DOT`, `FN_INIT_ROBOT_CONNECTION`, `FN_SEND_ROBOT_COMMAND`, `FN_CLOSE_ROBOT`
  - _Requirements: 11.1, 11.2, 11.3_

- [ ] 18. Final integration and wiring
  - [x] 18.1 Wire round completion flow end-to-end
    - GuidedRound complete → star grading → progress save → mascot celebrating → show completion message → enable "Next Round"
    - ExploreRound complete → star grading → progress save → mascot celebrating → show completion message → enable "Next Round"
    - ChallengeRound complete → star grading → progress save → mascot celebrating → lesson complete → unlock next lesson → return to list → exit lesson mode
    - Language switch during active lesson updates all displayed text without losing state
    - _Requirements: 3.4, 3.5, 3.6, 4.7, 5.7, 6.7, 7.3, 7.4, 8.5, 11.4_

  - [ ]* 18.2 Write unit tests for navigation flow and integration
    - Test lesson list → story → guided → explore → challenge → lesson list flow
    - Test back button at each navigation depth (triggers lesson mode exit)
    - Test locked lesson click shows prerequisite message
    - Test round replay for improving star rating
    - Test lesson tab existence in hub
    - Test full-layout mode activation and deactivation
    - Test pixel scene theme changes per pack
    - _Requirements: 7.6, 7.7, 9.1, 9.5, 9.6, 9.7, 9.8_

  - [ ]* 18.3 Write smoke tests for lesson pack content
    - Verify all JSON files in `src/modules/courses/lessons/` exist and have required fields (including scene_effect)
    - Verify Camera Basics pack has ≥ 3 lessons
    - Verify each pack has a `scene_theme` field
    - _Requirements: 15.1, 16.2_

- [ ] 19. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document (Properties 1-19)
- Unit tests validate specific examples and edge cases
- The design uses Python (PyQt5) throughout — all code examples and implementations use Python
- New library functions (14.1-14.5) must be implemented before lesson JSON files (16.x) that reference them
- The `src/modules/courses/` directory and `kdi_hatchling.png` already exist; `lessons/` subdirectory exists but is empty
- NEW components: `pixel_mascot.py`, `pixel_scene.py`, `lesson_mode_manager.py`, `block_palette.py`, `drop_zone_board.py`
- The existing 3-column QSplitter layout is NOT modified — only the content of each column is swapped by LessonModeManager
- The pixel mascot is code-drawn via QPainter (not a static PNG) for animation support
- Task numbering has been updated to reflect the new component ordering: pixel scene/mascot early (tasks 3-4), then UI components, then integration
