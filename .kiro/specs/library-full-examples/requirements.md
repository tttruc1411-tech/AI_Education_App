# Requirements Document

## Introduction

Expand the AI Coding Lab's Function Library with new blocks and a new Variables category, then create a comprehensive set of curriculum example programs that demonstrate how these blocks chain together. The design is example-driven: beginner examples focus on vision and camera concepts (before AI), intermediate examples introduce AI detection with overlays, and advanced examples combine AI with image processing and complex logic. All new Function_Blocks must integrate with the existing hint system's type scanner so that "Connect Logic" hints, "Type Mismatch" warnings, and "Unknown Variable" alerts work seamlessly.

## Glossary

- **Function_Library**: The drag-and-drop panel in the AI Coding Lab UI that organizes reusable code blocks into color-coded categories
- **Function_Block**: A single draggable entry in the Function_Library, defined by a description, parameters, return type, usage snippet, import statement, and source module reference
- **Definitions_Registry**: The `LIBRARY_FUNCTIONS` dictionary in `src/modules/library/definitions.py` that stores all Function_Block metadata
- **Curriculum_Example**: A complete Python program in the `curriculum/` folder with metadata headers (TITLE, TITLE_VI, LEVEL, ICON, COLOR, DESC, DESC_VI) that appears as a card in the Learning Hub
- **Learning_Hub**: The UI panel that displays Curriculum_Example cards for students to load and study
- **Dashboard_Protocol**: The stdout-based IPC mechanism using `Update_Dashboard()` to stream camera frames and variable values to the app UI
- **Image**: An OpenCV ndarray representing a picture frame (BGR color or grayscale)
- **AI_Model**: A loaded neural network object (ONNX session, YuNet detector, or TensorRT engine) used for inference
- **ORC_Hub**: The OhStem Motor Driver V2 hardware connected via I2C for robotics motor and servo control
- **Hint_System**: The `_scan_variable_types()` mechanism in `advanced_editor.py` that builds a type registry by scanning variable assignments against library function return types, list literals, and string/number literals, then shows "Connect Logic", "Type Mismatch", and "Warning: Unknown" hints in the editor
- **Type_Registry**: The dictionary produced by `_scan_variable_types()` mapping variable names to their inferred types (e.g., `"Image"`, `"Capture Object"`, `"Text (str)"`, `"Number"`, `"List"`)
- **Type_Chain**: A sequence of Function_Blocks where the `returns.type` of one block matches the `params[].type` of the next block, enabling the Hint_System to suggest "Connect Logic" hints

## Requirements

### Requirement 1: Hint System Compatibility for All New Blocks

**User Story:** As a student, I want the editor's hint system to recognize all new blocks and their variables, so that I get "Connect Logic" suggestions, "Type Mismatch" warnings, and "Unknown Variable" alerts when building programs.

#### Acceptance Criteria

1. THE Definitions_Registry SHALL define the `returns.type` of each new Function_Block using only types already recognized by the Hint_System or explicitly documented new types added to this specification (recognized types: `"Image"`, `"Image (ndarray)"`, `"Capture Object"`, `"AI Detector"`, `"AI Session"`, `"AI Model"`, `"Array"`, `"Number (int)"`, `"Number (float)"`, `"Number"`, `"Text (str)"`, `"List"`, `"None"`, `"Any"`, `"Control Flow"`, `"Check"`, `"Boolean"`)
2. THE Definitions_Registry SHALL define the `params[].type` of each new Function_Block parameter using the same recognized type vocabulary, so that `_scan_variable_types()` can match return types to parameter types via normalized prefix comparison (e.g., `"Image (ndarray)"` matches `"Image"`)
3. WHEN a student assigns the output of a new Function_Block to a variable, THE Hint_System SHALL register that variable in the Type_Registry with the correct `returns.type` from the Definitions_Registry
4. WHEN a student hovers over a parameter slot that accepts `"Image"` type, THE Hint_System SHALL show a "Connect Logic" hint listing all variables in the Type_Registry whose type normalizes to `"Image"` (including `"Image (ndarray)"`)
5. WHEN a student assigns a variable of type `"Text (str)"` to a parameter slot expecting `"Image"`, THE Hint_System SHALL display a "Type Mismatch" warning
6. THE `usage` snippet of each new Function_Block SHALL follow the pattern `variable_name = FunctionName(param1 = None, param2 = 'default')` so that the Hint_System's regex-based scanner can parse the assignment and register the variable type

