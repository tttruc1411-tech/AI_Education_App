``````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````# Implementation Plan: Library Full Examples

## Overview

Expand the AI Coding Lab's Function Library with 20 new blocks across 6 categories (including a new Variables category), then create 35 curriculum example programs (numbered 4–38) demonstrating progressive learning from basic camera concepts through AI detection to complex multi-category integrations. All new blocks integrate with the existing hint system type scanner. New examples use `Show_Image` + `Observe_Variable` instead of `Update_Dashboard`.

## Tasks

- [x] 1. Create new source files for Variables, Display, and Logic blocks
  - [x] 1.1 Create `src/modules/library/functions/variables.py` with identity functions
    - Implement `Create_Text(value)`, `Create_Number(value)`, `Create_Decimal(value)`, `Create_Boolean(value)`, `Create_List(value)`
    - Each function returns its input cast to the appropriate type (str, int, float, bool, list)
    - `Create_List` returns `[]` when value is None
    - _Requirements: 2.1–2.9_

  - [x] 1.2 Create `src/modules/library/functions/display_blocks.py` with visualization functions
    - Implement `Show_FPS(camera_frame)` — calculates FPS from elapsed time, overlays text at top-left, returns annotated frame
    - Implement `Show_Image(camera_frame)` — encodes frame as JPEG base64, prints `IMG:{base64}` to stdout, flushes
    - Implement `Observe_Variable(var_name, var_value)` — prints `VAR:{name}:{value}` to stdout, flushes
    - Implement `Draw_Rectangle(camera_frame, x, y, width, height, color)` — draws colored rectangle, returns frame
    - Implement `Draw_Circle(camera_frame, center_x, center_y, radius, color)` — draws colored circle, returns frame
    - Color map: green, red, blue, yellow, white with fallback to green for unknown colors
    - _Requirements: 5.1–5.7_

  - [x] 1.3 Create `src/modules/library/functions/logic_blocks.py` with utility functions
    - Implement `Wait_Seconds(seconds)` — calls `time.sleep(float(seconds))`
    - Implement `Print_Message(message)` — calls `print(message)`
    - _Requirements: 6.1, 6.3_

  - [ ]* 1.4 Write property tests for Variables identity functions
    - **Property 4: Type scanner correctly registers function outputs**
    - **Validates: Requirements 1.3, 2.6**

  - [ ]* 1.5 Write property tests for display block shape preservation
    - **Property 8: Image processing shape preservation**
    - **Validates: Requirements 5.1, 5.2, 5.3**

- [x] 2. Extend existing source files with new functions
  - [x] 2.1 Add `Save_Frame` and `Load_Image` to `src/modules/library/functions/ai_blocks.py`
    - `Save_Frame(camera_frame, file_path)` — writes image to disk via `cv2.imwrite`, prints confirmation; handles None frame
    - `Load_Image(file_path)` — reads image via `cv2.imread`, returns ndarray or None with descriptive error if file missing
    - _Requirements: 3.1–3.7_

  - [x] 2.2 Add 5 new functions to `src/modules/library/functions/image_processing.py`
    - `adjust_brightness(input_image, factor)` — multiplies pixels by factor, clamps to 0–255, returns uint8
    - `rotate_image(input_image, angle)` — rotates around center without cropping using expanded bounding box
    - `crop_image(input_image, x, y, width, height)` — returns sliced region via NumPy indexing
    - `draw_text(input_image, text, x, y)` — overlays white text using cv2.putText, returns frame
    - `convert_to_hsv(input_image)` — converts BGR to HSV via cv2.cvtColor
    - _Requirements: 4.1–4.8_

  - [ ]* 2.3 Write property test for Save/Load round-trip
    - **Property 5: Save/Load image round-trip**
    - **Validates: Requirements 3.5, 3.6**

  - [ ]* 2.4 Write property test for brightness clamping
    - **Property 6: Brightness adjustment clamping**
    - **Validates: Requirements 4.1, 4.7**

  - [ ]* 2.5 Write property test for HSV round-trip
    - **Property 7: HSV color conversion round-trip**
    - **Validates: Requirements 4.5**

  - [ ]* 2.6 Write property test for crop dimensions
    - **Property 9: Crop output dimensions**
    - **Validates: Requirements 4.3**

