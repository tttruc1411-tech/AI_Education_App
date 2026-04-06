# 🤖 AI Agent Handover: Project "AI Coding Lab"

## 1. Project Overview
A professional, education-focused Python development environment built with **PyQt5**. The app features a high-fidelity "Running Mode" dashboard designed to teach AI concepts through a "Learning Hub," a smart Code Editor, and real-time Camera/Results feedback.

## 2. Core Architecture
* **UI Framework**: Python PyQt5 using `.ui` XML files loaded dynamically via `loadUi`.
* **Localization Engine**: Custom `translations.py` module providing a reactive dictionary for all UI text, tooltips, and terminal hints.
* **Frontend-Backend Bridge**: Function Library logic mapped to Python injection managers.

## 3. Supported Features

### 🌍 Dual-Language Support (EN ⇆ VI)
* **Status**: ✅ **COMPLETED**
* **Toggle System**: Minimalist, professional "EN / VI" text-based toggle integrated into the main header—matching the mode-switcher aesthetic.
* **Reactive Core**: All labels, success/error hints, tooltips, and terminal status update instantly upon language switch.
* **AI Vocabulary**: Optimized for Vietnamese technical standards (e.g., using **"Nhận diện"** for Recognition/Detection).
* **Localized Curriculum**: All core lessons (Face Detection, YOLOv10) support dual-language headers (`TITLE_VI`, `DESC_VI`) in the Learning Hub.

### 📂 Workspace & File System (Adaptive Mode)
* **Smart Permissions**: 
    * **Code**: Full CRUD access.
    * **Model**: Restricted view. Foundation models (`yunet`, `yolo`) are protected. Binary files blocked from text editor.
    * **Data Folder (Visual Gallery)**: `IconMode` gallery using `QListWidget`. Automatically renders dataset images as 120x120 thumbnails.
* **Layout Stability**: Fixed vertical expansion bug; workspace now fills 100% of the vertical column.

### 📚 Learning Hub & Curriculum
* **Design**: Immersive cards with row-based alignment. Descriptions are now perfectly aligned with the "Load" buttons for a premium visual balance.
* **Vision Inference**: Powered by **Microsoft ONNX Runtime**, ensuring stable execution for YOLOv10 and YuNet blocks.
* **Logic Operations**: Dedicated block category for `while True` and `if/else` control flow, using structural anchors (`# [START] / # [END]`) to teach Python scope.

### 📚 Function Library & Learning Hub
* **Categorical UI**: Functions are grouped into professional, color-coded categories (Camera, Image Processing, AI Vision, Display, Logic, Robotics).
* **Categorical Icons**: Unique 20px icons (📸, 🖼️, 🧠, 🎨, ⚡, 🤖) are used for each group header and function block, providing clear visual hierarchy and accessibility.
* **Zen Mode Startup**: Categories are collapsed by default on application launch to keep the student workspace organized and focused.
* **Rich Definitions**: The `definitions.py` registry manages snippet injection, automatic imports, and source-code previews for every individual block.
* **Custom Color Themes**: Categories use modern HSL-inspired colors (Amber for Camera, Blue for Processing, Mint for AI, Indigo for Display, Pink for Logic, Violet for Robotics) for high-contrast usability.

### 🤖 Robotics (ORC Hub) — Motor Driver V2 Integration
* **Status**: ✅ **COMPLETED**
* **Hardware**: OhStem Motor Driver V2 connected via I2C (Bus 1, Address `0x54`). Wiring: SDA→Pin27, SCL→Pin28, GND→Pin30.
* **Supported Ports**: M1–M4 (DC motors), E1–E2 (Encoder DC motors with RPM reading), S1–S4 (Servos).
* **Function Blocks** (4 blocks in the Function Library, Violet `#8b5cf6` category):
    | Block | Snippet | Behavior |
    |-------|---------|----------|
    | **DC_Run** | `DC_Run(pin='M1', speed=50, time_ms=None)` | Run motor at speed (-100 to 100). `time_ms=None` runs forever; set a value (e.g. `2000`) for timed run. |
    | **DC_Stop** | `DC_Stop(pin='M1')` | Stop a specific motor. Omit `pin` to stop ALL motors. |
    | **Get_Speed** | `rpm = Get_Speed(pin='E1')` | Read encoder RPM (E1/E2 only). Returns `0.0` if hub disconnected. |
    | **Set_Servo** | `Set_Servo(pin='S1', angle=90)` | Rotate servo to angle 0–180. Servo holds position (no stop command — hardware limitation). |