### Requirement 2: Add Variables Category for Basic Data Type Declarations

**User Story:** As a student, I want dedicated variable blocks for declaring strings, integers, floats, and booleans, so that I can learn data types and create typed values that feed into other blocks via the hint system.

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain a new `"Variables"` category with a distinct color and icon (e.g., 📦 teal `#14b8a6`)
2. THE Definitions_Registry SHALL contain a `Create_Text` Function_Block in the Variables category that creates a text string variable, with a `value` parameter of type `"Text (str)"` and returns type `"Text (str)"`
3. THE Definitions_Registry SHALL contain a `Create_Number` Function_Block in the Variables category that creates a numeric variable, with a `value` parameter of type `"Number"` and returns type `"Number"`
4. THE Definitions_Registry SHALL contain a `Create_Decimal` Function_Block in the Variables category that creates a floating-point variable, with a `value` parameter of type `"Number (float)"` and returns type `"Number (float)"`
5. THE Definitions_Registry SHALL contain a `Create_Boolean` Function_Block in the Variables category that creates a boolean variable, with a `value` parameter of type `"Boolean"` and returns type `"Boolean"`
6. THE Definitions_Registry SHALL contain a `Create_List` Function_Block in the Variables category that creates a list variable, with a `value` parameter of type `"List"` and returns type `"List"` — this is needed because several blocks (e.g., `Draw_Detections_MultiClass`) accept `"List"` parameters
7. WHEN a student drags `Create_Text` into the editor and assigns it (e.g., `my_label = Create_Text(value = 'Hello')`), THE Hint_System SHALL register `my_label` as type `"Text (str)"` in the Type_Registry
8. WHEN a student later hovers over a `label` parameter of type `"Text (str)"` in `Draw_Detections`, THE Hint_System SHALL show a "Connect Logic" hint suggesting the `my_label` variable
9. THE Variables category blocks SHALL each have `source_func`, `source_module`, and `import_statement` pointing to a valid implementation file under `src/modules/library/functions/`

### Requirement 3: Expand Camera Category with Save and Load Blocks

**User Story:** As a student, I want blocks to save camera frames to files and load images from disk, so that I can work with pictures without a live camera and learn about file I/O.

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain a `Save_Frame` Function_Block in the Camera category with parameters `camera_frame` of type `"Image"` and `file_path` of type `"Text (str)"`, returning type `"None"`
2. THE Definitions_Registry SHALL contain a `Load_Image` Function_Block in the Camera category with parameter `file_path` of type `"Text (str)"`, returning type `"Image (ndarray)"`
3. WHEN a student drags `Save_Frame` into the editor, THE Function_Library SHALL inject a usage snippet with parameters for `camera_frame` and `file_path`
4. WHEN a student drags `Load_Image` into the editor, THE Function_Library SHALL inject a usage snippet that assigns the result to a variable (e.g., `loaded_image = Load_Image(file_path = None)`)
5. THE `Save_Frame` implementation SHALL write the Image to disk using OpenCV and print a confirmation message
6. THE `Load_Image` implementation SHALL read an image file from disk and return the Image ndarray
7. IF the file path provided to `Load_Image` does not exist, THEN THE `Load_Image` implementation SHALL print a descriptive error message and return None

### Requirement 4: Expand Image Processing Category with Vision Blocks