- [x] 3. Checkpoint — Verify all new source files
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Update definitions.py registry with all 20 new blocks
  - [x] 4.1 Add the new `Variables` category to `LIBRARY_FUNCTIONS`
    - Add category with color `#14b8a6`, icon `📦`
    - Add entries for `Create_Text`, `Create_Number`, `Create_Decimal`, `Create_Boolean`, `Create_List`
    - Each entry: `desc`, `params` (with name/type/desc), `returns` (with type/desc), `usage`, `import_statement`, `source_func`, `source_module`
    - All types from recognized vocabulary: `"Text (str)"`, `"Number"`, `"Number (float)"`, `"Boolean"`, `"List"`
    - _Requirements: 2.1–2.9, 1.1, 1.2, 1.6_

  - [x] 4.2 Add `Save_Frame` and `Load_Image` entries to the `Camera` category
    - `Save_Frame`: params `camera_frame` (Image), `file_path` (Text (str)); returns None
    - `Load_Image`: param `file_path` (Text (str)); returns `Image (ndarray)`
    - Usage snippets follow assignment pattern for Load_Image, statement pattern for Save_Frame
    - Import statements reference `ai_blocks`
    - _Requirements: 3.1–3.4, 11.1–11.5_

  - [x] 4.3 Add 5 new entries to the `Image Processing` category
    - `adjust_brightness`, `rotate_image`, `crop_image`, `draw_text`, `convert_to_hsv`
    - All params use `"Image (ndarray)"` for input_image, appropriate types for other params
    - All return `"Image (ndarray)"`
    - Import statements reference `image_processing`
    - _Requirements: 4.1–4.6, 11.1–11.5_

  - [x] 4.4 Add 5 new entries to the `Display & Dashboard` category
    - `Show_FPS`, `Draw_Rectangle`, `Draw_Circle`, `Show_Image`, `Observe_Variable`
    - `Show_Image` and `Observe_Variable` reference `display_blocks` module
    - `Show_FPS`, `Draw_Rectangle`, `Draw_Circle` also reference `display_blocks`
    - Keep existing `Update_Dashboard` unchanged for backward compatibility
    - _Requirements: 5.1–5.6, 11.1–11.5_

  - [x] 4.5 Add 3 new entries to the `Logic Operations` category
    - `Wait_Seconds`: param `seconds` (Number (float)), returns None, import references `logic_blocks`
    - `Repeat_N_Times`: param `count` (Number (int)), returns Control Flow, `source_func: None`, `source_module: None`, `import_statement: ""`
    - `Print_Message`: param `message` (Text (str)), returns None, import references `logic_blocks`
    - `Repeat_N_Times` usage is a for-loop snippet (like Loop_Forever pattern)
    - _Requirements: 6.1–6.5, 11.1–11.6_

  - [ ]* 4.6 Write property tests for registry completeness and type vocabulary
    - **Property 1: Registry type vocabulary validity**
    - **Property 2: Function block metadata completeness**
    - **Property 3: Usage snippet format consistency**
    - **Validates: Requirements 1.1, 1.2, 1.6, 11.1–11.5**