* **Shared Driver Singleton**: `_get_driver()` in `robotics.py` initializes the I2C connection once on first use. Uses `_driver_init_attempted` flag to prevent repeated retry on failure. All functions print a friendly `[Robotics]` message and return gracefully if the hub is absent.
* **Pin Resolution**: Students use string names (`'M1'`, `'E1'`, `'S3'`) — internally mapped to bitmask constants via `_PIN_MAP` / `_SERVO_MAP`.
* **ORC Hub Connection Indicator**: A live status dot in the `resFooter` bar (bottom of the Results column). Green = connected, Gray = disconnected. Includes a refresh button (`↻`) to re-probe I2C. Auto-checks 500ms after app launch via `QTimer.singleShot`. Fully bilingual (EN/VI) via translation keys `ORC_HUB_LABEL`, `ORC_CONNECTED`, `ORC_DISCONNECTED`, `ORC_REFRESH_TIP`.
* **Lightweight I2C Probe**: `check_orc_hub()` in `motor_driver_v2.py` reads the WHO_AM_I register without instantiating the full driver — safe, fast (~10ms), non-destructive.

### 🍱 Ghost Block & Smart Logic
* **Horizontal Layers (Contextual Scope)**: Real-time background tinting during drag-and-drop that shows the "Main", "Loop", and "Condition" blocks. Empty lines are automatically color-coded based on the *intended* scope by scanning the previous code blocks.
* **Occupied Line Protection (Smart Injection)**: Dropping content on an existing code line automatically creates a new line and pushes the existing code down, preventing accidental logic merging.
* **Visual Anchors**: Deep integration with structural markers (e.g., `# [ENDIF]`, `# [ENDLOOP]`) to handle de-indentation and closure of Python scopes for students visually.

### 💻 Advanced Code Editor (Pro IDE Engine)
* **Engine**: **QScintilla** implementation.
* **Aesthetics**: VS Code "Dark+" or "Professional Light" (Beige) adaptive themes.
* **IDE Features**: Interactive line numbers, intelligent auto-indentation, and smart snippet injection.
* **Ghost Block System**: Semi-transparent, color-coded visual guidance (Green, Blue, Purple) that matches the current block's indentation level.
* **Smart Contextual Indentation**: Custom logic that automatically detects the correct indentation level based on preceding colons (`:`) or end markers. The user only chooses the drop line; the system manages the exact column alignment.

### 🧠 Deep Learning Dashboard (Training Mode)
* **Design**: High-fidelity, transparent glassmorphism design with vibrant color-coded headers (Indigo, Purple, Emerald) and 12px-16px rounded modern inputs.
* **Layout Structure**: Organized Three-Column Pipeline:
    1. **Data Classes**: Interactive class management with image count badges.
    2. **Training Config & Progress**: A 2.5:1 ratio vertical `QSplitter`, maximizing parameter visibility while keeping real-time performance curves (`matplotlib`) visible.
    3. **Fast Validation**: Auto-transitions from a locked placeholder to an active camera preview upon successful training completion.
* **Architecture Stability (V15)**: Zero `QGridLayout` policy. Completely replaced deprecated `margin` properties with explicit directional padding.
* **Geometry Engine**: Optimized window minimum-size constraints (lowered to 120px internally) to ensure the 1080p UI remains perfectly centered and crash-free even with the Windows Taskbar active.

### 📂 Project-Based Data Workflow
* **Mandatory Initialization**: The UI prevents data collection (Webcam/Upload) until a valid "Project Name" is verified.
* **Smart Mode-Reset**: Toggling between Recognition and Detection automatically clears the project state, resets the naming field, and purges existing class blocks to ensure data purity.
* **Dynamic Directory Structure**: 
    * **Recognition Mode**: Uses `projects/data/[project_name]/[class_name]/` (Category-specific subfolders required for classification training).
    * **Detection Mode**: Uses `projects/data/[project_name]/` (A flattened structure where all images and YOLO `.txt` annotations are saved directly in the project root for streamlined single-class detection).
