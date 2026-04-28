# Requirements Document

## Introduction

Add a gamified, lesson-based coding experience to the AI Coding Lab, organized as Lesson Packs → Lessons → Rounds. Each Lesson Pack groups skills by theme (e.g., Camera Pack, Image Processing Pack, AI Vision Pack). Each Lesson teaches a specific concept through three progressive rounds: Guided (drag-and-drop with drop zones and distractors), Explore (parameter tweaking to match a target), and Challenge (build from scratch using the full Function Library). A per-round star grading system (based on wrong attempts) motivates careful thinking.

When lesson mode is active, the system takes over ALL THREE COLUMNS of the existing Running Mode QSplitter layout: the left column becomes the lesson list (browsing) or block palette/hints (playing), the center column becomes the playground (drop zone board for Round 1, code editor for Rounds 2-3), and the right column becomes a Pixel Visualization Scene with an animated KDI Hatchling pixel mascot. When the student exits lesson mode, the normal Running Mode content returns to all three columns.

The KDI Hatchling mascot is rendered as a code-drawn pixel art character (via QPainter) with multiple animation states (idle, happy, sad, celebrating, thinking, pointing). It lives in the Pixel Visualization Scene and reacts to student actions in real time. The system reuses the existing QScintilla code editor, drag-and-drop Function Library (`DraggableFunctionBlock`, `DraggableFunctionWidget`), and module import system (`import camera; camera.Init_Camera()`).

## Glossary

