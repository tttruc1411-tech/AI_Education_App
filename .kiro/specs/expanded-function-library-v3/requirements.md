# Requirements Document

## Introduction

This specification covers the V3 expansion of the AI Coding Lab's Function Library and Curriculum system. The scope includes: (1) adding new educational function blocks to existing and potentially new categories to teach additional AI/computer vision concepts, (2) creating new curriculum examples that demonstrate the new blocks with progressive difficulty, and (3) renaming all curriculum example files to remove the numeric prefix (e.g., `1_face_detection.py` → `face_detection.py`) while introducing an explicit ordering mechanism and updating all codebase references.

## Glossary

- **Function_Library**: The drag-and-drop panel in the Learning Hub that organizes educational code blocks into color-coded categories (Camera, Image Processing, AI Vision, Display, Logic, Robotics, Variables)
- **Function_Block**: A single draggable entry in the Function_Library that injects a code snippet, import statement, and metadata into the QScintilla editor
- **Definitions_Registry**: The `LIBRARY_FUNCTIONS` dictionary in `src/modules/library/definitions.py` that stores all Function_Block metadata (desc, desc_vi, params, returns, usage, import_statement, source_func, source_module)
- **Curriculum_Example**: A Python script in the `curriculum/` folder with metadata headers (TITLE, TITLE_VI, LEVEL, ICON, COLOR, DESC, DESC_VI) that demonstrates Function_Block usage
- **Level_Navigation_Bar**: The frosted pill bar UI that filters Curriculum_Examples by difficulty level (Beginner, Intermediate, Advanced)
- **Hint_System**: The `_scan_variable_types()` and `_show_assistance()` logic in `advanced_editor.py` that detects variable types from Function_Block return values and shows contextual "Connect Logic" / "Type Mismatch" hints
- **Shortcut_Module**: A root-level Python file (e.g., `camera.py`, `image.py`) that re-exports functions from the actual source files in `src/modules/library/functions/`, enabling clean `import camera` style imports in student code
- **Source_File**: The actual implementation file in `src/modules/library/functions/` that contains the function logic (e.g., `camera_blocks.py`, `image_processing.py`)
- **Metadata_Header**: The comment block at the top of each Curriculum_Example containing TITLE, TITLE_VI, LEVEL, ICON, COLOR, DESC, DESC_VI fields
- **AI_Assistant_Bot**: The floating LLM-powered chat assistant that uses Definitions_Registry entries for context injection when answering student questions
- **Type_Chain**: The pattern where Function_Blocks return typed values (e.g., `Image (ndarray)`, `Text (str)`) that the Hint_System uses to suggest compatible connections between blocks
- **ORDER_Field**: A new integer metadata field in the Metadata_Header that controls the display sort order of Curriculum_Examples within each difficulty level
- **Ghost_Block_System**: The visual code scope guidance system that uses color-coded background tinting during drag-and-drop to show Main, Loop, and Condition blocks

## Requirements

### Requirement 1: New Image Processing Function Blocks

**User Story:** As a student, I want additional image processing blocks in the Function_Library, so that I can learn more computer vision techniques beyond the current set.

The following 5 new blocks SHALL be added to the "Image Processing" category (bringing the total from 10 to 15):

| Block Name | Signature | Returns | Concept Taught |
|---|---|---|---|
| `threshold_image` | `threshold_image(input_image, threshold=127, max_value=255)` | `Image (ndarray)` | Binary thresholding — converting images to black/white at a cutoff value |
| `blend_images` | `blend_images(image1, image2, alpha=0.5)` | `Image (ndarray)` | Image blending/overlay with transparency weight |
| `split_channels` | `split_channels(input_image)` | `List` | Splitting a BGR image into 3 separate color channel images |
| `equalize_histogram` | `equalize_histogram(input_image)` | `Image (ndarray)` | Enhancing contrast via histogram equalization |
| `detect_contours` | `detect_contours(input_image)` | `Image (ndarray)` | Finding and drawing object contours/outlines |

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain Function_Block entries for `threshold_image`, `blend_images`, `split_channels`, `equalize_histogram`, and `detect_contours` in the "Image Processing" category
2. WHEN a new Image Processing Function_Block is dragged into the editor, THE Function_Library SHALL inject the correct `import image` statement and module-prefixed usage snippet (e.g., `image.threshold_image(...)`)
3. THE Source_File `image_processing.py` SHALL contain the implementation for each new Image Processing Function_Block
4. THE Shortcut_Module `image.py` SHALL re-export all 5 new Image Processing functions from the Source_File
5. WHEN a new Image Processing Function_Block returns a value, THE return type SHALL use the recognized Type_Chain vocabulary (`Image (ndarray)` or `List`) so the Hint_System registers variables correctly