**User Story:** As a student, I want more image processing blocks for brightness, rotation, cropping, drawing text, and color conversion, so that I can experiment with visual transformations and build vision-focused beginner programs.

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain an `adjust_brightness` Function_Block in the Image Processing category with parameters `input_image` of type `"Image (ndarray)"` and `factor` of type `"Number (float)"`, returning type `"Image (ndarray)"`
2. THE Definitions_Registry SHALL contain a `rotate_image` Function_Block in the Image Processing category with parameters `input_image` of type `"Image (ndarray)"` and `angle` of type `"Number (int)"`, returning type `"Image (ndarray)"`
3. THE Definitions_Registry SHALL contain a `crop_image` Function_Block in the Image Processing category with parameters `input_image` of type `"Image (ndarray)"`, `x` of type `"Number (int)"`, `y` of type `"Number (int)"`, `width` of type `"Number (int)"`, and `height` of type `"Number (int)"`, returning type `"Image (ndarray)"`
4. THE Definitions_Registry SHALL contain a `draw_text` Function_Block in the Image Processing category with parameters `input_image` of type `"Image (ndarray)"`, `text` of type `"Text (str)"`, `x` of type `"Number (int)"`, `y` of type `"Number (int)"`, returning type `"Image (ndarray)"`
5. THE Definitions_Registry SHALL contain a `convert_to_hsv` Function_Block in the Image Processing category with parameter `input_image` of type `"Image (ndarray)"`, returning type `"Image (ndarray)"`
6. WHEN a student drags any new Image Processing block into the editor, THE Function_Library SHALL inject the correct usage snippet and import statement for that block
7. THE `adjust_brightness` implementation SHALL clamp output pixel values to the valid 0–255 range
8. THE `rotate_image` implementation SHALL rotate the image around its center without cropping the content

### Requirement 5: Expand Display & Dashboard Category with Visualization Blocks

**User Story:** As a student, I want more display blocks for FPS counters, rectangles, and circles, so that I can add visual overlays to the camera feed and understand computer graphics basics.

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain a `Show_FPS` Function_Block in the Display & Dashboard category with parameter `camera_frame` of type `"Image"`, returning type `"Image (ndarray)"`
2. THE Definitions_Registry SHALL contain a `Draw_Rectangle` Function_Block in the Display & Dashboard category with parameters `camera_frame` of type `"Image"`, `x` of type `"Number (int)"`, `y` of type `"Number (int)"`, `width` of type `"Number (int)"`, `height` of type `"Number (int)"`, and `color` of type `"Text (str)"`, returning type `"Image (ndarray)"`
3. THE Definitions_Registry SHALL contain a `Draw_Circle` Function_Block in the Display & Dashboard category with parameters `camera_frame` of type `"Image"`, `center_x` of type `"Number (int)"`, `center_y` of type `"Number (int)"`, `radius` of type `"Number (int)"`, and `color` of type `"Text (str)"`, returning type `"Image (ndarray)"`
4. THE Definitions_Registry SHALL contain a `Show_Image` Function_Block in the Display & Dashboard category with parameter `camera_frame` of type `"Image"`, returning type `"None"` — this block streams only the camera frame to the Live Feed panel via the `IMG:{base64}` stdout protocol, without updating any variable
5. THE Definitions_Registry SHALL contain an `Observe_Variable` Function_Block in the Display & Dashboard category with parameters `var_name` of type `"Text (str)"` and `var_value` of type `"Any"`, returning type `"None"` — this block updates only a variable in the Results panel via the `VAR:{name}:{value}` stdout protocol, without streaming any image
6. WHEN a student drags any new Display block into the editor, THE Function_Library SHALL inject the correct usage snippet and import statement
7. THE `Show_FPS` implementation SHALL calculate FPS based on elapsed time between consecutive calls and overlay the value as text on the top-left corner of the Image

### Requirement 6: Expand Logic Operations with Delay and Loop Blocks

**User Story:** As a student, I want logic blocks for timed delays, counting loops, and console output, so that I can build more complex programs step by step.