- **Game_Engine**: The core module that manages Lesson Packs, Lessons, Rounds, progress tracking, star state, and grading logic for the coding game experience
- **Lesson_Pack**: A top-level thematic grouping of Lessons organized by skill area (e.g., "Camera Pack", "Image Processing Pack", "AI Vision Pack"). Each Lesson_Pack contains an ordered sequence of Lessons and a short fun narrative orientation (1-2 sentences)
- **Lesson**: A single teaching unit within a Lesson_Pack that covers one concept. Each Lesson contains exactly three Rounds (Guided, Explore, Challenge) and a variable number of code blocks depending on the concept taught
- **Round**: One of three progressive stages within a Lesson. Round types are Guided (Round 1), Explore (Round 2), and Challenge (Round 3). Each Round is independently graded with a Star_Rating
- **Guided_Round**: Round 1 of a Lesson. Displays a visual puzzle-like game board in the center column with numbered, colored rectangle drop zones. The left column shows a block palette with correct code blocks plus 1-2 distractor (wrong) blocks for drag-and-drop. The right column shows the Pixel_Visualization_Scene where the mascot reacts to correct/incorrect placements
- **Explore_Round**: Round 2 of a Lesson. The center column presents the code editor with the same code structure from the Guided_Round, requiring the student to modify parameter values to match a specific puzzle target. The right column Pixel_Visualization_Scene reacts to parameter changes (e.g., brightness changes make the scene brighter/darker, rotation rotates the scene). The left column shows the lesson list or is minimized
- **Challenge_Round**: Round 3 of a Lesson. The center column presents a blank template in the code editor where the student must find and drag the correct blocks from the full Function Library, then fill in parameters. The left column shows the hints panel with KDI Hatchling guidance. The right column shows the Pixel_Visualization_Scene with the mascot in "thinking" mode
- **Drop_Zone**: A numbered, colored rectangle slot in the Guided_Round game board (center column) where the student drags a code block. Each Drop_Zone has a label describing the expected action (e.g., "1. Initialize the camera", "2. ___", "3. ___")
- **Distractor_Block**: An incorrect code block included alongside correct blocks in the Guided_Round block palette (left column) to test the student's understanding. Dragging a Distractor_Block onto a Drop_Zone counts as one mistake
- **Puzzle_Target**: The specific expected output or parameter value that the student must achieve in the Explore_Round (e.g., "rotation = 90°", "brightness = 150")
- **Star_Rating**: A 1-to-3 star score awarded per Round based on the number of wrong attempts. Default thresholds: 3 stars = 0 mistakes, 2 stars = 1-2 mistakes, 1 star = 3+ mistakes. Thresholds may vary based on the number of blocks in the Lesson
- **Star_Threshold**: A configurable set of mistake-count boundaries for star grading per Round. Allows more lenient grading for Lessons with more blocks
- **KDI_Hatchling**: The mascot character for the coding game, rendered as a code-drawn pixel art character using QPainter. Lives in the Pixel_Visualization_Scene (right column). Has multiple animation states: idle, happy, sad, celebrating, thinking, pointing. Approximately 200-300px in size. Uses frame-based animation with QTimer
- **Pixel_Visualization_Scene**: A pixel art game world rendered in the right column (Camera+Results area) when lesson mode is active. Contains the KDI_Hatchling pixel mascot and a themed background scene. For image processing lessons, the scene can visualize effects (grayscale filter, blur, brightness changes, rotation). Rendered using QPainter on a QWidget
- **Lesson_Mode_Manager**: The component that manages the transition between normal Running Mode and lesson mode by swapping the content of all three columns in the existing QSplitter layout. Saves and restores the normal column content when entering/exiting lesson mode
- **Block_Palette**: The left column content during Guided_Round (Round 1), displaying the available draggable code blocks (correct + distractors) in a clear, attractive layout for the student to choose from
- **Story_Narrative**: A short (1-2 sentences), fun scenario text displayed at the start of each Lesson, featuring the KDI_Hatchling mascot to set context and motivation (e.g., "KDI needs your help to fix the robot's camera before the big show!")
- **Completion_Indicator**: A 3-dot visual indicator on each Lesson_Card showing the student's round completion progress within that Lesson. Each dot represents one Round (Guided, Explore, Challenge). Gray dots (○) represent incomplete Rounds, green dots (●) represent completed Rounds
- **Progress_Tracker**: The component that persists the student's completion state across Lesson Packs, Lessons, and Rounds, including star ratings per round, stored as a local JSON file
- **Lesson_Panel**: The UI panel within the Running Mode that displays the lesson interface. In browsing mode, it occupies the left column (Learning Hub area). When a lesson is active, it coordinates all three columns via the Lesson_Mode_Manager
- **Lesson_Card**: A clickable UI widget representing a single Lesson in the Lesson tab's flat list, showing the lesson title, description/objectives, a 3-dot Completion_Indicator (showing round progress), and a "Start Lesson" button. Similar in style to the Example cards in the Examples tab
- **Pack_Header**: A section header/group divider in the Lesson tab's flat list that displays the Lesson_Pack title, icon, and theme color, visually grouping the Lesson_Cards belonging to that pack (similar to level badges in the Examples tab)
- **Lesson_Definition_File**: A JSON file in the `src/modules/courses/lessons/` directory that defines a Lesson_Pack's metadata, lessons, and rounds with all associated content (stories, blocks, targets, hints, star thresholds)
- **Game_Progress_File**: A local JSON file (`game/progress.json`) that stores the student's completion state, star ratings per round, and unlocked lessons/packs
- **Function_Library**: The existing drag-and-drop library panel containing categorized `DraggableFunctionBlock` widgets. Used directly in the Challenge_Round and as the source for curated block subsets in the Guided_Round

## Requirements

### Requirement 1: Lesson Pack Structure and Content Organization

**User Story:** As a student, I want coding lessons organized into themed packs with a clear progression path, so that I can learn Python and AI vision skills step by step through focused skill groups.

#### Acceptance Criteria

