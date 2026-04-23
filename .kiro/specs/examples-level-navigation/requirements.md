# Requirements Document

## Introduction

The Learning Hub "Examples" tab currently displays all 38 curriculum examples in a flat scrolling list, causing visual overflow and card overlap. This feature replaces the flat list with a level-based navigation system: three prominent level badges (Beginner, Intermediate, Advanced) at the top of the Examples panel act as filter buttons. Selecting a level shows only the matching examples in a properly scrollable container below. The feature must support both standard (1280×800) and small (1024×600) resolution modes, and bilingual EN/VI labels.

## Glossary

- **Examples_Panel**: The "pageExamples" widget inside the Learning Hub's `hubStackedWidget`, which displays curriculum example cards.
- **Level_Navigation_Bar**: A horizontal bar of three clickable level badge buttons placed at the top of the Examples_Panel, above the scrollable example area.
- **Level_Badge**: A single clickable widget within the Level_Navigation_Bar representing one difficulty level (Beginner, Intermediate, or Advanced). In its inactive state, the Level_Badge renders as a small half-circle (colored indicator light) at the top of the bar. In its active state, the half-circle animates downward into a flag/ribbon shape (banner unfurling effect) using QPropertyAnimation. The badge displays the level name text and a representative icon or emoji.
- **Badge_Animation**: A smooth QPropertyAnimation-driven height transition that grows a Level_Badge from its compact half-circle (inactive) form downward into a full flag/ribbon (active) form, and shrinks it back when deselected.
- **Filtered_Example_Area**: A `QScrollArea` widget below the Level_Navigation_Bar that displays only the CurriculumCard widgets matching the currently selected level.
- **CurriculumCard**: An existing `QFrame`-based widget (defined in `main.py`) that renders a single curriculum example with icon, title, description, level badge, and Load button.
- **Active_Level**: The currently selected level whose examples are visible in the Filtered_Example_Area.
- **Resolution_Mode**: The application display mode, either Standard (1280×800) or Small (1024×600), controlled by `refresh_ui_resolution()` in `main.py`.
- **Curriculum_Metadata**: The header comments in each curriculum `.py` file containing TITLE, TITLE_VI, LEVEL, ICON, COLOR, DESC, and DESC_VI fields.

## Requirements

### Requirement 1: Level Navigation Bar Display

**User Story:** As a student, I want to see three vibrant, animated level badges at the top of the Examples tab, so that I can quickly identify and select a difficulty level in an engaging way.

#### Acceptance Criteria

1. WHEN the Examples tab is displayed, THE Level_Navigation_Bar SHALL render exactly three Level_Badge widgets in a horizontal row: Beginner, Intermediate, and Advanced (left to right).
2. THE Level_Badge for Beginner SHALL use hex color #3b82f6 (blue) as its base color.
3. THE Level_Badge for Intermediate SHALL use hex color #22c55e (green) as its base color.
4. THE Level_Badge for Advanced SHALL use hex color #f97316 (orange) as its base color.
5. WHEN a Level_Badge is in the inactive state, THE Level_Badge SHALL render as a small half-circle shape at the top of the Level_Navigation_Bar, displaying only the level color as a subtle colored indicator light.
6. WHEN a Level_Badge is in the active state, THE Level_Badge SHALL render as a flag/ribbon shape that extends downward from the half-circle, displaying the level name text, a representative icon or emoji, and a vibrant version of the level color.
7. THE Level_Badge SHALL remain proportionally sized as a child component within the Examples_Panel, not exceeding the height or visual dominance of the Learning Hub title.
8. WHILE Resolution_Mode is Standard (1280×800), THE Level_Badge SHALL render with font size, padding, and icon size appropriate for the standard layout.
7. WHILE Resolution_Mode is Small (1024×600), THE Level_Badge SHALL render at 80% of the standard dimensions, with proportionally reduced font size, padding, and icon size.

### Requirement 2: Level Filtering Behavior

**User Story:** As a student, I want to click a level badge to see only examples of that difficulty, so that I am not overwhelmed by 38 examples at once.

#### Acceptance Criteria

1. WHEN the application launches, THE Examples_Panel SHALL display the Beginner level as the Active_Level by default.
2. WHEN a user clicks a Level_Badge, THE Examples_Panel SHALL set that level as the Active_Level.
3. WHEN the Active_Level changes, THE Filtered_Example_Area SHALL display only CurriculumCard widgets whose Curriculum_Metadata LEVEL field matches the Active_Level.
4. WHEN the Active_Level changes, THE Filtered_Example_Area SHALL hide all CurriculumCard widgets that do not match the Active_Level.
5. THE Examples_Panel SHALL display the count of examples for each level on or near the corresponding Level_Badge.