### Requirement 2: New Display and Dashboard Function Blocks

**User Story:** As a student, I want additional display blocks, so that I can create richer visual overlays and annotations on camera feeds.

The following 3 new blocks SHALL be added to the "Display & Dashboard" category (bringing the total from 7 to 10):

| Block Name | Signature | Returns | Concept Taught |
|---|---|---|---|
| `Draw_Line` | `Draw_Line(camera_frame, x1, y1, x2, y2, color='green')` | `Image (ndarray)` | Drawing lines for visual guides, crosshairs, and annotations |
| `Draw_Text_Box` | `Draw_Text_Box(camera_frame, text, x, y, bg_color='blue', text_color='white')` | `Image (ndarray)` | Drawing text with a colored background box for labels and status bars |
| `Stack_Images` | `Stack_Images(image1, image2, direction='horizontal')` | `Image (ndarray)` | Stacking two images side-by-side or top-bottom for comparison views |

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain Function_Block entries for `Draw_Line`, `Draw_Text_Box`, and `Stack_Images` in the "Display & Dashboard" category
2. WHEN a new Display Function_Block is dragged into the editor, THE Function_Library SHALL inject the correct `import display` statement and module-prefixed usage snippet
3. THE Source_File `display_blocks.py` SHALL contain the implementation for each new Display Function_Block
4. THE Shortcut_Module `display.py` SHALL re-export all 3 new Display functions from the Source_File
5. WHEN a new Display Function_Block returns a value, THE return type SHALL use `Image (ndarray)` for frame-modifying operations so the Type_Chain remains compatible

### Requirement 3: New Logic and Control Flow Function Blocks

**User Story:** As a student, I want additional logic blocks, so that I can learn more programming control flow patterns.

The following 2 new blocks SHALL be added to the "Logic Operations" category (bringing the total from 6 to 8):

| Block Name | Signature | Returns | Concept Taught |
|---|---|---|---|
| `Get_Timestamp` | `Get_Timestamp()` | `Text (str)` | Getting the current time as a formatted string for logging and timestamping |
| `Compare_Values` | `Compare_Values(value1, value2)` | `Boolean` | Comparing two values and returning True/False (educational wrapper for comparisons) |

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain Function_Block entries for `Get_Timestamp` and `Compare_Values` in the "Logic Operations" category
2. THE Source_File `logic_blocks.py` SHALL contain the implementation for `Get_Timestamp` and `Compare_Values`
3. THE Shortcut_Module `logic.py` SHALL re-export `Get_Timestamp` and `Compare_Values` from the Source_File
4. WHEN `Get_Timestamp` is called, THE function SHALL return the current date and time as a human-readable formatted string
5. WHEN `Compare_Values` is called with two values, THE function SHALL return a Boolean indicating whether the values are equal

### Requirement 4: New Camera Function Blocks

**User Story:** As a student, I want additional camera blocks, so that I can learn more camera control techniques.

The following 2 new blocks SHALL be added to the "Camera" category (bringing the total from 5 to 7):

| Block Name | Signature | Returns | Concept Taught |
|---|---|---|---|
| `Set_Camera_Resolution` | `Set_Camera_Resolution(capture_camera, width=640, height=480)` | `None` | Changing camera capture resolution for different use cases |
| `Capture_Snapshot` | `Capture_Snapshot(capture_camera, countdown=0)` | `Image (ndarray)` | Capturing a single frame with an optional countdown delay |

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain Function_Block entries for `Set_Camera_Resolution` and `Capture_Snapshot` in the "Camera" category
2. WHEN a new Camera Function_Block is dragged into the editor, THE Function_Library SHALL inject the correct `import camera` statement and module-prefixed usage snippet
3. THE Source_File `camera_blocks.py` SHALL contain the implementation for `Set_Camera_Resolution` and `Capture_Snapshot`
4. THE Shortcut_Module `camera.py` SHALL re-export `Set_Camera_Resolution` and `Capture_Snapshot` from the Source_File
5. WHEN `Capture_Snapshot` is called with a countdown value greater than 0, THE function SHALL print a countdown message each second before capturing

### Requirement 5: New AI Vision Function Blocks

