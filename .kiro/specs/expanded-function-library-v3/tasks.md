# Implementation Plan: Expanded Function Library V3

## Overview

Add 15 new function blocks across 6 categories (Image Processing, Display, Logic, Camera, AI Vision, Robotics) with full bilingual metadata (EN/VI), implement source functions, update shortcut modules, create 12 new curriculum examples, and migrate all 38 existing curriculum files to remove numeric prefixes with an explicit ORDER metadata field. All new blocks integrate with the existing hint system and AI Assistant Bot via the Definitions Registry.

## Tasks

- [x] 1. Implement new Image Processing source functions
  - [x] 1.1 Add 5 new functions to `src/modules/library/functions/image_processing.py`
    - Implement `threshold_image(input_image, threshold=127, max_value=255)` — cv2.threshold wrapper, auto-converts to grayscale, returns thresholded image
    - Implement `blend_images(image1, image2, alpha=0.5)` — cv2.addWeighted wrapper, auto-resizes image2 to match image1
    - Implement `split_channels(input_image)` — cv2.split wrapper, returns list of 3 single-channel images
    - Implement `equalize_histogram(input_image)` — cv2.equalizeHist wrapper, handles color via per-channel equalization
    - Implement `detect_contours(input_image)` — cv2.findContours + cv2.drawContours, returns image with contours drawn
    - Each function must include docstring, try/except with `[Image]` prefixed error, and safe default return
    - Each function must handle both color (BGR) and grayscale input images
    - _Requirements: 1.1, 1.3, 1.5, 16.1, 16.2, 16.3, 16.4_

  - [x] 1.2 Update shortcut module `image.py` to re-export the 5 new functions
    - Add `threshold_image`, `blend_images`, `split_channels`, `equalize_histogram`, `detect_contours` to the explicit import list
    - _Requirements: 1.4_

  - [ ]* 1.3 Write property test for color/grayscale handling (Property 6)
    - **Property 6: Image processing functions handle color and grayscale**
    - Generate random 3-channel BGR and 1-channel grayscale images of various sizes
    - Verify each of the 5 new image processing functions returns a non-None result without exception
    - **Validates: Requirements 16.4**