1. THE Game_Engine SHALL support a three-tier hierarchy: Lesson_Pack → Lesson → Round, where each Lesson_Pack contains one or more Lessons and each Lesson contains exactly three Rounds (Guided_Round, Explore_Round, Challenge_Round)
2. THE Game_Engine SHALL load Lesson_Pack definitions from Lesson_Definition_File JSON files stored in the `src/modules/courses/lessons/` directory
3. THE Lesson_Definition_File SHALL contain the following fields for each Lesson_Pack: `id`, `title`, `title_vi`, `description`, `description_vi`, `icon`, `color`, `story_intro`, `story_intro_vi`, and an ordered `lessons` array
4. THE Lesson_Definition_File SHALL contain the following fields for each Lesson: `id`, `title`, `title_vi`, `story`, `story_vi`, `block_count`, `star_thresholds`, and a `rounds` object containing `guided`, `explore`, and `challenge` definitions
5. THE `guided` round definition SHALL contain: `template_steps` (ordered array of labeled drop zone descriptions), `correct_blocks` (ordered array of code block identifiers), and `distractor_blocks` (array of 1-2 incorrect code block identifiers)
6. THE `explore` round definition SHALL contain: `code_template` (the pre-filled code from the Guided_Round), `editable_params` (array of parameter names the student can modify), `puzzle_target` (the expected parameter values or output description), and `scene_effect` (the visual effect to apply to the Pixel_Visualization_Scene, e.g., "brightness", "rotation", "grayscale")
7. THE `challenge` round definition SHALL contain: `expected_blocks` (ordered array of code block identifiers the student must find), `expected_params` (parameter values for each block), and `hint_categories` (array of Function_Library category names to guide the student)
8. WHEN the application starts, THE Game_Engine SHALL scan the `src/modules/courses/lessons/` directory and load all valid Lesson_Definition_File JSON files
9. IF a Lesson_Definition_File contains invalid JSON or missing required fields, THEN THE Game_Engine SHALL log a descriptive error message to the console and skip that file without crashing

### Requirement 2: Story Narrative with Mascot

**User Story:** As a student, I want to see a short fun story with the KDI Hatchling mascot before each lesson, so that I feel excited and curious about what I am going to learn.

#### Acceptance Criteria

1. WHEN a student selects a Lesson, THE Lesson_Panel SHALL display the Story_Narrative text (1-2 sentences) in a visually distinct, themed panel alongside the KDI_Hatchling pixel mascot in the Pixel_Visualization_Scene (right column)
2. THE Story_Narrative panel SHALL render the KDI_Hatchling pixel mascot in "pointing" animation state in the Pixel_Visualization_Scene while the story is displayed
3. THE Story_Narrative SHALL support bilingual content, displaying the `story` field when the current language is English and the `story_vi` field when the current language is Vietnamese
4. WHEN the language is switched while a Lesson is active, THE Lesson_Panel SHALL update the Story_Narrative text to the new language without losing the current navigation state
5. THE Pack_Header in the Lesson tab SHALL display the `story_intro` / `story_intro_vi` text alongside the KDI_Hatchling mascot to introduce the pack theme

### Requirement 3: Per-Round Star Grading System

**User Story:** As a student, I want to earn stars for each round based on how few mistakes I make, so that I am motivated to think carefully and try to get a perfect score.

#### Acceptance Criteria

1. WHEN a student completes a Round, THE Game_Engine SHALL calculate the Star_Rating for that specific Round based on the number of wrong attempts during that Round
2. THE Game_Engine SHALL apply the following default Star_Threshold: 3 stars for 0 mistakes, 2 stars for 1-2 mistakes, and 1 star for 3 or more mistakes
3. THE Lesson_Definition_File SHALL support a per-Lesson `star_thresholds` field that overrides the default thresholds, allowing more lenient grading for Lessons with a higher `block_count`
4. THE Lesson_Panel SHALL display the earned Star_Rating as filled star icons (gold) and empty star outlines (gray) at the completion of each Round
5. THE Progress_Tracker SHALL persist the best Star_Rating for each Round in the Game_Progress_File, keeping the highest rating across all attempts
6. WHEN a student replays a completed Round and earns a higher Star_Rating, THE Progress_Tracker SHALL update the stored rating to the new higher value
7. THE Lesson_Card SHALL display the aggregate star count across all three Rounds (e.g., "7/9 ★") as a summary of Lesson performance

### Requirement 4: Guided Round — Full-Layout Drag-and-Drop with Drop Zone Game Board

**User Story:** As a student starting a new lesson, I want a visual puzzle-like game board in the center of the screen with colorful drop zones, a block palette on the left, and an animated mascot on the right that celebrates when I get it right, so that learning feels like playing a game.

#### Acceptance Criteria