#### Acceptance Criteria

1. THE Definitions_Registry SHALL contain a `Wait_Seconds` Function_Block in the Logic Operations category with parameter `seconds` of type `"Number (float)"`, returning type `"None"`
2. THE Definitions_Registry SHALL contain a `Repeat_N_Times` Function_Block in the Logic Operations category with parameter `count` of type `"Number (int)"`, returning type `"Control Flow"` with `source_func` and `source_module` set to None
3. THE Definitions_Registry SHALL contain a `Print_Message` Function_Block in the Logic Operations category with parameter `message` of type `"Text (str)"`, returning type `"None"`
4. WHEN a student drags `Wait_Seconds` into the editor, THE Function_Library SHALL inject a usage snippet containing `time.sleep()` with the appropriate import statement
5. WHEN a student drags `Repeat_N_Times` into the editor, THE Function_Library SHALL inject a for-loop snippet with a configurable count parameter

### Requirement 7: Create Beginner Curriculum Examples (Vision-Focused, No AI)

**User Story:** As a student, I want many beginner-level examples that teach me camera basics, image processing, variables, and display overlays before I touch AI models, so that I build a solid foundation in computer vision concepts and discover many different things I can build.

#### Acceptance Criteria

1. THE `curriculum/` folder SHALL contain a "My First Camera" Beginner example that demonstrates only `Init_Camera`, `Get_Camera_Frame`, `Show_Image`, and `Close_Camera` blocks in a simple live feed loop with no AI model usage — teaching the concept of a camera pipeline
2. THE `curriculum/` folder SHALL contain an "Image Filters Lab" Beginner example that captures a live camera feed and applies a chain of image processing blocks (`convert_to_gray`, `apply_blur`, `detect_edges`, `flip_image`) to demonstrate visual transformations — teaching image processing pipelines
3. THE `curriculum/` folder SHALL contain a "Save & Load Pictures" Beginner example that demonstrates `Save_Frame` to save a camera snapshot to disk and `Load_Image` to reload it, then displays the loaded image via `Show_Image` — teaching file I/O concepts
4. THE `curriculum/` folder SHALL contain a "Mirror Selfie Mode" Beginner example that uses `Init_Camera`, `Get_Camera_Frame`, and `flip_image` with `direction = 'horizontal'` inside a `Loop_Forever` to create a real-time mirror effect — teaching the concept of real-time image transformation
5. THE `curriculum/` folder SHALL contain a "Brightness Controller" Beginner example that uses `Create_Decimal` to define a brightness factor variable, then applies `adjust_brightness` to a live camera feed inside a loop — teaching how Variables blocks control image processing parameters
6. THE `curriculum/` folder SHALL contain a "Photo Rotator" Beginner example that uses `Create_Number` to define an angle variable, then applies `rotate_image` to a live camera feed and displays the result — teaching rotation transformations and variable usage
7. THE `curriculum/` folder SHALL contain a "Text Overlay Studio" Beginner example that uses `Create_Text` to define a message variable, then uses `draw_text` to overlay custom text on a live camera feed at a specified position — teaching text rendering on images
8. THE `curriculum/` folder SHALL contain a "Shape Drawing Canvas" Beginner example that uses `Init_Camera`, `Get_Camera_Frame`, `Draw_Rectangle`, and `Draw_Circle` to draw colored shapes on a live camera feed — teaching computer graphics basics and coordinate systems
9. THE `curriculum/` folder SHALL contain a "Edge Detection Explorer" Beginner example that uses `Create_Number` variables for threshold1 and threshold2, applies `detect_edges` to a live camera feed with those thresholds, and displays the binary edge map — teaching edge detection concepts and parameter tuning
10. THE `curriculum/` folder SHALL contain a "Color Space Explorer" Beginner example that uses `convert_to_hsv` on a live camera feed and displays both the original BGR frame and the HSV-converted frame side by side via separate `Show_Image` calls — teaching color representation concepts
11. THE `curriculum/` folder SHALL contain a "Photo Crop & Frame" Beginner example that uses `crop_image` with `Create_Number` variables for x, y, width, height to crop a region from a live camera feed and display the cropped result — teaching image cropping and region-of-interest concepts
12. THE `curriculum/` folder SHALL contain a "Blur Intensity Lab" Beginner example that uses `Create_Number` to define a `kernel_size` variable, applies `apply_blur` with that variable to a live camera feed, and displays the result — teaching blur effects and how kernel size affects smoothness
13. THE `curriculum/` folder SHALL contain a "Grayscale Converter" Beginner example that uses `convert_to_gray` on a live camera feed and displays the grayscale result, with inline comments explaining how color channels are combined — teaching the concept of color-to-grayscale conversion
14. THE beginner examples SHALL NOT import or use any AI Vision Core blocks (no `Load_YuNet_Model`, `Load_ONNX_Model`, `Load_Engine_Model`, or any AI inference blocks)
15. WHEN a beginner example is loaded in the Learning_Hub, THE Curriculum_Example SHALL include bilingual metadata headers (TITLE, TITLE_VI, DESC, DESC_VI) with LEVEL set to "Beginner"
16. THE beginner examples SHALL use the separated display blocks (`Show_Image` for streaming camera frames and `Observe_Variable` for updating result values) instead of the combined `Update_Dashboard` block, to teach students the concept of separation of concerns
17. THE beginner examples SHALL include inline comments explaining each step for educational clarity
18. THE beginner examples SHALL demonstrate Type_Chain patterns where the output of one block feeds into the input of the next (e.g., `Get_Camera_Frame` returns `"Image"` which feeds into `convert_to_gray` accepting `"Image (ndarray)"`)