- [x] 5. Checkpoint — Verify registry and hint system integration
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Create beginner curriculum examples (4–16)
  - [x] 6.1 Create `curriculum/4_my_first_camera.py`
    - Beginner: Init_Camera, Get_Camera_Frame, Show_Image, Close_Camera in a loop
    - Metadata: TITLE, TITLE_VI, LEVEL=Beginner, ICON, COLOR=#3b82f6, DESC, DESC_VI
    - No AI blocks; inline comments explaining each step
    - _Requirements: 7.1, 7.14, 7.15, 7.16, 7.17, 7.18, 10.1–10.4_

  - [x] 6.2 Create `curriculum/5_image_filters_lab.py`
    - Beginner: Camera feed → convert_to_gray → apply_blur → detect_edges → flip_image → Show_Image
    - Demonstrates image processing pipeline and Type_Chain
    - _Requirements: 7.2, 7.14, 7.16, 7.17, 7.18, 10.1–10.4_

  - [x] 6.3 Create `curriculum/6_save_load_pictures.py`
    - Beginner: Save_Frame to save snapshot, Load_Image to reload, Show_Image to display
    - _Requirements: 7.3, 7.14, 7.16, 10.1–10.4_

  - [x] 6.4 Create `curriculum/7_mirror_selfie_mode.py`
    - Beginner: Camera + flip_image(horizontal) in Loop_Forever for real-time mirror
    - _Requirements: 7.4, 7.14, 7.16, 7.18, 10.1–10.4_

  - [x] 6.5 Create `curriculum/8_brightness_controller.py`
    - Beginner: Create_Decimal for factor, adjust_brightness on live feed, Show_Image + Observe_Variable
    - _Requirements: 7.5, 7.14, 7.16, 7.18, 10.1–10.4_

  - [x] 6.6 Create `curriculum/9_photo_rotator.py`
    - Beginner: Create_Number for angle, rotate_image on live feed, Show_Image + Observe_Variable
    - _Requirements: 7.6, 7.14, 7.16, 7.18, 10.1–10.4_

  - [x] 6.7 Create `curriculum/10_text_overlay_studio.py`
    - Beginner: Create_Text for message, draw_text on live feed, Show_Image
    - _Requirements: 7.7, 7.14, 7.16, 7.18, 10.1–10.4_

  - [x] 6.8 Create `curriculum/11_shape_drawing_canvas.py`
    - Beginner: Camera + Draw_Rectangle + Draw_Circle on live feed, Show_Image
    - _Requirements: 7.8, 7.14, 7.16, 10.1–10.4_

  - [x] 6.9 Create `curriculum/12_edge_detection_explorer.py`
    - Beginner: Create_Number for thresholds, detect_edges on live feed, Show_Image + Observe_Variable
    - _Requirements: 7.9, 7.14, 7.16, 7.18, 10.1–10.4_

  - [x] 6.10 Create `curriculum/13_color_space_explorer.py`
    - Beginner: convert_to_hsv on live feed, display both BGR and HSV via Show_Image
    - _Requirements: 7.10, 7.14, 7.16, 10.1–10.4_

  - [x] 6.11 Create `curriculum/14_photo_crop_frame.py`
    - Beginner: Create_Number for x, y, width, height; crop_image on live feed, Show_Image
    - _Requirements: 7.11, 7.14, 7.16, 7.18, 10.1–10.4_

  - [x] 6.12 Create `curriculum/15_blur_intensity_lab.py`
    - Beginner: Create_Number for kernel_size, apply_blur on live feed, Show_Image + Observe_Variable
    - _Requirements: 7.12, 7.14, 7.16, 7.18, 10.1–10.4_

  - [x] 6.13 Create `curriculum/16_grayscale_converter.py`
    - Beginner: convert_to_gray on live feed, Show_Image, inline comments about color channels
    - _Requirements: 7.13, 7.14, 7.16, 7.17, 10.1–10.4_