1. WHEN the Guided_Round starts, THE Lesson_Mode_Manager SHALL configure the three columns: left column shows the Block_Palette, center column shows the drop zone game board, and right column shows the Pixel_Visualization_Scene with the KDI_Hatchling mascot in idle animation
2. THE center column (drop zone game board) SHALL display a visual puzzle-like layout of numbered, colored rectangle Drop_Zones, each labeled with a description of the expected action (e.g., "1. Initialize the camera", "2. ___", "3. ___"), arranged as large, colorful, attractive slots
3. THE left column (Block_Palette) SHALL display a set of draggable code blocks containing all correct blocks for the Lesson plus 1-2 Distractor_Blocks, arranged in a randomized order with clear visual presentation
4. THE draggable code blocks in the Block_Palette SHALL reuse the visual style of the existing `DraggableFunctionBlock` widget from the Function_Library
5. WHEN a student drags a correct block from the Block_Palette onto the matching Drop_Zone, THE Lesson_Panel SHALL snap the block into place with a success visual indicator (green highlight or checkmark) AND the KDI_Hatchling pixel mascot in the Pixel_Visualization_Scene SHALL play a happy bounce animation
6. WHEN a student drags a Distractor_Block or an incorrect block onto a Drop_Zone, THE Lesson_Panel SHALL reject the drop with an error visual indicator (red flash or shake animation), increment the mistake counter by 1, AND the KDI_Hatchling pixel mascot SHALL play a sad shake animation
7. WHEN all Drop_Zones are correctly filled, THE KDI_Hatchling pixel mascot SHALL play a victory dance animation, AND THE Lesson_Panel SHALL display a round completion message with the earned Star_Rating and a "Next Round" button to proceed to the Explore_Round
8. THE number of Drop_Zones and code blocks SHALL vary per Lesson based on the `block_count` and the `template_steps` defined in the Lesson_Definition_File
9. THE Drop_Zone rectangles SHALL use distinct colors and clear numbering to be visually attractive and easy to understand for young students

### Requirement 5: Explore Round — Parameter Tweaking with Pixel Scene Feedback

**User Story:** As a student who has learned the code structure, I want to modify parameters in the code and see the pixel world react to my changes in real time, so that I understand how changing values affects the program and it feels like tuning a game world.

#### Acceptance Criteria

1. WHEN the Explore_Round starts, THE Lesson_Mode_Manager SHALL configure the three columns: left column is minimized or shows the lesson navigation, center column shows the QScintilla editor with pre-filled code, and right column shows the Pixel_Visualization_Scene with the KDI_Hatchling mascot
2. THE center column SHALL load the completed code structure from the Guided_Round into the QScintilla editor with all blocks pre-filled and only the parameter values editable
3. THE Lesson_Panel SHALL display the Puzzle_Target prominently above the editor (e.g., "Rotate the image to exactly 90°", "Set brightness to 150") alongside the KDI_Hatchling mascot
4. THE Pixel_Visualization_Scene (right column) SHALL react to parameter changes in real time based on the `scene_effect` field: brightness changes make the scene brighter/darker, rotation rotates the scene, grayscale applies a grayscale filter over the scene
5. THE Lesson_Panel SHALL provide a "Run" button that executes the student's code and displays the output in the camera/results panel for comparison against the Puzzle_Target
6. WHEN a student clicks "Submit" with parameter values that do not match the Puzzle_Target, THE Lesson_Panel SHALL increment the mistake counter by 1, the KDI_Hatchling pixel mascot SHALL play a sad shake animation, and display a hint suggesting the direction of adjustment
7. WHEN a student clicks "Submit" with parameter values that match the Puzzle_Target, THE KDI_Hatchling pixel mascot SHALL play a victory dance animation, AND THE Lesson_Panel SHALL display a round completion message with the earned Star_Rating and a "Next Round" button to proceed to the Challenge_Round
8. THE `editable_params` field in the Lesson_Definition_File SHALL specify which parameter fields the student can modify, and all other code SHALL remain read-only in the editor

### Requirement 6: Challenge Round — Build from Full Library with Hints Panel

**User Story:** As a student ready for a challenge, I want to build the code from scratch by finding blocks in the full Function Library, with hints available on the left and the mascot thinking alongside me on the right, so that I can prove I understand which functions to use.

#### Acceptance Criteria