**User Story:** As a student, I want additional AI vision blocks, so that I can explore more AI model types and inference techniques.

The following 2 new blocks SHALL be added to the "AI Vision Core" category (bringing the total from 6 to 8):

| Block Name | Signature | Returns | Concept Taught |
|---|---|---|---|
| `Get_Detection_Count` | `Get_Detection_Count(results)` | `Number (int)` | Extracting the number of detections from raw model output |
| `Crop_Detection` | `Crop_Detection(camera_frame, results, index=0)` | `Image (ndarray)` | Cropping a detected object region from the frame by detection index |

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain Function_Block entries for `Get_Detection_Count` and `Crop_Detection` in the "AI Vision Core" category
2. WHEN a new AI Vision Function_Block is dragged into the editor, THE Function_Library SHALL inject the correct `import ai_vision` statement and module-prefixed usage snippet
3. THE Source_File `ai_vision_blocks.py` SHALL contain the implementation for `Get_Detection_Count` and `Crop_Detection`
4. THE Shortcut_Module `ai_vision.py` SHALL re-export `Get_Detection_Count` and `Crop_Detection` from the Source_File
5. WHEN `Crop_Detection` is called with an index that exceeds the number of detections, THE function SHALL return None and print a friendly error message

### Requirement 6: New Robotics Function Blocks

**User Story:** As a student, I want additional robotics blocks, so that I can build more complex robot behaviors.

The following 1 new block SHALL be added to the "Robotics" category (bringing the total from 4 to 5):

| Block Name | Signature | Returns | Concept Taught |
|---|---|---|---|
| `Sweep_Servo` | `Sweep_Servo(pin='S1', start_angle=0, end_angle=180, step=10, delay=0.05)` | `None` | Smoothly sweeping a servo motor across an angle range with configurable step and delay |

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain a Function_Block entry for `Sweep_Servo` in the "Robotics" category
2. WHEN `Sweep_Servo` is dragged into the editor, THE Function_Library SHALL inject the correct `import robotics` statement and module-prefixed usage snippet
3. THE Source_File `robotics.py` in `src/modules/library/functions/` SHALL contain the implementation for `Sweep_Servo`
4. THE Shortcut_Module `robotics.py` at the project root SHALL re-export `Sweep_Servo` from the Source_File
5. WHEN `Sweep_Servo` is called, THE function SHALL iterate from `start_angle` to `end_angle` in increments of `step`, calling `Set_Servo` at each position with a `delay` pause between steps

### Requirement 7: Bilingual Metadata for All New Function Blocks

**User Story:** As a Vietnamese student, I want all new function blocks to have Vietnamese descriptions, so that I can learn in my native language.

#### Acceptance Criteria

1. THE Definitions_Registry entry for each new Function_Block SHALL include a `desc_vi` field containing the Vietnamese translation of the description
2. THE Definitions_Registry entry for each new Function_Block SHALL include `desc_vi` fields in every item of the `params` list
3. THE Definitions_Registry entry for each new Function_Block SHALL include a `desc_vi` field in the `returns` dictionary
4. WHEN the application language is set to Vietnamese, THE Function_Library panel SHALL display the `desc_vi` text for all new Function_Blocks

### Requirement 8: Hint System Compatibility for New Blocks

**User Story:** As a student, I want the editor hints to work correctly with new function blocks, so that I get accurate "Connect Logic" and "Type Mismatch" guidance.

#### Acceptance Criteria

1. WHEN a new Function_Block returns a typed value, THE return type string SHALL match one of the recognized Hint_System vocabulary types: `Image`, `Image (ndarray)`, `Capture Object`, `AI Detector`, `AI Session`, `AI Model`, `Array`, `Text (str)`, `Number`, `Number (int)`, `Number (float)`, `Boolean`, `List`, `Control Flow`, `None`
2. WHEN a student assigns the result of a new Function_Block to a variable, THE Hint_System `_scan_variable_types()` SHALL correctly register the variable and its type in the registry
3. WHEN a student drags a new Function_Block that expects a specific parameter type, THE Hint_System SHALL show "Connect Logic" hints suggesting compatible variables from the registry

### Requirement 9: AI Assistant Bot Context for New Blocks

**User Story:** As a student, I want the AI Assistant Bot to understand new function blocks, so that it can help me use them correctly.

#### Acceptance Criteria