- [x] 7. Checkpoint — Verify beginner examples
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Create intermediate curriculum examples (17–26)
  - [x] 8.1 Create `curriculum/17_smart_face_counter.py`
    - Intermediate: YuNet face detection + Draw_Detections + Show_FPS + If_Condition + Create_Number threshold + Print_Message alert
    - Uses Show_Image + Observe_Variable; blocks from Camera, AI Vision, Display, Logic, Variables
    - _Requirements: 8.1, 8.11, 8.12, 8.13, 10.1–10.4_

  - [x] 8.2 Create `curriculum/18_image_processing_pipeline.py`
    - Intermediate: Chain convert_to_gray → apply_blur → detect_edges → adjust_brightness on live feed
    - Show_Image + Observe_Variable
    - _Requirements: 8.2, 8.11, 8.13, 10.1–10.4_

  - [x] 8.3 Create `curriculum/19_color_explorer_hsv.py`
    - Intermediate: convert_to_hsv + adjust_brightness + draw_text + Draw_Rectangle on live feed
    - _Requirements: 8.3, 8.11, 8.13, 10.1–10.4_

  - [x] 8.4 Create `curriculum/20_face_triggered_filter.py`
    - Intermediate: YuNet detection + If_Else_Control to apply convert_to_gray + apply_blur only when face detected
    - Show_Image + Observe_Variable
    - _Requirements: 8.4, 8.11, 8.12, 8.13, 10.1–10.4_

  - [x] 8.5 Create `curriculum/21_object_counter_alert.py`
    - Intermediate: ONNX model + Draw_Detections_MultiClass + If_Condition + Print_Message alert on threshold
    - Show_Image + Observe_Variable
    - _Requirements: 8.5, 8.11, 8.12, 8.13, 10.1–10.4_

  - [x] 8.6 Create `curriculum/22_fps_performance_monitor.py`
    - Intermediate: Show_FPS + convert_to_gray + detect_edges to show computational cost
    - Show_Image
    - _Requirements: 8.6, 8.11, 8.13, 10.1–10.4_

  - [x] 8.7 Create `curriculum/23_face_detection_annotations.py`
    - Intermediate: YuNet + Draw_Detections + draw_text (face count label) + Draw_Rectangle (status bar)
    - Show_Image + Observe_Variable
    - _Requirements: 8.7, 8.11, 8.13, 10.1–10.4_

  - [x] 8.8 Create `curriculum/24_timed_photo_capture.py`
    - Intermediate: YuNet detection in Loop_Forever + Wait_Seconds countdown + Save_Frame on face detect
    - Show_Image
    - _Requirements: 8.8, 8.11, 8.12, 10.1–10.4_

  - [x] 8.9 Create `curriculum/25_repeat_capture_series.py`
    - Intermediate: Repeat_N_Times loop + adjust_brightness + draw_text (frame counter) + Save_Frame sequential
    - Show_Image
    - _Requirements: 8.9, 8.11, 8.12, 10.1–10.4_

  - [x] 8.10 Create `curriculum/26_custom_object_detector.py`
    - Intermediate: Load_Engine_Model + Run_Engine_Model + Draw_Engine_Detections + Show_Image + Observe_Variable
    - _Requirements: 8.10, 8.11, 10.1–10.4_