1. WHEN the Challenge_Round starts, THE Lesson_Mode_Manager SHALL configure the three columns: left column shows the hints panel with KDI_Hatchling guidance, center column shows the QScintilla editor with a blank code template, and right column shows the Pixel_Visualization_Scene with the KDI_Hatchling mascot in thinking animation
2. THE center column SHALL display a blank code template in the QScintilla editor with placeholder comments indicating where blocks should be placed
3. THE Lesson_Panel SHALL make the full Function_Library panel accessible for the student to browse and drag blocks from (accessible via the hints panel or a toggle in the left column)
4. THE left column (hints panel) SHALL display guided hint notes from the KDI_Hatchling mascot indicating which Function_Library category to look in (based on the `hint_categories` field in the Lesson_Definition_File)
5. WHEN a student drags a correct block from the Function_Library into the correct position in the editor, THE Lesson_Panel SHALL accept the drop using the existing ghost block and smart indentation system, AND the KDI_Hatchling pixel mascot SHALL play a happy bounce animation
6. WHEN a student drags an incorrect block into the editor and submits, THE Lesson_Panel SHALL increment the mistake counter by 1, the KDI_Hatchling pixel mascot SHALL play a sad shake animation, and provide a hint
7. WHEN the student's code matches the expected block structure and parameter values, THE KDI_Hatchling pixel mascot SHALL play a victory dance animation, AND THE Lesson_Panel SHALL display a Lesson completion message with the earned Star_Rating for the Challenge_Round and the aggregate Lesson star summary
8. THE Challenge_Round SHALL reuse the existing drag-and-drop infrastructure (`DraggableFunctionBlock`, `DraggableFunctionWidget`, ghost blocks, smart indentation) without modification to the core library code

### Requirement 7: Lesson Progression and Completion Indicators

**User Story:** As a student, I want to see my progress through lessons as a visual path of dots, so that I know how far I have come and what is next.

#### Acceptance Criteria

1. EACH Lesson_Card SHALL display a Completion_Indicator as a horizontal row of 3 dots, one per Round (Guided, Explore, Challenge), where gray dots (○) represent incomplete Rounds and green dots (●) represent completed Rounds
2. WHEN a Lesson_Pack is first started, THE Game_Engine SHALL unlock only the first Lesson within that Lesson_Pack
3. WHEN a student completes all three Rounds of a Lesson, THE Game_Engine SHALL mark that Lesson as completed (all 3 dots green) and unlock the next Lesson in the Lesson_Pack
4. WITHIN a Lesson, THE Game_Engine SHALL enforce sequential Round progression: the Explore_Round unlocks only after the Guided_Round is completed, and the Challenge_Round unlocks only after the Explore_Round is completed
5. THE Lesson_Card SHALL display one of three visual states: locked (grayed out with a lock icon), available (highlighted and clickable with "Start Lesson" button), or completed (showing the aggregate Star_Rating earned across all three Rounds with all 3 dots green)
6. WHEN a student clicks a locked Lesson_Card, THE Lesson_Panel SHALL display a message from the KDI_Hatchling mascot indicating the prerequisite Lesson that must be completed first
7. THE Game_Engine SHALL allow students to replay any previously completed Round to improve the Star_Rating for that Round

### Requirement 8: Progress Persistence

**User Story:** As a student, I want my game progress to be saved automatically, so that I can continue where I left off when I reopen the application.

#### Acceptance Criteria

1. THE Progress_Tracker SHALL store progress data in a Game_Progress_File located at `game/progress.json`
2. THE Game_Progress_File SHALL contain for each Lesson_Pack: the list of unlocked Lesson IDs and the current active Lesson ID
3. THE Game_Progress_File SHALL contain for each Lesson: the completion status of each Round (boolean), the best Star_Rating for each Round (0-3), and the number of attempts per Round
4. THE Game_Progress_File SHALL contain for each Lesson_Pack: the Completion_Indicator state (array of completed/incomplete flags per Lesson)
5. WHEN a student completes a Round, earns a star rating, or unlocks a new Lesson, THE Progress_Tracker SHALL write the updated state to the Game_Progress_File within 1 second
6. WHEN the application starts, THE Progress_Tracker SHALL load the Game_Progress_File and restore the student's last known state
7. IF the Game_Progress_File does not exist or is corrupted, THEN THE Progress_Tracker SHALL create a fresh progress file with all Lesson Packs at their initial state (first Lesson unlocked)

### Requirement 9: Lesson Panel UI Integration — Full-Layout Lesson Mode