- [x] 2. Implement new Display, Logic, Camera, AI Vision, and Robotics source functions
  - [x] 2.1 Add 3 new functions to `src/modules/library/functions/display_blocks.py`
    - Implement `Draw_Line(camera_frame, x1, y1, x2, y2, color='green')` — cv2.line wrapper with color name resolution
    - Implement `Draw_Text_Box(camera_frame, text, x, y, bg_color='blue', text_color='white')` — draws filled rectangle + cv2.putText
    - Implement `Stack_Images(image1, image2, direction='horizontal')` — np.hstack/np.vstack with auto-resize
    - Each function must include docstring, try/except with `[Display]` prefixed error, and safe default return
    - _Requirements: 2.1, 2.3, 2.5, 16.2, 16.3_

  - [x] 2.2 Update shortcut module `display.py` to re-export the 3 new Display functions
    - Add `Draw_Line`, `Draw_Text_Box`, `Stack_Images` to the explicit import list
    - _Requirements: 2.4_

  - [x] 2.3 Add 2 new functions to `src/modules/library/functions/logic_blocks.py`
    - Implement `Get_Timestamp()` — returns `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
    - Implement `Compare_Values(value1, value2)` — returns `value1 == value2` as bool
    - Each function must include docstring, try/except with `[Logic]` prefixed error, and safe default return
    - _Requirements: 3.2, 3.4, 3.5, 16.2, 16.3_

  - [x] 2.4 Update shortcut module `logic.py` to re-export the 2 new Logic functions
    - Add `Get_Timestamp`, `Compare_Values` to the explicit import list
    - _Requirements: 3.3_

  - [x] 2.5 Add 2 new functions to `src/modules/library/functions/camera_blocks.py`
    - Implement `Set_Camera_Resolution(capture_camera, width=640, height=480)` — sets CAP_PROP_FRAME_WIDTH/HEIGHT
    - Implement `Capture_Snapshot(capture_camera, countdown=0)` — reads single frame with optional countdown print each second
    - Each function must include docstring, try/except with `[Camera]` prefixed error, and safe default return
    - _Requirements: 4.3, 4.5, 16.2, 16.3_

  - [x] 2.6 Update shortcut module `camera.py` to re-export the 2 new Camera functions
    - Add `Set_Camera_Resolution`, `Capture_Snapshot` to the explicit import list
    - _Requirements: 4.4_

  - [x] 2.7 Add 2 new functions to `src/modules/library/functions/ai_vision_blocks.py`
    - Implement `Get_Detection_Count(results)` — extracts count from ONNX/Engine/YuNet result formats
    - Implement `Crop_Detection(camera_frame, results, index=0)` — crops bounding box region, returns None if index out of bounds with friendly error
    - Each function must include docstring, try/except with `[AI Vision]` prefixed error, and safe default return
    - _Requirements: 5.3, 5.5, 16.2, 16.3_

  - [x] 2.8 Update shortcut module `ai_vision.py` to re-export the 2 new AI Vision functions
    - Add `Get_Detection_Count`, `Crop_Detection` to the explicit import list
    - _Requirements: 5.4_

  - [x] 2.9 Add `Sweep_Servo` to `src/modules/library/functions/robotics.py` (source file)
    - Implement `Sweep_Servo(pin='S1', start_angle=0, end_angle=180, step=10, delay=0.05)` — iterates from start_angle to end_angle calling Set_Servo at each position with delay pause
    - Must include docstring, try/except with `[Robotics]` prefixed error, and ORC Hub connection check
    - _Requirements: 6.3, 6.5, 16.2, 16.3_

  - [x] 2.10 Update shortcut module `robotics.py` (root) to re-export `Sweep_Servo`
    - Add `Sweep_Servo` to the explicit import list
    - _Requirements: 6.4_

  - [ ]* 2.11 Write property test for Compare_Values correctness (Property 4)
    - **Property 4: Compare_Values correctness**
    - Generate random pairs of ints, floats, strings, bools, None
    - Verify `Compare_Values(a, b)` returns a bool equal to `a == b`
    - **Validates: Requirements 3.5**

  - [ ]* 2.12 Write property test for Sweep_Servo iteration sequence (Property 5)
    - **Property 5: Sweep_Servo iteration sequence**
    - Generate random start_angle, end_angle (0–180), step (1–90)
    - Mock Set_Servo and verify it is called with the correct ascending angle sequence
    - **Validates: Requirements 6.5**

  - [ ]* 2.13 Write property test for Get_Timestamp format (Property 7)
    - **Property 7: Get_Timestamp returns valid datetime string**
    - Invoke Get_Timestamp multiple times
    - Verify each result is a non-empty string parseable as `%Y-%m-%d %H:%M:%S`
    - **Validates: Requirements 3.4**

- [x] 3. Checkpoint — Verify all new source functions and shortcut modules
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Add all 15 new block entries to `definitions.py` with bilingual metadata
  - [x] 4.1 Add 5 Image Processing entries to the `LIBRARY_FUNCTIONS["Image Processing"]` category
    - Add `threshold_image`, `blend_images`, `split_channels`, `equalize_histogram`, `detect_contours`
    - Each entry must include: `desc`, `desc_vi`, `params` (each param with `name`, `type`, `desc`, `desc_vi`), `returns` (with `type`, `desc`, `desc_vi`), `usage`, `import_statement`, `source_func`, `source_module`
    - Return types must use recognized Hint System vocabulary: `Image (ndarray)` or `List`
    - `import_statement` must be `"import image"`, `source_module` must be `"src.modules.library.functions.image_processing"`
    - _Requirements: 1.1, 1.2, 1.5, 7.1, 7.2, 7.3, 8.1_

  - [x] 4.2 Add 3 Display & Dashboard entries to the `LIBRARY_FUNCTIONS["Display & Dashboard"]` category
    - Add `Draw_Line`, `Draw_Text_Box`, `Stack_Images`
    - Each entry with full bilingual metadata (desc_vi, params[].desc_vi, returns.desc_vi)
    - Return type `Image (ndarray)` for all three
    - `import_statement`: `"import display"`, `source_module`: `"src.modules.library.functions.display_blocks"`
    - _Requirements: 2.1, 2.2, 2.5, 7.1, 7.2, 7.3, 8.1_

  - [x] 4.3 Add 2 Logic Operations entries to the `LIBRARY_FUNCTIONS["Logic Operations"]` category
    - Add `Get_Timestamp`, `Compare_Values`
    - Each entry with full bilingual metadata
    - Return types: `Text (str)` for Get_Timestamp, `Boolean` for Compare_Values
    - `import_statement`: `"import logic"`, `source_module`: `"src.modules.library.functions.logic_blocks"`
    - _Requirements: 3.1, 7.1, 7.2, 7.3, 8.1_

  - [x] 4.4 Add 2 Camera entries to the `LIBRARY_FUNCTIONS["Camera"]` category
    - Add `Set_Camera_Resolution`, `Capture_Snapshot`
    - Each entry with full bilingual metadata
    - Return types: `None` for Set_Camera_Resolution, `Image (ndarray)` for Capture_Snapshot
    - `import_statement`: `"import camera"`, `source_module`: `"src.modules.library.functions.camera_blocks"`
    - _Requirements: 4.1, 4.2, 7.1, 7.2, 7.3, 8.1_

  - [x] 4.5 Add 2 AI Vision Core entries to the `LIBRARY_FUNCTIONS["AI Vision Core"]` category
    - Add `Get_Detection_Count`, `Crop_Detection`
    - Each entry with full bilingual metadata
    - Return types: `Number (int)` for Get_Detection_Count, `Image (ndarray)` for Crop_Detection
    - `import_statement`: `"import ai_vision"`, `source_module`: `"src.modules.library.functions.ai_vision_blocks"`
    - _Requirements: 5.1, 5.2, 7.1, 7.2, 7.3, 8.1_

  - [x] 4.6 Add 1 Robotics entry to the `LIBRARY_FUNCTIONS["Robotics"]` category
    - Add `Sweep_Servo`
    - Entry with full bilingual metadata
    - Return type: `None`
    - `import_statement`: `"import robotics"`, `source_module`: `"src.modules.library.functions.robotics"`
    - _Requirements: 6.1, 6.2, 7.1, 7.2, 7.3, 8.1_

  - [ ]* 4.7 Write property test for return type vocabulary (Property 1)
    - **Property 1: Return types use recognized Hint System vocabulary**
    - For each of the 15 new block definitions, verify `returns.type` is in the recognized vocabulary set
    - **Validates: Requirements 1.5, 2.5, 8.1**

  - [ ]* 4.8 Write property test for bilingual metadata completeness (Property 2)
    - **Property 2: Bilingual metadata completeness**
    - For each of the 15 new block definitions, verify `desc_vi` is non-empty, every `params[].desc_vi` is non-empty, and `returns.desc_vi` is non-empty
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [x] 5. Checkpoint — Verify definitions registry and hint system integration
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Migrate curriculum filenames and add ORDER metadata
  - [x] 6.1 Update `_parse_lesson_metadata()` in `main.py` to extract the ORDER field
    - Add `ORDER` to the metadata parser logic
    - Parse as integer, default to `999` if missing
    - _Requirements: 14.3_

  - [x] 6.2 Update `populate_curriculum_hub()` sort logic in `main.py`
    - Primary sort: LEVEL group (Beginner → Intermediate → Advanced)
    - Secondary sort: ORDER ascending within each level
    - Tertiary sort: alphabetical filename (tiebreaker)
    - _Requirements: 14.2_

  - [x] 6.3 Rename all 38 existing curriculum files to remove numeric prefix
    - Rename `1_face_detection.py` → `face_detection.py`, `2_object_detection.py` → `object_detection.py`, etc. for all 38 files
    - Add `# ORDER: N` to each file's metadata header preserving current sequence (1–38)
    - _Requirements: 13.1, 13.2, 14.1, 14.4_

  - [x] 6.4 Update all codebase references to renamed curriculum files
    - Update `agent.md` references to old numbered filenames
    - Update `.kiro/specs/` documents referencing old filenames
    - Grep Python source files for any hardcoded curriculum filename references and update
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [x] 7. Checkpoint — Verify curriculum migration
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Create new Beginner curriculum examples (4 files)
  - [x] 8.1 Create `curriculum/threshold_lab.py`
    - Beginner example teaching `threshold_image` with adjustable cutoff
    - Metadata: TITLE, TITLE_VI, LEVEL=Beginner, ICON, COLOR=#22c55e, DESC, DESC_VI, ORDER=39
    - Use only Camera, Image Processing, Display, Logic, Variables blocks (no AI Vision or Robotics)
    - Use Clean Module Import System with module-prefixed calls
    - Include inline comments explaining each step
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 13.3_

  - [x] 8.2 Create `curriculum/image_blender.py`
    - Beginner example teaching `blend_images` + `Load_Image` — blending camera feed with a loaded image
    - Metadata: TITLE, TITLE_VI, LEVEL=Beginner, ICON, COLOR=#22c55e, DESC, DESC_VI, ORDER=40
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 13.3_

  - [x] 8.3 Create `curriculum/channel_splitter.py`
    - Beginner example teaching `split_channels` + `Stack_Images` — viewing individual R/G/B channels side-by-side
    - Metadata: TITLE, TITLE_VI, LEVEL=Beginner, ICON, COLOR=#22c55e, DESC, DESC_VI, ORDER=41
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 13.3_

  - [x] 8.4 Create `curriculum/contour_finder.py`
    - Beginner example teaching `detect_contours` + `threshold_image` — finding and drawing object outlines
    - Metadata: TITLE, TITLE_VI, LEVEL=Beginner, ICON, COLOR=#22c55e, DESC, DESC_VI, ORDER=42
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 13.3_