1. WHEN a student asks the AI_Assistant_Bot a question mentioning a new Function_Block name, THE `_extract_func_context()` method in `prompt_builder.py` SHALL find the Function_Block in the Definitions_Registry and inject its description, parameters, return type, and usage into the LLM prompt
2. WHEN a student uses the "Explain" action on code containing new Function_Blocks, THE AI_Assistant_Bot SHALL include the relevant Function_Block definitions in the explain prompt context

### Requirement 10: New Beginner Curriculum Examples

**User Story:** As a beginner student, I want new curriculum examples that teach the new function blocks with simple, standalone projects, so that I can learn one concept at a time.

The following 4 new Beginner examples SHALL be created (bringing the Beginner total from 13 to 17):

| Filename | Title | Blocks Taught |
|---|---|---|
| `threshold_lab.py` | Threshold Lab | `threshold_image` — binary thresholding with adjustable cutoff |
| `image_blender.py` | Image Blender | `blend_images` + `Load_Image` — blending camera feed with a loaded image |
| `channel_splitter.py` | Channel Splitter | `split_channels` + `Stack_Images` — viewing individual R/G/B channels side-by-side |
| `contour_finder.py` | Contour Finder | `detect_contours` + `threshold_image` — finding and drawing object outlines |

#### Acceptance Criteria

1. THE `curriculum/` folder SHALL contain `threshold_lab.py`, `image_blender.py`, `channel_splitter.py`, and `contour_finder.py`
2. EACH new Beginner Curriculum_Example SHALL use only Camera, Image Processing, Display, Logic, and Variables category blocks (no AI Vision or Robotics blocks)
3. EACH new Beginner Curriculum_Example SHALL include a complete Metadata_Header with TITLE, TITLE_VI, LEVEL set to `Beginner`, ICON, COLOR set to `#22c55e`, DESC, DESC_VI, and ORDER
4. EACH new Beginner Curriculum_Example SHALL use the Clean Module Import System (`import camera`, `import image`, etc.) with module-prefixed function calls
5. EACH new Beginner Curriculum_Example SHALL include inline comments explaining each step for educational clarity

### Requirement 11: New Intermediate Curriculum Examples

**User Story:** As an intermediate student, I want new curriculum examples that combine new function blocks with AI detection, so that I can build smarter projects.

The following 4 new Intermediate examples SHALL be created (bringing the Intermediate total from 12 to 16):

| Filename | Title | Blocks Taught |
|---|---|---|
| `face_crop_gallery.py` | Face Crop Gallery | `Crop_Detection` + `Save_Frame` — detecting faces and cropping each one |
| `smart_timestamp_logger.py` | Smart Timestamp Logger | `Get_Timestamp` + `Get_Detection_Count` — logging detections with timestamps |
| `side_by_side_filters.py` | Side-by-Side Filters | `Stack_Images` + multiple image filters — comparing original vs filtered in split view |
| `contrast_enhancer.py` | Contrast Enhancer | `equalize_histogram` + AI detection — auto-enhancing low-contrast images |

#### Acceptance Criteria

1. THE `curriculum/` folder SHALL contain `face_crop_gallery.py`, `smart_timestamp_logger.py`, `side_by_side_filters.py`, and `contrast_enhancer.py`
2. EACH new Intermediate Curriculum_Example SHALL use blocks from at least 3 different categories
3. EACH new Intermediate Curriculum_Example SHALL include a complete Metadata_Header with TITLE, TITLE_VI, LEVEL set to `Intermediate`, ICON, COLOR set to `#eab308`, DESC, DESC_VI, and ORDER
4. EACH new Intermediate Curriculum_Example SHALL use `Show_Image` and `Observe_Variable` (not `Update_Dashboard`) for display output
5. EACH new Intermediate Curriculum_Example SHALL use the Clean Module Import System with module-prefixed function calls

### Requirement 12: New Advanced Curriculum Examples

**User Story:** As an advanced student, I want new curriculum examples that integrate multiple categories including robotics, so that I can build complex real-world projects.

The following 4 new Advanced examples SHALL be created (bringing the Advanced total from 13 to 17):

| Filename | Title | Blocks Taught |
|---|---|---|
| `smart_traffic_monitor.py` | Smart Traffic Monitor | `Get_Detection_Count` + `Get_Timestamp` + ONNX — counting and logging vehicles |
| `panoramic_servo_scanner.py` | Panoramic Servo Scanner | `Sweep_Servo` + AI detection — sweeping servo while detecting objects |
| `object_isolation_studio.py` | Object Isolation Studio | `Crop_Detection` + `Stack_Images` + filters — detecting, cropping, filtering, and displaying in grid |
| `hi_res_capture_station.py` | Hi-Res Capture Station | `Set_Camera_Resolution` + `Capture_Snapshot` — switching resolutions for detection vs capture |