**User Story:** As a student, I want the lesson experience to use the entire screen with a game board in the center, blocks on the left, and an animated pixel world on the right, so that it feels like a real coding game and not just a sidebar.

#### Acceptance Criteria

1. THE Learning Hub SHALL include a new "Lesson" tab alongside the existing tabs, accessible via a tab button with a book icon (📖)
2. WHEN the "Lesson" tab is selected, THE Learning Hub panel SHALL display the Lesson_Panel showing a flat scrollable list of all Lesson_Cards, grouped by Lesson_Pack with Pack_Header section dividers (similar to how the Examples tab groups examples by level)
3. EACH Pack_Header SHALL display the Lesson_Pack title, icon, and theme color as a section divider above its Lesson_Cards
4. EACH Lesson_Card in the list SHALL display: the lesson title, a short description/objectives, a 3-dot Completion_Indicator (○○○ or ●○○ etc.) showing round progress, and a "Start Lesson" button (similar to the "Load" button on Example cards)
5. WHEN a student clicks "Start Lesson" on an available Lesson_Card, THE Lesson_Mode_Manager SHALL activate full-layout lesson mode: the left column content is swapped to lesson-specific content (Block_Palette for Round 1, hints panel for Round 3), the center column content is swapped to the playground (drop zone board for Round 1, code editor for Rounds 2-3), and the right column content is swapped to the Pixel_Visualization_Scene with the KDI_Hatchling pixel mascot
6. WHEN the student exits lesson mode (via Back button or lesson completion), THE Lesson_Mode_Manager SHALL restore the normal Running Mode content to all three columns (Learning Hub in left, code editor in center, camera+results in right)
7. THE Lesson_Panel SHALL display a round indicator (e.g., "Round 1/3", "Round 2/3", "Round 3/3") in the header area showing the current round within the active Lesson
8. THE Lesson_Panel SHALL include a "Back" button at each navigation depth (Round → Story → Lesson list) to allow the student to navigate backward, and exiting from the story or round level SHALL trigger the Lesson_Mode_Manager to restore normal Running Mode
9. WHILE a Round is active in the Lesson_Panel, THE Lesson_Panel SHALL display the current mistake count and the Star_Rating thresholds for that Round
10. THE existing 3-column QSplitter layout SHALL remain unchanged — the Lesson_Mode_Manager only swaps the CONTENT of each column, not the layout structure itself

### Requirement 10: Hint System for Challenge Round

**User Story:** As a student, I want guided hints when I am stuck on the Challenge Round, so that I can learn from guidance rather than giving up.

#### Acceptance Criteria

1. THE Challenge_Round definition SHALL support an ordered array of hint strings (up to 3 hints per Round) in both English (`hints`) and Vietnamese (`hints_vi`)
2. THE left column hints panel SHALL display a "Hint" button with the KDI_Hatchling mascot icon that reveals hints one at a time in sequential order
3. WHEN a student clicks the "Hint" button for the first time on a Challenge_Round, THE hints panel SHALL reveal only the first hint in a speech-bubble style panel next to the KDI_Hatchling mascot, AND the pixel mascot in the Pixel_Visualization_Scene SHALL play a pointing animation
4. WHEN a student clicks the "Hint" button again, THE hints panel SHALL reveal the next unrevealed hint in sequence
5. WHEN all hints for a Challenge_Round have been revealed, THE "Hint" button SHALL become disabled with a label indicating no more hints are available
6. THE hint text SHALL support bilingual content, displaying the English hint when the current language is English and the Vietnamese hint when the current language is Vietnamese
7. THE `hint_categories` field SHALL provide the KDI_Hatchling mascot with category-level guidance (e.g., "Look in the Camera category!") displayed as a persistent small note in the hints panel

### Requirement 11: Bilingual Support for Game Content

**User Story:** As a Vietnamese student, I want all game content (stories, challenges, hints, UI labels) displayed in my language, so that I can fully understand and enjoy the coding game.

#### Acceptance Criteria