### Requirement 8: Create Intermediate Curriculum Examples (AI Detection + Overlays)

**User Story:** As a student, I want many intermediate examples that introduce AI models combined with display overlays, conditional logic, and image processing, so that I can learn how detection works, how to visualize results, and discover many different ways to combine blocks.

#### Acceptance Criteria

1. THE `curriculum/` folder SHALL contain a "Smart Face Counter" Intermediate example that combines `Load_YuNet_Model`, `Run_YuNet_Model`, `Draw_Detections`, `Show_FPS`, and `If_Condition` logic to count faces and display an alert message via `Print_Message` when the face count exceeds a threshold defined by `Create_Number` — teaching AI detection with conditional alerts
2. THE `curriculum/` folder SHALL contain an "Image Processing Pipeline" Intermediate example that chains multiple image processing blocks (`convert_to_gray`, `apply_blur`, `detect_edges`, `adjust_brightness`) on a live camera feed in sequence and displays the final processed result using `Show_Image` and `Observe_Variable` — teaching multi-step image transformation pipelines
3. THE `curriculum/` folder SHALL contain a "Color Explorer with HSV" Intermediate example that demonstrates `convert_to_hsv`, `adjust_brightness`, `draw_text` (to label the color space), and `Draw_Rectangle` (to highlight a region) on a live camera feed — teaching color space analysis and annotation
4. THE `curriculum/` folder SHALL contain a "Face-Triggered Filter" Intermediate example that uses `Load_YuNet_Model` and `Run_YuNet_Model` for face detection, then applies `convert_to_gray` and `apply_blur` to the frame only when a face is detected using `If_Else_Control` — teaching conditional image processing based on AI results
5. THE `curriculum/` folder SHALL contain an "Object Counter with Alert" Intermediate example that uses `Load_ONNX_Model`, `Run_ONNX_Model`, `Draw_Detections_MultiClass` with COCO classes, and `If_Condition` to print an alert via `Print_Message` when the total detected object count exceeds a threshold — teaching multi-class detection with threshold-based alerts
6. THE `curriculum/` folder SHALL contain a "FPS Performance Monitor" Intermediate example that uses `Show_FPS` on a live camera feed with `convert_to_gray` and `detect_edges` processing, displaying the FPS counter to teach students about computational cost of image processing operations — teaching performance awareness
7. THE `curriculum/` folder SHALL contain a "Face Detection with Annotations" Intermediate example that uses `Load_YuNet_Model`, `Run_YuNet_Model`, `Draw_Detections` for face boxes, then adds `draw_text` to overlay the face count as a label and `Draw_Rectangle` to draw a status bar area on the frame — teaching how to combine AI detection with custom annotations
8. THE `curriculum/` folder SHALL contain a "Timed Photo Capture" Intermediate example that uses `Load_YuNet_Model` for face detection inside a `Loop_Forever`, and when a face is detected uses `Wait_Seconds` for a countdown delay, then `Save_Frame` to save the photo — teaching timed automation with AI triggers
9. THE `curriculum/` folder SHALL contain a "Repeat Capture Series" Intermediate example that uses `Repeat_N_Times` to capture a fixed number of frames from the camera, applies `adjust_brightness` and `draw_text` (with a frame counter label) to each frame, and saves each using `Save_Frame` with sequential filenames — teaching counted loops and batch processing
10. THE `curriculum/` folder SHALL contain a "Custom Object Detector" Intermediate example that uses `Load_Engine_Model` and `Run_Engine_Model` with a student-trained `.engine` model, `Draw_Engine_Detections` for visualization, and `Show_Image` with `Observe_Variable` — teaching how to use custom-trained models for detection
11. WHEN an intermediate example is loaded in the Learning_Hub, THE Curriculum_Example SHALL include bilingual metadata headers with LEVEL set to "Intermediate"
12. THE intermediate examples SHALL use `Loop_Forever` and `If_Condition` or `If_Else_Control` logic blocks to demonstrate control flow
13. THE intermediate examples SHALL demonstrate blocks from at least two different Function_Library categories working together via Type_Chain connections