- [x] 9. Create new Intermediate curriculum examples (4 files)
  - [x] 9.1 Create `curriculum/face_crop_gallery.py`
    - Intermediate example teaching `Crop_Detection` + `Save_Frame` — detecting faces and cropping each one
    - Metadata: TITLE, TITLE_VI, LEVEL=Intermediate, ICON, COLOR=#eab308, DESC, DESC_VI, ORDER=43
    - Must use blocks from at least 3 different categories
    - Use `Show_Image` and `Observe_Variable` for display output
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.3_

  - [x] 9.2 Create `curriculum/smart_timestamp_logger.py`
    - Intermediate example teaching `Get_Timestamp` + `Get_Detection_Count` — logging detections with timestamps
    - Metadata: TITLE, TITLE_VI, LEVEL=Intermediate, ICON, COLOR=#eab308, DESC, DESC_VI, ORDER=44
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.3_

  - [x] 9.3 Create `curriculum/side_by_side_filters.py`
    - Intermediate example teaching `Stack_Images` + multiple image filters — comparing original vs filtered in split view
    - Metadata: TITLE, TITLE_VI, LEVEL=Intermediate, ICON, COLOR=#eab308, DESC, DESC_VI, ORDER=45
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.3_

  - [x] 9.4 Create `curriculum/contrast_enhancer.py`
    - Intermediate example teaching `equalize_histogram` + AI detection — auto-enhancing low-contrast images
    - Metadata: TITLE, TITLE_VI, LEVEL=Intermediate, ICON, COLOR=#eab308, DESC, DESC_VI, ORDER=46
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.3_