### Requirement 3: Active Level Visual Indicator

**User Story:** As a student, I want to clearly see which level is currently selected through a dynamic flag animation, so that I know which difficulty I am browsing.

#### Acceptance Criteria

1. WHEN a Level_Badge becomes the Active_Level, THE Level_Badge SHALL animate from the compact half-circle shape downward into the full flag/ribbon shape using a smooth Badge_Animation (QPropertyAnimation on height/size), creating a banner-unfurling visual effect.
2. WHEN a Level_Badge becomes the Active_Level, THE Level_Badge SHALL transition its color from a muted or semi-transparent shade to a vibrant, fully saturated version of the level color.
3. WHEN a Level_Badge is not the Active_Level, THE Level_Badge SHALL display as a compact half-circle with a muted or semi-transparent version of the level color, acting as a subtle colored indicator light.
4. WHEN the user clicks a different Level_Badge, THE previously active Level_Badge SHALL animate from the flag/ribbon shape back to the compact half-circle shape (shrinking upward), and the newly clicked Level_Badge SHALL animate from the half-circle to the flag/ribbon shape (growing downward).
5. THE Badge_Animation transition duration SHALL be smooth and perceptible (150–300 milliseconds) to create an engaging, dynamic feel attractive to young students.

### Requirement 4: Scrollable Filtered Example Area

**User Story:** As a student, I want the filtered examples to be in a scrollable container, so that they do not overflow or overlap with other UI elements.

#### Acceptance Criteria

1. THE Filtered_Example_Area SHALL use a `QScrollArea` widget to contain the filtered CurriculumCard widgets.
2. WHEN the total height of the filtered CurriculumCard widgets exceeds the visible height of the Filtered_Example_Area, THE Filtered_Example_Area SHALL display a vertical scrollbar.
3. THE Filtered_Example_Area SHALL prevent CurriculumCard widgets from overlapping each other.
4. THE Filtered_Example_Area SHALL set `widgetResizable` to true so that the scroll contents expand to fill the available width.

### Requirement 5: Dual Resolution Support

**User Story:** As a student using a small 10-inch screen, I want the level navigation and example cards to scale down properly, so that the UI remains usable at 1024×600 resolution.

#### Acceptance Criteria

1. WHEN `refresh_ui_resolution()` is called, THE Level_Navigation_Bar SHALL update its dimensions and font sizes to match the current Resolution_Mode.
2. WHILE Resolution_Mode is Small, THE Level_Badge buttons SHALL render with reduced height, width, font size, icon size, and padding (80% of standard values).
3. WHILE Resolution_Mode is Small, THE CurriculumCard widgets in the Filtered_Example_Area SHALL render with the `is_small=True` parameter.
4. WHEN the resolution toggles between Standard and Small, THE Examples_Panel SHALL re-populate the Level_Navigation_Bar and Filtered_Example_Area with correctly sized components.

### Requirement 6: Bilingual Label Support

**User Story:** As a Vietnamese student, I want the level badges and example cards to display in my language, so that I can understand the interface.

#### Acceptance Criteria

1. WHEN the current language is English, THE Level_Badge buttons SHALL display "Beginner", "Intermediate", and "Advanced".
2. WHEN the current language is Vietnamese, THE Level_Badge buttons SHALL display the Vietnamese translations for each level name.
3. WHEN the language is switched, THE Level_Navigation_Bar SHALL update the Level_Badge text to the new language.
4. WHEN the language is switched, THE CurriculumCard widgets SHALL display the localized title and description from Curriculum_Metadata (TITLE_VI, DESC_VI for Vietnamese; TITLE, DESC for English).

### Requirement 7: Preserve Existing Load Behavior

**User Story:** As a student, I want the Load button on each example card to continue loading the code into the editor, so that existing functionality is not broken.

#### Acceptance Criteria

1. WHEN a user clicks the "Load" button on a CurriculumCard, THE Examples_Panel SHALL load the corresponding curriculum file content into the code editor (existing `load_curriculum_example` behavior).
2. THE CurriculumCard "Load" button click handler SHALL remain connected to the existing `load_curriculum_example` method without modification to its signature or behavior.