1. THE Lesson_Panel UI labels (tab title, button text, status messages, navigation labels, mascot messages) SHALL use translation keys from `translations.py` and update when the language is switched
2. THE Lesson_Definition_File SHALL include bilingual fields for all user-facing text: `title`/`title_vi`, `description`/`description_vi`, `story`/`story_vi`, `story_intro`/`story_intro_vi`, `hints`/`hints_vi`, `puzzle_target`/`puzzle_target_vi`
3. WHEN the current language is Vietnamese, THE Lesson_Panel SHALL display all Vietnamese variants of Lesson_Pack, Lesson, Round, Story_Narrative, Puzzle_Target, and hint text
4. WHEN the language is switched while the Lesson_Panel is active, THE Lesson_Panel SHALL refresh all displayed text to the new language without losing the current navigation state or round progress

### Requirement 12: Dual Resolution Support for Game UI

**User Story:** As a student using a small 10-inch screen, I want the game interface to scale properly, so that stories, stars, drop zones, the pixel scene, and lesson cards remain readable at 1024×600 resolution.

#### Acceptance Criteria

1. WHEN `refresh_ui_resolution()` is called, THE Lesson_Panel, Pixel_Visualization_Scene, and KDI_Hatchling pixel mascot SHALL update their dimensions, font sizes, and spacing to match the current Resolution_Mode
2. WHILE Resolution_Mode is Standard (1280×800), THE Lesson_Panel SHALL render Story_Narrative text at 14px, Star_Rating icons at 24px, Drop_Zone rectangles at standard dimensions, Lesson_Card widgets at standard dimensions, and the KDI_Hatchling pixel mascot at ~250px
3. WHILE Resolution_Mode is Small (1024×600), THE Lesson_Panel SHALL render Story_Narrative text at 10px, Star_Rating icons at 18px, Drop_Zone rectangles at 80% of standard dimensions, Lesson_Card widgets at 80% of standard dimensions, and the KDI_Hatchling pixel mascot at ~180px
4. THE KDI_Hatchling pixel mascot, Pixel_Visualization_Scene, Drop_Zone rectangles, Star_Rating icons, Lesson_Card, Pack_Header, and Completion_Indicator widgets SHALL scale proportionally without clipping or overlapping in both Resolution_Modes

### Requirement 13: KDI Hatchling Pixel Mascot

**User Story:** As a student, I want a friendly animated pixel art mascot character that lives in the game world and reacts to my actions, so that the experience feels alive, fun, and personal.

#### Acceptance Criteria

1. THE KDI_Hatchling pixel mascot SHALL be rendered as code-drawn pixel art using QPainter (not a static PNG), living inside the Pixel_Visualization_Scene in the right column
2. THE KDI_Hatchling pixel mascot SHALL support the following animation states: idle (gentle breathing/bobbing), happy (bounce animation on correct action), sad (shake animation on mistake), celebrating (victory dance on round completion), thinking (head tilt with thought bubble, used during Challenge_Round), and pointing (arm gesture, used when showing hints)
3. THE pixel mascot animations SHALL use frame-based animation driven by QTimer, cycling through predefined pixel art frames for each state
4. WHEN a student places a correct block in any Round, THE pixel mascot SHALL transition to the happy animation state
5. WHEN a student makes a mistake in any Round, THE pixel mascot SHALL transition to the sad animation state
6. WHEN a student completes a Round, THE pixel mascot SHALL transition to the celebrating animation state
7. WHEN a hint is revealed in the Challenge_Round, THE pixel mascot SHALL transition to the pointing animation state
8. THE KDI_Hatchling pixel mascot SHALL render at approximately 200-300px in Standard Resolution_Mode and scale proportionally in Small Resolution_Mode
9. THE pixel mascot SHALL support bilingual celebration/encouragement text overlays that display in the current language
10. WHEN a student completes a Round with 3 stars, THE pixel mascot SHALL display a celebratory message (e.g., "Perfect! You're amazing! 🌟")
11. WHEN a student completes a Round with 1 star, THE pixel mascot SHALL display an encouraging message (e.g., "Good effort! Try again for more stars!")

### Requirement 14: Drag-and-Drop Integration with Existing Function Library

**User Story:** As a student, I want to drag code blocks from familiar colored categories into my code, so that the game feels consistent with the rest of the app and I can reuse what I already know.

#### Acceptance Criteria