- [x] 9. Checkpoint — Verify intermediate examples
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Create advanced curriculum examples (27–38)
  - [x] 10.1 Create `curriculum/27_security_camera.py`
    - Advanced: ONNX detection + Draw_Detections_MultiClass + Show_FPS + draw_text "ALERT" + If_Condition/If_Else_Control
    - Camera + AI Vision + Image Processing + Display + Logic
    - _Requirements: 9.1, 9.13, 9.14, 9.15, 10.1–10.4_

  - [x] 10.2 Create `curriculum/28_smart_photo_booth.py`
    - Advanced: YuNet face detection + adjust_brightness + draw_text + Draw_Rectangle border + If_Condition + Save_Frame
    - _Requirements: 9.2, 9.13, 9.14, 9.15, 10.1–10.4_

  - [x] 10.3 Create `curriculum/29_ai_image_gallery.py`
    - Advanced: ONNX detection + Draw_Detections_MultiClass + draw_text + Save_Frame + Repeat_N_Times
    - _Requirements: 9.3, 9.13, 9.14, 9.15, 10.1–10.4_

  - [x] 10.4 Create `curriculum/30_face_following_robot.py`
    - Advanced: YuNet + Draw_Detections + face center calculation + Set_Servo + If_Else_Control
    - Include ORC_Hub hardware warning comment
    - _Requirements: 9.4, 9.13, 9.14, 9.15, 9.16, 10.1–10.5_

  - [x] 10.5 Create `curriculum/31_multi_model_comparison.py`
    - Advanced: Load both YuNet and ONNX models, run on same frame, Show_FPS + Create_Number counters
    - Show_Image + Observe_Variable for side-by-side comparison
    - _Requirements: 9.5, 9.13, 9.14, 9.15, 10.1–10.4_

  - [x] 10.6 Create `curriculum/32_object_tracker_stats.py`
    - Advanced: ONNX + Draw_Detections_MultiClass + Create_Number cumulative counters + If_Condition + draw_text stats + Show_FPS
    - Camera + AI Vision + Image Processing + Display + Logic + Variables
    - _Requirements: 9.6, 9.13, 9.14, 9.15, 10.1–10.4_

  - [x] 10.7 Create `curriculum/33_smart_doorbell.py`
    - Advanced: YuNet + If_Else_Control + Print_Message + draw_text "Welcome!" + Draw_Rectangle banner + Save_Frame + Wait_Seconds cooldown
    - _Requirements: 9.7, 9.13, 9.14, 9.15, 10.1–10.4_

  - [x] 10.8 Create `curriculum/34_robot_obstacle_avoider.py`
    - Advanced: ONNX detection + Draw_Detections_MultiClass + If_Else_Control + DC_Run + DC_Stop
    - Include ORC_Hub hardware warning comment
    - _Requirements: 9.8, 9.13, 9.14, 9.15, 9.16, 10.1–10.5_

  - [x] 10.9 Create `curriculum/35_night_vision_effect.py`
    - Advanced: convert_to_gray + adjust_brightness(high) + detect_edges + convert_to_hsv + draw_text "NIGHT VISION" + Show_FPS
    - _Requirements: 9.9, 9.13, 9.14, 9.15, 10.1–10.4_

  - [x] 10.10 Create `curriculum/36_face_attendance_logger.py`
    - Advanced: YuNet + Create_Number counter + If_Condition + Print_Message log + draw_text count + Wait_Seconds cooldown
    - _Requirements: 9.10, 9.13, 9.14, 9.15, 10.1–10.4_

  - [x] 10.11 Create `curriculum/37_ai_art_filter.py`
    - Advanced: YuNet + If_Else_Control + convert_to_gray + detect_edges + adjust_brightness + flip_image chain
    - Display both original and filtered versions
    - _Requirements: 9.11, 9.13, 9.14, 9.15, 10.1–10.4_

  - [x] 10.12 Create `curriculum/38_motor_speed_dashboard.py`
    - Advanced: Get_Speed for 2 motors + Create_Decimal RPM vars + draw_text RPM overlay + Draw_Rectangle gauge + If_Condition threshold + Show_FPS
    - Include ORC_Hub hardware warning comment
    - _Requirements: 9.12, 9.13, 9.14, 9.15, 9.16, 10.1–10.5_

- [x] 11. Checkpoint — Verify advanced examples
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Write remaining property-based tests and final validation
  - [ ]* 12.1 Write property test for curriculum metadata completeness
    - **Property 10: Curriculum metadata completeness**
    - **Validates: Requirements 10.2, 7.15, 8.11, 9.13**

  - [ ]* 12.2 Write property test for curriculum file naming convention
    - **Property 11: Curriculum file naming convention**
    - **Validates: Requirements 10.1**

  - [ ]* 12.3 Write property test for beginner AI exclusion
    - **Property 12: Beginner examples exclude AI Vision blocks**
    - **Validates: Requirements 7.14**

  - [ ]* 12.4 Write property test for robotics hardware warning
    - **Property 13: Robotics examples include hardware warning**
    - **Validates: Requirements 10.5, 9.16**

  - [ ]* 12.5 Write unit tests for individual function behaviors
    - Test Load_Image with non-existent path returns None
    - Test Show_FPS timing with known delay
    - Test Wait_Seconds delay accuracy
    - Test Variables identity: Create_Text("hello") == "hello", Create_Number(42) == 42, etc.
    - Test control flow blocks have source_func: None
    - _Requirements: 3.7, 5.7, 6.1, 2.2–2.6, 11.6_

- [x] 13. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation after each major phase
- Property tests validate universal correctness properties from the design document
- All 35 new curriculum examples (4–38) use `Show_Image` + `Observe_Variable` instead of `Update_Dashboard`
- Existing curriculum files (1–3) and `Update_Dashboard` block are untouched for backward compatibility
- The implementation language is Python throughout (matching the existing codebase)