### Requirement 9: Create Advanced Curriculum Examples (AI + Image Processing + Complex Logic)

**User Story:** As a student, I want many advanced examples that combine AI vision with image processing, robotics, complex decision-making logic, and real-world scenarios, so that I can build complete intelligent systems and discover the full power of the platform.

#### Acceptance Criteria

1. THE `curriculum/` folder SHALL contain a "Security Camera" Advanced example that uses `Load_ONNX_Model`, `Run_ONNX_Model`, `Draw_Detections_MultiClass` (using its built-in `conf_threshold` parameter for confidence filtering), `Show_FPS`, `draw_text` to overlay a "ALERT" warning label, and conditional alerts (`If_Condition`, `If_Else_Control`) to detect specific objects (e.g., "person") and display warnings when a target object class is found — teaching surveillance system concepts
2. THE `curriculum/` folder SHALL contain a "Smart Photo Booth" Advanced example that combines face detection (`Load_YuNet_Model`, `Run_YuNet_Model`, `Draw_Detections`) with image processing effects (`adjust_brightness`, `draw_text`, `Draw_Rectangle` for a frame border), conditional logic (`If_Condition`, `If_Else_Control`), and `Save_Frame` to automatically capture and save a stylized snapshot when a face is detected — teaching automated photography systems
3. THE `curriculum/` folder SHALL contain an "AI Image Gallery" Advanced example that uses `Load_ONNX_Model` and `Run_ONNX_Model` for object detection on a live feed, `Draw_Detections_MultiClass` for annotation, `draw_text` to label the image with detection results, `Save_Frame` to save annotated frames, and `Repeat_N_Times` to capture a fixed gallery of annotated images — teaching automated image annotation and archival
4. THE `curriculum/` folder SHALL contain a "Face-Following Robot" Advanced example that uses `Load_YuNet_Model`, `Run_YuNet_Model`, and `Draw_Detections` for face detection, calculates the face center position, then uses `Set_Servo` to pan a servo toward the detected face using `If_Else_Control` for left/right decisions, with a comment warning that ORC_Hub hardware is required — teaching AI-powered robotics
5. THE `curriculum/` folder SHALL contain a "Multi-Model Speed Comparison" Advanced example that loads both `Load_YuNet_Model` and `Load_ONNX_Model` (YOLOv10), runs each on the same camera frame in sequence, uses `Show_FPS` and `Create_Number` variables to track inference counts, and displays both results side by side via `Show_Image` and `Observe_Variable` — teaching model performance comparison
6. THE `curriculum/` folder SHALL contain an "Object Tracker with Statistics" Advanced example that uses `Load_ONNX_Model`, `Run_ONNX_Model`, `Draw_Detections_MultiClass`, `Create_Number` variables for tracking cumulative counts, `If_Condition` for threshold checks, `draw_text` to overlay running statistics (total detections, current count), and `Show_FPS` — teaching data tracking and statistics visualization
7. THE `curriculum/` folder SHALL contain a "Smart Doorbell" Advanced example that uses `Load_YuNet_Model` for face detection, `If_Else_Control` to check if a face is detected, `Print_Message` to simulate a doorbell ring notification, `draw_text` to overlay "Welcome!" on the frame, `Draw_Rectangle` for a notification banner area, `Save_Frame` to save a snapshot of the visitor, and `Wait_Seconds` for a cooldown period between detections — teaching event-driven smart home concepts
8. THE `curriculum/` folder SHALL contain a "Robot Obstacle Avoider" Advanced example that uses `Load_ONNX_Model` and `Run_ONNX_Model` for object detection, `Draw_Detections_MultiClass` for visualization, `If_Else_Control` to check if objects are detected, `DC_Run` and `DC_Stop` to drive motors forward or stop when an obstacle is found, with a comment warning that ORC_Hub hardware is required — teaching AI-powered autonomous navigation
9. THE `curriculum/` folder SHALL contain a "Night Vision Effect" Advanced example that uses `convert_to_gray`, `adjust_brightness` with a high factor, `detect_edges`, `convert_to_hsv`, `draw_text` to overlay "NIGHT VISION" label, and `Show_FPS` on a live camera feed to simulate a night-vision camera effect — teaching creative image processing pipelines
10. THE `curriculum/` folder SHALL contain a "Face Attendance Logger" Advanced example that uses `Load_YuNet_Model` for face detection, `Create_Number` for a face counter variable, `If_Condition` to check for new faces, `Print_Message` to log attendance events to the console, `draw_text` to overlay the attendance count, and `Wait_Seconds` for a cooldown between logs — teaching automated logging and counting systems
11. THE `curriculum/` folder SHALL contain a "AI Art Filter" Advanced example that uses face detection (`Load_YuNet_Model`, `Run_YuNet_Model`) to detect faces, then applies a chain of artistic effects (`convert_to_gray`, `detect_edges`, `adjust_brightness`, `flip_image`) only to frames where faces are detected using `If_Else_Control`, and displays both the original and filtered versions — teaching conditional artistic image processing
12. THE `curriculum/` folder SHALL contain a "Motor Speed Dashboard" Advanced example that uses `Get_Speed` to read encoder RPM from two motors, `Create_Decimal` variables to store speed values, `draw_text` to overlay RPM readings on a camera feed, `Draw_Rectangle` for dashboard gauge backgrounds, `If_Condition` to check speed thresholds, and `Show_FPS`, with a comment warning that ORC_Hub hardware is required — teaching real-time sensor data visualization
13. WHEN an advanced example is loaded in the Learning_Hub, THE Curriculum_Example SHALL include bilingual metadata headers with LEVEL set to "Advanced"
14. THE advanced examples SHALL demonstrate integration across at least three Function_Library categories (e.g., Camera + AI Vision Core + Image Processing + Display + Logic)
15. THE advanced examples SHALL include inline comments explaining the AI decision-making logic for educational purposes
16. IF an advanced example uses robotics blocks, THEN THE example SHALL include a comment warning that ORC_Hub hardware is required