- [x] 10. Create new Advanced curriculum examples (4 files)
  - [x] 10.1 Create `curriculum/smart_traffic_monitor.py`
    - Advanced example teaching `Get_Detection_Count` + `Get_Timestamp` + ONNX — counting and logging vehicles
    - Metadata: TITLE, TITLE_VI, LEVEL=Advanced, ICON, COLOR=#f97316, DESC, DESC_VI, ORDER=47
    - Must integrate blocks from 4+ categories demonstrating a cohesive real-world scenario
    - _Requirements: 12.1, 12.2, 12.4, 12.5, 13.3_

  - [x] 10.2 Create `curriculum/panoramic_servo_scanner.py`
    - Advanced example teaching `Sweep_Servo` + AI detection — sweeping servo while detecting objects
    - Metadata: TITLE, TITLE_VI, LEVEL=Advanced, ICON, COLOR=#f97316, DESC, DESC_VI, ORDER=48
    - Include `# ⚠️ WARNING: This example requires ORC Hub hardware` comment
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 13.3_

  - [x] 10.3 Create `curriculum/object_isolation_studio.py`
    - Advanced example teaching `Crop_Detection` + `Stack_Images` + filters — detecting, cropping, filtering, and displaying in grid
    - Metadata: TITLE, TITLE_VI, LEVEL=Advanced, ICON, COLOR=#f97316, DESC, DESC_VI, ORDER=49
    - _Requirements: 12.1, 12.2, 12.4, 12.5, 13.3_

  - [x] 10.4 Create `curriculum/hi_res_capture_station.py`
    - Advanced example teaching `Set_Camera_Resolution` + `Capture_Snapshot` — switching resolutions for detection vs capture
    - Metadata: TITLE, TITLE_VI, LEVEL=Advanced, ICON, COLOR=#f97316, DESC, DESC_VI, ORDER=50
    - _Requirements: 12.1, 12.2, 12.4, 12.5, 13.3_