* **Hardware Locking**: Image resolution buttons (320px/640px) are locked once a project is initialized to ensure consistent dataset dimensions.

### 🏷️ Multi-Class Detection Workflow (Pro Edition)
* **Status**: ✅ **COMPLETED**
* **Unified Pipeline**: Replaced single-class detection with a high-fidelity 4-class labeling engine.
* **Smart UI Expansion**: Detection cards now use a dynamic `QGridLayout` (4 columns) that expands to fill the entire vertical dashboard workspace (300px+ height).
* **Decoupled Workflow**: 
    * **Webcam Mode**: Optimized for rapid, raw image data collection only (Drawing disabled).
    * **Label Series**: Specialized annotation loop with normalized YOLOv8 coordinate mapping.
* **Interactive Tooltips**: Application-wide `DarkTooltipFilter` that replaces native Windows tooltips with a custom dark-navy (`#1e293b`) design, ensuring consistent aesthetics even on disabled/locked widgets.
* **UX Safety Locks**: 
    * **Name Protection**: Project and Class name inputs are permanently disabled as soon as 'Webcam', 'Upload', or 'Labeling' begins to prevent folder-desync.
    * **Naming Standards**: Strict `[a-zA-Z]+` alphabetic validation enforced via `QRegularExpressionValidator` to prevent numeric collisions with YOLO class IDs.
* **Professional Canvas**: `AnnotationLabel` enhanced with mouse-tracking crosshairs, interactive resizing handles, and color-coded tag overlays.
* **Realistic Metadata**: The 'Start Training' action now validates the project structure and automatically generates a compliant `dataset.yaml` in the project root.

## 4. Stability & Performance
* **Custom Event Routing**: Implementation of a global `QEventFilter` for tooltips to bypass OS-level rendering restrictions.
* **Deferred Init**: Application launches instantly regardless of editor complexity.
* **Process Protection**: The Run/Stop button state is determined by the actual script execution lifecycle.
* **Init Order Logic**: All UI splitters and containers are fully initialized before the translation engine applies the first string map.

## 5. File Structure
* `main.py`: Central controller and UI integrator.
* `src/modules/translations.py`: Global translation registry (EN/VI).
* `src/modules/advanced_editor.py`: The QScintilla custom logic (modular).
* `src/modules/training_components.py`: Reusable UI widgets (Tag Panels, etc.).
* `src/modules/library/functions/ai_blocks.py`: Functional block scripts.
* `src/modules/library/functions/robotics.py`: Student-facing robotics blocks (DC_Run, DC_Stop, Get_Speed, Set_Servo).
* `src/modules/library/functions/motor_driver_v2.py`: Low-level I2C driver for OhStem Motor Driver V2 + `check_orc_hub()` probe.
* `src/modules/library/functions/motor.py`: Brain layer with async motor control (DCMotor class, run_time, run_until_stalled).
* `src/modules/library/definitions.py`: Master function registry for all Library categories.

## 6. Next Steps for Development
* [x] **Dual-Language**: Full Vietnamese/English support across the entire GUI.
* [x] **Smart Contextual Ghost Block System**: Context-aware indentation zones.
* [x] **Training Mode**: High-fidelity, stable 3-column pipeline with dynamic splitters.
* [x] **Annotation Canvas**: Interactive YOLOv8-compatible bounding box editor.
* [x] **Batch Labeling Workflow**: "Label Series" engine for rapid dataset annotation.
* [x] **UX Guardrails**: Strict naming validation and interaction-based input locking.
* [x] **Premium Tooltips**: Custom dark-themed tooltip engine for OS-agnostic styling.
* [x] **Robotics Blocks**: 4 function blocks (DC_Run, DC_Stop, Get_Speed, Set_Servo) wired to Motor Driver V2 via I2C.
* [x] **ORC Hub Status Indicator**: Live connection dot in footer with refresh button and bilingual tooltips.
* [ ] **Backend Training Engine**: Connect the actual YOLOv8 `ultralytics` training engine.
* [ ] **Dataset Augmentation**: Add UI controls for Flip, Blur, and Noise simulations.
* [ ] **Model Export**: Implement a 1-click export of trained `.pt` weights.