### Requirement 10: Curriculum Example File Format Consistency

**User Story:** As a developer, I want all curriculum examples to follow a consistent file format, so that the Learning Hub can parse and display them correctly.

#### Acceptance Criteria

1. THE Curriculum_Example files SHALL follow the naming convention `{number}_{snake_case_name}.py` with sequential numbering starting after the existing examples (4, 5, 6, ...)
2. THE Curriculum_Example files SHALL include all required metadata headers: TITLE, TITLE_VI, LEVEL, ICON, COLOR, DESC, DESC_VI, each prefixed with `# ` and followed by the separator line `# ============================================================`
3. THE Curriculum_Example files SHALL import function blocks using the same import paths defined in the Definitions_Registry
4. THE Curriculum_Example files SHALL use `Show_Image()` and `Observe_Variable()` as the primary mechanism for displaying camera frames and results in the app UI (new examples should prefer these separated blocks over the combined `Update_Dashboard()`)
5. IF a Curriculum_Example uses robotics blocks, THEN THE example SHALL include a comment warning that ORC_Hub hardware is required

### Requirement 11: Function Block Definition Completeness

**User Story:** As a developer, I want every new function block to have complete metadata, so that the Function Library panel, info tooltips, and source-code preview all work correctly.

#### Acceptance Criteria