1. THE Guided_Round Block_Palette (left column) SHALL present curated code blocks as `DraggableFunctionBlock` widgets with the same visual style (category color, icon, name, description) used in the existing Function_Library
2. THE Guided_Round block set SHALL be generated by filtering the existing `LIBRARY_FUNCTIONS` definitions to include only the blocks specified in the `correct_blocks` and `distractor_blocks` fields of the Lesson_Definition_File
3. THE Challenge_Round SHALL use the full existing Function_Library panel (`populate_functions_tab`) without modification, allowing the student to browse all categories and drag blocks into the editor
4. WHEN a block is dragged from the Block_Palette onto a Drop_Zone in the center column, THE Lesson_Panel SHALL use MIME data (`QMimeData.setText`) containing the function identifier, consistent with the existing `DraggableFunctionWidget` drag protocol
5. WHEN a block is dragged from the Function_Library in the Challenge_Round, THE Lesson_Panel SHALL use the existing ghost block system and smart indentation logic in the QScintilla editor to place the code snippet
6. THE Game_Engine SHALL validate dropped blocks by comparing the function identifier from the MIME data against the expected block for each Drop_Zone position

### Requirement 15: Initial Lesson Pack Content — Camera Basics Pack

**User Story:** As a student new to Python, I want a beginner Camera Basics lesson pack with fun stories and guided lessons, so that I can start learning through play.

#### Acceptance Criteria

1. THE `src/modules/courses/lessons/` directory SHALL contain a Lesson_Definition_File for a "Camera Basics" Lesson_Pack with at least 3 Lessons that progressively teach `Init_Camera`, `Get_Camera_Frame`, `Show_Image`, and `Close_Camera`
2. EACH Lesson in the Camera Basics pack SHALL include a Story_Narrative of 1-2 sentences featuring the KDI_Hatchling mascot in a fun scenario relevant to the coding concept
3. EACH Guided_Round in the Camera Basics pack SHALL include the correct code blocks plus 1-2 Distractor_Blocks from related but incorrect functions
4. EACH Explore_Round in the Camera Basics pack SHALL include a Puzzle_Target that requires modifying at least one parameter value, and a `scene_effect` that visualizes the parameter change in the Pixel_Visualization_Scene
5. EACH Challenge_Round in the Camera Basics pack SHALL include `hint_categories` pointing to the "Camera" and "Display & Dashboard" Function_Library categories
6. EACH Lesson in the Camera Basics pack SHALL include at least 1 hint and at most 3 hints for the Challenge_Round
7. THE Camera Basics pack SHALL use only Function_Blocks from the Camera, Display & Dashboard, and Variables categories (no AI Vision or Robotics blocks)
8. THE Camera Basics pack lesson structure SHALL follow the step-by-step format demonstrated in the existing curriculum examples (e.g., `curriculum/4_my_first_camera.py`)

### Requirement 16: Pixel Visualization Scene

**User Story:** As a student, I want to see a colorful pixel art game world on the right side of the screen where my mascot lives and reacts to what I do, so that coding feels like controlling a game world.

#### Acceptance Criteria

1. WHEN lesson mode is active, THE right column (Camera+Results area) SHALL be replaced with the Pixel_Visualization_Scene widget, rendered using QPainter on a QWidget
2. THE Pixel_Visualization_Scene SHALL display a themed pixel art background scene appropriate to the current Lesson_Pack (e.g., a camera studio for Camera Basics, a photo lab for Image Processing)
3. THE Pixel_Visualization_Scene SHALL contain the KDI_Hatchling pixel mascot character as the central interactive element
4. THE Pixel_Visualization_Scene SHALL support visual effect overlays for image processing lessons: grayscale filter over the scene, blur effect, brightness adjustment (brighter/darker), and rotation of scene elements
5. WHEN the student modifies parameters in the Explore_Round, THE Pixel_Visualization_Scene SHALL update its visual effects in real time to reflect the parameter changes (e.g., changing brightness value makes the scene visually brighter or darker)
6. WHEN lesson mode is deactivated, THE Pixel_Visualization_Scene SHALL be removed and the normal Camera+Results content SHALL be restored to the right column
7. THE Pixel_Visualization_Scene SHALL scale proportionally for both Standard (1280×800) and Small (1024×600) Resolution_Modes without clipping or distortion