- [x] 11. Checkpoint — Verify all new curriculum examples
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Write remaining property tests and final validation
  - [ ]* 12.1 Write property test for curriculum metadata completeness (Property 3)
    - **Property 3: Curriculum metadata header completeness**
    - For all curriculum files (existing + new), verify all 8 required header fields (TITLE, TITLE_VI, LEVEL, ICON, COLOR, DESC, DESC_VI, ORDER) are present with non-empty values
    - Verify ORDER parses as a valid integer
    - **Validates: Requirements 10.3, 11.3, 12.2, 14.1**

  - [ ]* 12.2 Write unit tests for definition registry structure
    - Verify all 15 new entries exist in correct categories with correct fields
    - Verify import_statement and usage match expected module prefix patterns
    - Verify no `{digit}_*.py` files remain in curriculum/ after rename
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 9.1, 9.2_

  - [ ]* 12.3 Write unit tests for specific function behaviors
    - Test `Crop_Detection` returns None for out-of-bounds index
    - Test `Capture_Snapshot` countdown behavior
    - Test `Set_Camera_Resolution` handles None camera gracefully
    - Test `Stack_Images` auto-resize behavior
    - _Requirements: 5.5, 4.5, 16.3_

- [x] 13. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation after each major phase
- Property tests validate universal correctness properties from the design document
- All new function blocks MUST have bilingual descriptions (EN/VI) in desc, params, and returns
- All new blocks integrate with the existing hint system via recognized Type_Chain vocabulary — no hint system code changes needed
- The AI Assistant Bot's `_extract_func_context()` reads from LIBRARY_FUNCTIONS dynamically — no code changes needed
- The implementation language is Python throughout (matching the existing codebase)