1. THE Definitions_Registry SHALL define each new Function_Block with all required fields: `desc`, `params`, `returns`, `usage`, `import_statement`, `source_func`, and `source_module`
2. THE `params` field of each new Function_Block SHALL contain a list of parameter objects, each with `name`, `type`, and `desc` keys
3. THE `returns` field of each new Function_Block SHALL contain an object with `type` and `desc` keys
4. THE `import_statement` of each new Function_Block SHALL reference a valid Python module path under `src/modules/library/functions/`
5. THE `source_func` of each new Function_Block SHALL match the exact function name in the referenced source module
6. WHEN a Logic Operations block has no backing Python function (e.g., control flow snippets), THE Function_Block SHALL set `source_func` and `source_module` to None and `import_statement` to an empty string

### Requirement 12: Type Chain Design Across All New Blocks

**User Story:** As a developer, I want all new blocks to form logical type chains, so that the output of one block can feed into the input of the next and the hint system can guide students through the connections.

#### Acceptance Criteria

1. THE Camera category blocks SHALL produce outputs that chain into Image Processing inputs: `Get_Camera_Frame` returns `"Image"` and `Load_Image` returns `"Image (ndarray)"`, both of which SHALL be accepted by Image Processing blocks with `input_image` parameter of type `"Image (ndarray)"`
2. THE Image Processing blocks SHALL return `"Image (ndarray)"` so their outputs chain into other Image Processing blocks, Display blocks, and AI Vision Core blocks that accept `"Image"` or `"Image (ndarray)"` parameters
3. THE AI Vision Core inference blocks SHALL return `"Array"` type results that chain into Display blocks (`Draw_Detections`, `Draw_Detections_MultiClass`) that accept `"Array"` parameters
4. THE Display blocks `Draw_Detections` and `Draw_Detections_MultiClass` SHALL return `"Number (int)"` (detection count) which chains into `Update_Dashboard`'s `var_value` parameter of type `"Any"` and into `If_Condition`'s condition comparisons
5. THE Variables category blocks SHALL produce typed outputs (`"Text (str)"`, `"Number"`, `"Number (float)"`, `"Boolean"`) that chain into any parameter slot of the matching type across all categories
6. WHEN a student builds a complete program by chaining blocks (e.g., `Init_Camera` → `Get_Camera_Frame` → `convert_to_gray` → `detect_edges` → `Update_Dashboard`), THE Hint_System SHALL show "Connect Logic" hints at each parameter slot suggesting the appropriate upstream variable