#### Acceptance Criteria

1. THE `curriculum/` folder SHALL contain `smart_traffic_monitor.py`, `panoramic_servo_scanner.py`, `object_isolation_studio.py`, and `hi_res_capture_station.py`
2. EACH new Advanced Curriculum_Example SHALL include a complete Metadata_Header with TITLE, TITLE_VI, LEVEL set to `Advanced`, ICON, COLOR set to `#f97316`, DESC, DESC_VI, and ORDER
3. WHEN an Advanced Curriculum_Example uses Robotics blocks, THE example SHALL include a `# ⚠️ WARNING: This example requires ORC Hub hardware` comment
4. EACH new Advanced Curriculum_Example SHALL use the Clean Module Import System with module-prefixed function calls
5. EACH new Advanced Curriculum_Example SHALL demonstrate a cohesive real-world project scenario integrating blocks from 4 or more categories

### Requirement 13: Remove Numeric Prefix from Curriculum Filenames

**User Story:** As a developer, I want curriculum filenames to use descriptive names without numeric prefixes, so that the file naming is cleaner and new examples can be added without renumbering.

#### Acceptance Criteria

1. WHEN the rename operation is performed, THE system SHALL rename each existing Curriculum_Example file from `{number}_{name}.py` to `{name}.py` (e.g., `1_face_detection.py` → `face_detection.py`, `4_my_first_camera.py` → `my_first_camera.py`)
2. WHEN the rename operation is performed, THE system SHALL rename all 38 existing Curriculum_Example files in the `curriculum/` folder
3. WHEN new Curriculum_Examples are created (Requirements 10–12), THE new files SHALL use the descriptive name format without a numeric prefix

### Requirement 14: Explicit Sort Order via ORDER Metadata Field

**User Story:** As a developer, I want an explicit ordering mechanism for curriculum examples, so that examples display in the correct pedagogical sequence after removing numeric prefixes.

#### Acceptance Criteria

1. EACH Curriculum_Example Metadata_Header SHALL include an `ORDER` field containing an integer that defines the display sort position within its difficulty level
2. WHEN `populate_curriculum_hub()` in `main.py` scans the `curriculum/` folder, THE method SHALL sort Curriculum_Examples by the `ORDER` field value (ascending) within each level group, falling back to alphabetical filename sort when ORDER values are equal
3. WHEN the `_parse_lesson_metadata()` method parses a Curriculum_Example file, THE method SHALL extract the `ORDER` field as an integer from the Metadata_Header
4. THE existing 38 Curriculum_Examples SHALL have ORDER values assigned that preserve their current display sequence

### Requirement 15: Update All Codebase References to Renamed Files

**User Story:** As a developer, I want all references to old curriculum filenames updated throughout the codebase, so that nothing breaks after the rename.

#### Acceptance Criteria

1. WHEN the rename operation is performed, THE system SHALL update all references to old numbered filenames in `agent.md` to use the new descriptive filenames
2. WHEN the rename operation is performed, THE system SHALL update all references to old numbered filenames in any `.kiro/specs/` documents to use the new descriptive filenames
3. IF any Python source file (outside `curriculum/`) contains hardcoded references to numbered curriculum filenames, THEN THE system SHALL update those references to the new descriptive filenames
4. WHEN `populate_curriculum_hub()` scans the `curriculum/` directory, THE method SHALL continue to work correctly with the new descriptive filenames since it uses `os.listdir()` with `.py` extension filtering

### Requirement 16: New Function Block Source File Structure

**User Story:** As a developer, I want new function implementations to follow the existing modular architecture, so that the codebase remains organized and maintainable.

#### Acceptance Criteria

1. WHEN a new Function_Block is added to an existing category, THE implementation SHALL be added to the corresponding existing Source_File (e.g., new Image Processing blocks go in `image_processing.py`)
2. EACH new function implementation SHALL include a Python docstring describing its purpose, parameters, and return value
3. EACH new function implementation SHALL include error handling that prints a friendly `[Module_Name]` prefixed error message and returns a safe default value on failure
4. IF a new function uses OpenCV operations, THEN THE function SHALL handle both color (BGR) and grayscale input images where applicable
