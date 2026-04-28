# 🤖 AI Agent Handover: Project "AI Coding Lab"

## 1. Project Overview
A professional, education-focused Python development environment built with **PyQt5**. The app features a high-fidelity "Running Mode" dashboard designed to teach AI concepts through a "Learning Hub," a smart Code Editor, and real-time Camera/Results feedback.

## 2. Core Architecture
* **UI Framework**: Python PyQt5 using `.ui` XML files loaded dynamically via `loadUi`.
* **Localization Engine**: Custom `translations.py` module providing a reactive dictionary for all UI text, tooltips, and terminal hints.
* **Frontend-Backend Bridge**: Function Library logic mapped to Python injection managers.
* **Target Hardware**: NVIDIA Jetson Orin Nano (8GB unified RAM, JetPack 6.x, Ubuntu 22.04, Python 3.10).
* **Dev Machine**: Windows, Python 3.9.

## 3. Supported Features

### 🌍 Dual-Language Support (EN ⇆ VI)
* **Status**: ✅ **COMPLETED**
* **Toggle System**: Minimalist, professional "EN / VI" text-based toggle integrated into the main header—matching the mode-switcher aesthetic.
* **Reactive Core**: All labels, success/error hints, tooltips, and terminal status update instantly upon language switch.
* **AI Vocabulary**: Optimized for Vietnamese technical standards (e.g., using **"Nhận diện"** for Recognition/Detection).
* **Localized Curriculum**: All core lessons (Face Detection, YOLOv10) support dual-language headers (`TITLE_VI`, `DESC_VI`) in the Learning Hub.

### 📐 Dual Resolution Mode
* **Status**: ✅ **COMPLETED**
* **Toggle**: `btnResToggle` (💻 icon) in the main header switches between Standard (1280×800) and Small/16:9 (1024×600) layouts.
* **Mechanism**: `refresh_ui_resolution(is_transition)` in `main.py` uses regex-based stylesheet patching + direct widget property overrides.
* **UI Scaling Specifications**:
    | Component | Standard (1280×800) | Small (1024×600) | Note |
    | :--- | :--- | :--- | :--- |
    | **Panel Titles** | 20px (Bold) | 12px (Bold) | Hub, Editor, Cam, Results |
    | **Console Titles** | 18px (Bold) | 10px (Bold) | Slightly smaller than panel titles |
    | **Console Header** | 44px (Fixed) | 36px (Fixed) | `setFixedHeight` prevents overlap |
    | **Collapsed Console** | 40px (Fixed) | 34px (Fixed) | |
    | **Hub Tabs Font** | 14px (Bold) | 8px (Bold) | |
    | **Hub Tabs Height** | 32px (Fixed) | 12px (Fixed) | |
    | **Editor Tab Bar** | 30px (Fixed) | 20px (Fixed) | |
    | **Editor Individual Tabs**| 8pt (Bold) | 6pt (Bold) | |
    | **Editor Tab Height** | 20px (Fixed) | 14px (Fixed) | Prevents clipping of 'p', 'y' |
    | **Run/Save Buttons** | 40px (Height) | 30px (Height) | 14px vs 10px font |
    | **Console Body** | 14px | 8px | Consolas / Monospace |
    | **Footer Labels** | 14px | 11px | Status and Timestamp |
* **Known Issue**: Some deeply nested form labels and metric cards in Training Mode still require a minimum floor of 8px to ensure readability on small screens.

### 📂 Workspace & File System (Adaptive Mode)
* **Smart Permissions**: 
    * **Code**: Full CRUD access.
    * **Model**: Restricted view. Foundation models (`yunet`, `yolo`) are protected. Binary files blocked from text editor.
    * **Data Folder (Visual Gallery)**: `IconMode` gallery using `QListWidget`. Automatically renders dataset images as 120x120 thumbnails.
* **Layout Stability**: Fixed vertical expansion bug; workspace now fills 100% of the vertical column.

### 📚 Learning Hub & Curriculum
* **Design**: Immersive cards with row-based alignment. Descriptions are now perfectly aligned with the "Load" buttons for a premium visual balance.
* **Vision Inference**: Multi-engine support including **Microsoft ONNX Runtime** (YOLOv10, YuNet) and **NVIDIA TensorRT** via Ultralytics for high-performance Jetson execution.
* **TensorRT Support**: ⚡ **LOGIC APPLIED** (Pending Jetson testing). Native support for `.engine` models via the Ultralytics YOLO framework, optimized for zero-latency inference.
* **Logic Operations**: Dedicated block category for `while True` and `if/else` control flow, using structural anchors (`# [START] / # [END]`) to teach Python scope.

### 📚 Function Library & Learning Hub
* **Categorical UI**: Functions are grouped into professional, color-coded categories (Camera, Image Processing, AI Vision, Display, Logic, Robotics, Variables).
* **Categorical Icons**: Unique 20px icons (📸, 🖼️, 🧠, 🎨, ⚡, 🤖, ✏️) are used for each group header and function block, providing clear visual hierarchy and accessibility.
* **Zen Mode Startup**: Categories are collapsed by default on application launch to keep the student workspace organized and focused.
* **Rich Definitions**: The `definitions.py` registry manages snippet injection, automatic imports, and source-code previews for every individual block.
* **Custom Color Themes**: Categories use modern HSL-inspired colors (Amber for Camera, Blue for Processing, Mint for AI, Indigo for Display, Pink for Logic, Violet for Robotics, Teal for Variables) for high-contrast usability.
* **Clean Module Import System (V3)**: Drag-and-drop generates a single `import module` line per module (e.g., `import camera`). Functions are called with module prefix (e.g., `camera.Init_Camera()`). See **"📦 Clean Module Import System"** section below for full details.

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
* **Read-Only Fixed Tags (Syntax Guardrails)**: Automatically detects and locks "Key" segments of code (e.g., `model_path =`, `cap = `, `id =`) to prevent accidental deletion or syntax corruption.
    *   **Logic**: Typing, Backspace, and Delete are blocked within protected segments.
    *   **Option A Deletion Policy**: To ensure students aren't "stuck," the system allows deleting an entire line if it is fully selected, enabling easy block removal while preventing partial syntax errors.

### 🧠 Deep Learning Dashboard (Training Mode)
* **Design**: High-fidelity, transparent glassmorphism design with vibrant color-coded headers (Indigo, Purple, Emerald) and 12px-16px rounded modern inputs.
* **Layout Structure**: Organized Three-Column Pipeline:
    1. **Data Classes**: Interactive class management with image count badges.
    2. **Training Config & Progress**: A 2.5:1 ratio vertical `QSplitter`, maximizing parameter visibility while keeping real-time performance curves (`matplotlib`) visible.
    3. **Fast Validation**: Auto-transitions from a locked placeholder to an active camera preview upon successful training completion.
* **Architecture Stability (V15)**: Zero `QGridLayout` policy. Completely replaced deprecated `margin` properties with explicit directional padding.
* **Geometry Engine**: Optimized window minimum-size constraints (lowered to 120px internally) to ensure the 1080p UI remains perfectly centered and crash-free even with the Windows Taskbar active.
* **BBox Editor Close Bug — FIXED**: When user closed the bounding box annotation editor via the "✕" button instead of finishing all images, the left panel header expanded downward and hid the Webcam/Upload/Label buttons. Root cause: `setVisible(False)` on the bbox panel did not collapse its layout space. Fix: `_close_bbox_panel()` now calls `self._bbox_panel.setFixedHeight(0)` to fully collapse it. `_open_bbox_editor()` restores proper height constraints when reopening.

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

### 🚀 Integrated Training Engine (YOLOv8)
* **Status**: ✅ **COMPLETED**
* **Engine**: Headless `ultralytics` YOLOv8n process launched as `QProcess`, optimized for **Jetson Orin Nano** (7.6GB shared CPU/GPU memory).
* **Jetson Orin Nano Optimizations**:
    *   `batch=1` — minimal batch to avoid OOM on 640x640 images.
    *   `workers=0` — in-process data loading (worker subprocesses eat shared memory).
    *   `cache='disk'` — disk cache instead of RAM (RAM competes with GPU on unified memory).
    *   `amp=True` — FP16 training saves memory; AMP safety check monkey-patched (`check_amp → True`) to avoid downloading an extra model that OOMs.
    *   `freeze=5` — freeze first 5 backbone layers for faster convergence with small datasets.
    *   Explicit `torch.cuda.empty_cache()` at every stage transition (post-training, pre-export, pre-validation).
* **Automated Data Preparation**:
    *   **Fixed Workspace**: Uses `src/modules/training/detection/` as the internal training site.
    *   **Smart Split**: Automatically performs a randomized 80/20 train/validation split of project images and annotations.
    *   **Dynamic Metadata**: Generates `dataset.yaml` on-the-fly based on active class names.
* **Real-time Synchronized Dashboard**:
    *   **Accuracy Chart**: Single large `matplotlib` chart showing mAP50 accuracy over epochs (loss displayed in metric card only). Chart has expanded height (220px min) with 12pt bold title.
    *   **Animated Progress**: Cycling "Training." / "Training.." / "Training..." dots on the epoch counter while waiting for first epoch to complete — gives immediate visual feedback that training is active.
    *   **Progress Tracking**: Smooth 1-100% progress bar and epoch counting synchronized with the backend process.
    *   **Collapsible Console**: Training log console hidden by default behind a "▶ Console" toggle button. Advanced users can expand to see detailed STATUS/SYSTEM messages.
* **Stdout IPC Protocol** (between `trainer.py` QProcess and main UI):
    *   `STATUS:{message}` — general status updates.
    *   `EPOCH:{current}:{total}:{loss}` — per-epoch metrics.
    *   `METRIC:acc:{value}` — mAP50 accuracy percentage.
    *   `RESULT_MODEL_PT:{path}` — PyTorch model location.
    *   `RESULT_MODEL_LOCAL:{path}` — local model path for validation.
* **Local Model Storage**: After training, `best.pt` is copied to `src/modules/training/best.pt` (overwritten each session). TensorRT export is **skipped** on Orin Nano to avoid C++-level OOM crashes.
* **Resilient Finish Handler**: `_on_train_finished` checks for `best.pt` existence even on non-zero exit codes — if a model file exists despite a subprocess crash, validation starts anyway.
* **Re-trainable**: After stopping validation, the "Start Training" button re-enables so users can iterate on their model.

### 🎯 Post-Training Fast Validation
* **Status**: ✅ **COMPLETED**
* **Auto-Start**: Validation camera launches automatically in the right panel after training completes — no manual step required.
* **Standalone Process**: `src/modules/training/validator.py` runs as an isolated `QProcess` (~100 lines, no app imports).
    *   Loads model via `ultralytics.YOLO(model_path, task='detect')`.
    *   Opens camera via `cv2.VideoCapture(0)`.
    *   Runs real-time inference loop with bounding box drawing (4-color palette matching the tag panel: Purple, Rose, Blue, Emerald).
    *   Streams annotated frames via `IMG:{base64}` stdout protocol (same as Running Mode).
* **Buffered Frame Decoding**: `_on_val_stdout` uses `_val_stdout_buf` to reassemble large base64 `IMG:` strings that arrive split across multiple `readAllStandardOutput()` calls — prevents corrupt JPEG errors.
* **Save Model**: "Save Model" button prompts for a name via `QInputDialog`, copies `best.pt` (or `.engine` if available) to `projects/model/{name}.ext`.
* **Stop Validation**: "Stop Validation" button kills the QProcess, releases camera/GPU, and re-enables the training button.

### 📂 Project Reload (Detection Mode)
* **Status**: ✅ **COMPLETED**
* **Reload Button**: Amber "📂" button in the project row opens a dropdown of existing detection projects (scanned from `projects/data/`).
* **Class Name Recovery**: Reads `classes.txt` from the project folder. Falls back to scanning annotation `.txt` files for the maximum class ID and generating placeholder names.
* **Class Persistence**: `_save_classes_txt()` writes class names to `projects/data/[project]/classes.txt` — called during annotation saves and before training starts.
* **Full State Restore**: Reloads all image thumbnails, populates the `MultiClassTagPanel`, detects image resolution (320 or 640) from the first image, updates all UI states including size toggle buttons and labels.
* **Overwrite Protection**: When initializing a project folder that already has data, a confirmation dialog warns the user before clearing existing images/annotations.

### 🤖 AI Assistant Bot (Running Mode)
* **Status**: ✅ **COMPLETED**
* **Location**: Floating circular `🤖` button parented to the `monacoPlaceholder` (QScintilla editor widget) in Running Mode. Positioned at ~68% down the editor height, right side, 26px from edge to clear the scrollbar.
* **Trigger**: Click the bot button → `AssistantChatPanel` floats above it with fade-in animation (`QGraphicsOpacityEffect`). Second click hides it. Switching to Training Mode hides it and unloads the model to free RAM.
* **Panel Position**: Right-aligned inside the editor with 20px margin to clear the scrollbar. Panel size: 370×420–600px (normal), 300×320–420px (small screen). All fonts bumped +2pt from original for readability.
* **Models** (2 options, user-switchable via dropdown):
    | Model | Size | Chat Format | Best For |
    |-------|------|-------------|----------|
    | `Qwen2.5-Coder-1.5B-Instruct` Q4_K_M | ~1.12 GB | ChatML | Code tasks (recommended) |
    | `Gemma-3-1B-IT` Q4_K_M | ~0.81 GB | Gemma turn | Lightweight/memory-constrained |
* **Model Storage**: `src/modules/LLM/llm_model/` (co-located with the LLM module).
* **Backend**: `llama-cpp-python` v0.3.20 built with CUDA (`-DGGML_CUDA=on`). Runs in a **subprocess worker** for GPU isolation from PyTorch/YOLO.
* **Inference speed**: ~18 tok/s CPU fallback, ~35–45 tok/s GPU (Jetson Orin Nano).
* **⚠️ CRITICAL ARCHITECTURE — Subprocess Worker (DO NOT REVERT)**:
    * **Problem**: On Jetson Orin Nano (8 GB shared RAM, 256 MB CMA), PyTorch/YOLO and llama.cpp cannot both call `cudaMalloc` in the same process — CMA fragmentation causes OOM even with 3+ GB "free" RAM. Setting `CUDA_VISIBLE_DEVICES=""` after CUDA is already initialized has no effect.
    * **Solution**: LLM inference runs in a **separate subprocess** (`llm_worker.py`) that is launched by `assistant.py`. This subprocess has its own CUDA context, isolated from PyTorch/YOLO.
    * **CMA-Aware GPU/CPU Selection**: The worker reads `/proc/meminfo` CmaFree at load time. If CmaFree > 200 MB → GPU mode (`n_gpu_layers=999`). If CmaFree ≤ 200 MB → sets `CUDA_VISIBLE_DEVICES=""` before importing llama_cpp, then loads on CPU.
    * **IPC Protocol** (stdin/stdout JSON, line-buffered):
        * Parent → Worker: `{"action": "load", "model_path": "...", "config": {...}}`
        * Parent → Worker: `{"action": "infer", "prompt": "..."}`
        * Parent → Worker: `{"action": "quit"}`
        * Worker → Parent: `STATUS:ready:gpu` or `STATUS:ready:cpu`
        * Worker → Parent: `TOKEN:<text>` (streaming, one per token)
        * Worker → Parent: `STATUS:done` or `STATUS:error:<msg>`
    * **Why not in-process?**: Even with `n_gpu_layers=0`, llama-cpp-python v0.3.20 with CUDA compiled still allocates ~480 MB CUDA compute buffers if `ggml_cuda_init` detects a device. The ONLY way to prevent this is to hide the GPU BEFORE the library is imported — impossible in the main process where PyTorch already uses CUDA.
    * **GPU unlock**: To get consistent GPU inference, increase CMA: add `cma=1536M` to APPEND line in `/boot/extlinux/extlinux.conf` and reboot.
    * **Phi-3 removed**: Too large (2.39 GB) for the 2 GB GPU memory budget. Only Qwen and Gemma are available.

* **Module files**:
    * `src/modules/LLM/__init__.py` — Module init.
    * `src/modules/LLM/model_config.py` — Model registry (Qwen, Gemma) with paths, GPU layers, context, inference params. `set_active_model(key)` for runtime switching.
    * `src/modules/LLM/prompt_builder.py` — Prompt engineering hub (see "Prompt Architecture" below).
    * `src/modules/LLM/assistant.py` — `LLMAssistant` class: `load()`, `ask()`, `fix_error()`, `explain_code()`, `cancel()`, `unload()`. Launches `llm_worker.py` as subprocess and communicates via stdin/stdout JSON.
    * `src/modules/LLM/llm_worker.py` — **Standalone subprocess** for GPU LLM inference. Loads model with CUDA, streams tokens back via stdout. CMA-aware: auto-falls back to CPU if GPU memory unavailable.
    * `src/modules/LLM/chat_panel.py` — `AssistantChatPanel` + `MessageBubble` widgets with `QGraphicsOpacityEffect` fade-in animation.

* **Chat Panel Features**:
    * Header with status dot (🟡 loading / 🟢 ready / 🟣 thinking / 🔴 error) and animated "thinking..." dots
    * Model selector dropdown (switch between Qwen/Gemma at runtime)
    * Two quick-action buttons: **🔧 Fix Error** / **💡 Explain** (bilingual labels via `translations.py`)
    * Free-text input field with Enter-to-send (bilingual placeholder)
    * Streaming token-by-token response into chat bubbles
    * `retranslate(strings)` method — all UI text updates when language is switched

* **Bilingual Support (EN ⇆ VI)**:
    * All chat panel UI text (buttons, placeholders, status messages) uses translation keys from `translations.py` (`BOT_TITLE`, `BOT_FIX_BTN`, `BOT_EXPLAIN_BTN`, `BOT_INPUT_HINT`, etc.)
    * `lang` parameter flows through `main.py` → `assistant.py` → `prompt_builder.py`
    * System prompts and few-shot examples switch between English and Vietnamese
    * Fix error output format: EN uses `Line/Original/Fixed`, VI uses `Dòng/Gốc/Sửa`
    * `_postprocess_fix()` regex recognizes both formats

* **Prompt Architecture (Translator Pattern)**:
    * **Design Philosophy**: 1B/1.5B models cannot reliably analyze code. Python's built-in tools (`compile()`, traceback parsing) find the error; the LLM only *translates* it into kid-friendly language. This eliminates hallucination.
    * **System Prompts**: Minimal — just "You are a coding tutor for kids. Explain this Python error simply." No "common mistakes" lists (causes prompt leakage on small models).
    * **SYSTEM_PROMPT** (Ask/Explain): Contains numbered workflow (Init_Camera → Get_Camera_Frame → Load Model → Run Model → Draw → Update_Dashboard → while True loop). Explicitly states `Update_Dashboard()` is the ONLY way to show camera feed.
    * **Fix Error Flow** (`build_fix_prompt`):
        1. `_bot_fix()` in `main.py` runs `compile(code)` first
        2. If code compiles clean AND no console error → instant "Great job! No errors found. 🎉" (no LLM)
        3. If `compile()` catches SyntaxError → extract line number, error type, broken line
        4. If console has runtime error (NameError, ImportError, etc.) → extract from traceback
        5. Special handling for indentation errors: preserves leading spaces in `Original:`, pre-fills `Fixed:` with stripped version
        6. Special handling for "code after colon" (e.g. `while True:x = 1`): detects via previous-line analysis, provides kid-friendly "Press Enter after..." instruction
        7. LLM receives ONLY: error message + broken line + output format template. Zero room for hallucination.
    * **Ask Flow** (`build_prompt`):
        1. `_detect_missing_workflow()` checks code for missing pipeline steps (e.g. has `Draw_*` but no `Update_Dashboard`)
        2. If question matches display/show keywords AND workflow step is missing → instant pre-built answer (no LLM)
        3. `_extract_func_context()` scans code/question for known function names, injects parameter definitions from `definitions.py` (max 4 functions to save tokens)
        4. Falls through to LLM for general questions
    * **Explain Flow** (`build_explain_prompt`): Injects relevant function definitions from `definitions.py`, asks model to explain simply for a beginner.
    * **Function Context Injection**: `_load_func_cache()` lazy-loads all function definitions from `LIBRARY_FUNCTIONS` in `definitions.py`. `_extract_func_context(text)` finds mentioned functions and returns their descriptions, parameters, return types, and usage examples.

* **Windows GUI Compatibility Fixes** (Windows dev machine only — Jetson uses subprocess worker):
    * **suppress_stdout_stderr monkey-patch**: llama-cpp-python's `verbose=False` uses `os.dup/dup2` to redirect fd 1/2, which corrupts stdout/stderr permanently in PyQt5 GUI apps (no valid console handles). Fix: replace `suppress_stdout_stderr` with a no-op class at module import time.
    * **Debug print removal**: Removed `print(flush=True)` from `_on_token_signal` — crashes in GUI apps with no console.

* **Model Switching**:
    * `_bot_switch_model()` in `main.py`: cancels + unloads old model (kills worker subprocess), switches `ACTIVE_MODEL`, creates fresh `LLMAssistant`, loads new model (spawns new worker subprocess).
    * 3-second stabilization delay after model switch (silent — no UI message) to let the previous worker terminate cleanly.
    * First launch: no delay, instant "ready" message.

* **🟢 FIXED — Response truncated mid-sentence/Empty response on large code**:
    * `max_tokens` set to **150** (was 512). Implemented `_trim_code()` (lines > 300 chars truncated, total code 1500 chars max).

* **🟢 OPTIMIZED — Concise LLM responses for student readability**:
    * Reduced `max_tokens` 512 → 150, `repeat_penalty` 1.1 → 1.2, added `"\n\n\n"` stop token.
    * All system/user prompts rewritten with explicit brevity constraints (word/sentence limits).
    * Fix: "EXACTLY 3 lines" format. Runtime errors: "1 line, max 15 words." Ask: "1-2 sentences." Explain: "Max 3 bullet points."
    * Added `_postprocess_trim()` in `assistant.py` — hard trims ask (3 sentences) and explain (4 bullets) even if model ignores prompt.

* **🟢 FIXED — Blank response bubble**: Replaced `QTextEdit` with `QLabel` + `_BubbleBox` to bypass QScintilla stylesheet cascade.

* **🟢 FIXED — All models fail to load (WinError 1/6)**: Monkey-patched `suppress_stdout_stderr` to no-op. See "Windows GUI Compatibility Fixes" above.

* **🟢 FIXED — Gemma crash on inference**: Same root cause as loading — fd corruption from `suppress_stdout_stderr`. Monkey-patch fixes both.

* **🟢 FIXED — Crash on model switch**: Previous model's destructor writes to corrupted stderr. 3-second stabilization delay + monkey-patch prevents this.

* **🟢 FIXED — Chat panel crash on bot click**: `QPropertyAnimation` on `windowOpacity` only works on top-level windows. Replaced with `QGraphicsOpacityEffect` (from `QtWidgets`, not `QtGui`).

* **🟢 FIXED — LLM hallucination on fix errors**: Replaced complex prompt with Translator Pattern. Python finds the error, LLM just explains it. No "common mistakes" list to cause prompt leakage.

## 4. Stability & Performance
* **Custom Event Routing**: Implementation of a global `QEventFilter` for tooltips to bypass OS-level rendering restrictions.
* **Deferred Init**: Application launches instantly regardless of editor complexity.
* **Process Protection**: The Run/Stop button state is determined by the actual script execution lifecycle.
* **Init Order Logic**: All UI splitters and containers are fully initialized before the translation engine applies the first string map.

## 5. File Structure
* `main.py`: Central controller and UI integrator (~4800+ lines).
* `src/ui/training_mode.ui`: Training mode layout (3-column QSplitter with config/progress/validation panels).
* `src/ui/running_mode.ui`: Running mode layout.
* `src/ui/main_window.ui`: Main window shell with mode switcher.
* `src/modules/translations.py`: Global translation registry (EN/VI).
* `src/modules/advanced_editor.py`: The QScintilla custom logic (modular).
* `src/modules/training_components.py`: Reusable UI widgets (`MultiClassTagPanel` with `set_class_names()`, `lock_classes()`).
* `src/modules/training/trainer.py`: Backend YOLOv8 training script (QProcess). Handles dataset split, YAML generation, training loop with epoch/metric reporting, local model copy.
* `src/modules/training/validator.py`: Standalone post-training validation script (QProcess). Live camera inference with bounding box drawing and `IMG:` frame streaming.
* `src/modules/training/detection/`: Internal training workspace (auto-generated train/val splits + `dataset.yaml`).
* `src/modules/library/functions/ai_blocks.py`: **LEGACY** — Original monolithic block (Camera, YuNet, ONNX, TensorRT, Drawing). Kept for backward compatibility with existing student projects in `projects/code/`. New code uses the split modules below.
* `src/modules/library/functions/camera_blocks.py`: Camera functions (Init_Camera, Get_Camera_Frame, Close_Camera, Save_Frame, Load_Image).
* `src/modules/library/functions/ai_vision_blocks.py`: AI model loading & inference (Load_YuNet_Model, Run_YuNet_Model, Load/Run_ONNX_Model, Load/Run_Engine_Model).
* `src/modules/library/functions/drawing_blocks.py`: Detection drawing & dashboard (Draw_Detections, Draw_Detections_MultiClass, Draw_Engine_Detections, Update_Dashboard).
* `src/modules/library/functions/robotics.py`: Student-facing robotics blocks (DC_Run, DC_Stop, Get_Speed, Set_Servo).
* `src/modules/library/functions/motor_driver_v2.py`: Low-level I2C driver for OhStem Motor Driver V2 + `check_orc_hub()` probe.
* `src/modules/library/functions/motor.py`: Brain layer with async motor control (DCMotor class, run_time, run_until_stalled).
* `src/modules/library/definitions.py`: Master function registry for all Library categories.
* `src/modules/LLM/__init__.py`: LLM module init.
* `src/modules/LLM/model_config.py`: Model registry (Qwen2.5-Coder-1.5B, Gemma-3-1B-IT) with paths, GPU layers (999=all), inference params.
* `src/modules/LLM/prompt_builder.py`: Prompt engineering hub — Translator Pattern for fix errors, workflow detection for ask mode, function context injection from `definitions.py`. Supports EN/VI bilingual prompts.
* `src/modules/LLM/assistant.py`: `LLMAssistant` class — spawns subprocess worker, sends JSON commands via stdin, reads streaming tokens from stdout.
* `src/modules/LLM/llm_worker.py`: **Subprocess GPU worker** — loads model with CUDA, CMA-aware fallback to CPU. DO NOT merge into assistant.py (CUDA isolation requirement).
* `src/modules/LLM/chat_panel.py`: `AssistantChatPanel` + `MessageBubble` — floating chat UI.
* `src/modules/LLM/llm_model/`: LLM GGUF model files (Qwen2.5-Coder-1.5B, Gemma-3-1B-IT).

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
* [x] **Backend Training Engine**: Fully integrated YOLOv8n training engine with Jetson Orin Nano memory optimizations.
* [x] **Post-Training Fast Validation**: Auto-launching live camera detection stream after training completes.
* [x] **Project Reload**: Reload existing detection projects with class name recovery.
* [x] **Collapsible Training Console**: Toggle button for advanced users; collapsed by default.
* [x] **Training Progress Animation**: Animated "Training..." dots while waiting for first epoch.
* [x] **Resilient Training Pipeline**: Non-fatal TRT export, model availability check on crash, GPU memory cleanup.
* [x] **TensorRT Support**: Native support for `.engine` models (TRT export skipped on Orin Nano).
* [x] **Read-Only Fixed Tags**: Syntax protection system locking parameter names and assignment keys.
* [x] **BBox Editor Close Bug Fixed**: `setFixedHeight(0)` on close, height restored on reopen.
* [x] **AI Assistant Bot UI**: Floating 🤖 button in code editor, chat panel with Fix/Explain quick actions, streaming inference backend with Qwen2.5-Coder-1.5B.
* [x] **AI Assistant Bot — Fix blank response bubble**: Replaced `QTextEdit` with `QLabel` in `MessageBubble` to escape QScintilla stylesheet cascade.
* [x] **Gemma-3-1B-IT Model**: Added as third LLM option (~810 MB Q4_K_M). Gemma turn-based prompt format, download script, model registry entry. Requires `llama-cpp-python >= 0.3.8`.
* [x] **LLM Model Storage Relocation**: Moved GGUF files from `projects/model/llm/` to `src/modules/LLM/llm_model/`.
* [x] **llama-cpp-python Upgrade**: v0.3.2 → v0.3.20 (Windows dev machine) for Gemma 3 architecture support.
* [x] **verbose=False Windows Fix**: Monkey-patched `suppress_stdout_stderr` to no-op to prevent fd corruption in PyQt5 GUI apps.
* [x] **Model Switching Stability**: 3-second silent stabilization delay after model switch to let C-level destructor finish.
* [x] **Chat Panel Fade Animation Fix**: Replaced `windowOpacity` animation with `QGraphicsOpacityEffect` for child widgets.
* [x] **Debug Print Crash Fix**: Removed `print(flush=True)` from `_on_token_signal` that crashed in GUI apps without console.
* [x] **AI Bot Bilingual Support**: All chat panel UI text (buttons, placeholders, messages) uses translation keys. LLM prompts switch between EN/VI. Fix output uses `Dòng/Gốc/Sửa` in Vietnamese.
* [x] **Translator Pattern for Fix Errors**: Python's `compile()` finds syntax errors, console traceback finds runtime errors. LLM only translates the error into kid-friendly language. Eliminates hallucination on 1B models.
* [x] **Syntax Check Short-Circuit**: If code compiles clean and no console error, instant "No errors found 🎉" without LLM inference.
* [x] **Indentation Error Handling**: Preserves leading spaces in `Original:` line, pre-fills `Fixed:` with stripped version.
* [x] **Code-After-Colon Detection**: Detects `while True:code_here` pattern, provides kid-friendly "Press Enter after..." instruction.
* [x] **Runtime Error Support**: NameError, ImportError, AttributeError etc. detected from console traceback, sent to LLM with simple "explain and suggest fix" prompt.
* [x] **Workflow Missing Step Detection**: `_detect_missing_workflow()` checks for missing pipeline steps (Init_Camera, Load Model, Draw, Update_Dashboard, while loop). Instant pre-built answer for display/show questions without LLM.
* [x] **Function Context Injection**: `_extract_func_context()` scans code/question for known function names, injects parameter definitions from `definitions.py` into Ask/Explain prompts (max 4 functions). Not injected into Fix prompts.
* [x] **Kid-Friendly System Prompt**: Numbered workflow (1→7) explaining the AI camera pipeline. Explicitly states `Update_Dashboard()` is required for camera feed display. Rules enforce short answers, no full scripts.
* [ ] **Dataset Augmentation**: Add UI controls for Flip, Blur, and Noise simulations.
* [ ] **Small-screen font sizes**: Minimum font size floor of 8px needed in `refresh_ui_resolution()` for form labels, metric cards, and dataset summary labels.
* [ ] **Save Model on Jetson**: `_save_trained_model()` only saves `.engine` files — on Orin Nano TRT export is skipped, so the button always shows "No .engine model found". Needs fallback to save `.pt` or `.onnx`.
* [ ] **Resume Training label**: After stopping training, button shows "🚀 Resume Training" but clicking starts fresh. Label is misleading.
* [x] **Jetson llama-cpp-python upgrade**: Upgraded to v0.3.20 built with CUDA (`CMAKE_ARGS="-DGGML_CUDA=on"`). Supports Gemma 3 architecture + GPU inference.
* [x] **LLM Subprocess Worker (GPU Isolation)**: Moved LLM inference to `llm_worker.py` subprocess to avoid CUDA CMA conflict with PyTorch/YOLO. Auto-detects CMA availability for GPU/CPU mode.
* [x] **Phi-3 Removed**: Removed from model registry and combobox — too large (2.39 GB) for 2 GB GPU budget.
* [x] **llama-cpp-python _internals.py fix**: Patched `LlamaModel.close()` to use `getattr()` for `sampler`/`_exit_stack` attributes — prevents `AttributeError` crash when model fails to load.
* [ ] **Increase CMA for consistent GPU**: Add `cma=1536M` to `/boot/extlinux/extlinux.conf` APPEND line and reboot. Currently CMA=256MB is mostly consumed by Xorg/GNOME, forcing LLM to CPU fallback.

### 📚 Expanded Function Library & Curriculum (V2)
* **Status**: ✅ **COMPLETED**
* **Scope**: Expanded from 25 function blocks across 6 categories to **45 blocks across 7 categories**, plus **35 new curriculum examples** (38 total).
* **New Variables Category** (✏️ Teal `#14b8a6`):
    | Block | Snippet | Returns |
    |-------|---------|---------|
    | **Create_Text** | `my_text = Create_Text(value = 'Hello')` | `Text (str)` |
    | **Create_Number** | `my_number = Create_Number(value = '0')` | `Number` |
    | **Create_Decimal** | `my_decimal = Create_Decimal(value = '0.0')` | `Number (float)` |
    | **Create_Boolean** | `my_flag = Create_Boolean(value = 'True')` | `Boolean` |
    | **Create_List** | `my_list = Create_List(value = None)` | `List` |
* **New Camera Blocks**: `Save_Frame(camera_frame, file_path)` saves images to `projects/data/saved/` by default; `Load_Image(file_path)` loads from disk with error handling.
* **New Image Processing Blocks**: `adjust_brightness`, `rotate_image`, `crop_image`, `draw_text`, `convert_to_hsv` — all return `Image (ndarray)` for type-chain compatibility.
* **New Display & Dashboard Blocks**: `Show_FPS` (FPS overlay), `Show_Image` (streams frame via `IMG:` protocol), `Observe_Variable` (streams variable via `VAR:` protocol), `Draw_Rectangle`, `Draw_Circle`. `Show_Image` + `Observe_Variable` are granular alternatives to `Update_Dashboard` — new examples use the separated blocks.
* **New Logic Blocks**: `Wait_Seconds` (time.sleep wrapper), `Repeat_N_Times` (for-loop snippet), `Print_Message` (console output).
* **New Source Files**:
    * `src/modules/library/functions/variables.py` — Identity functions for typed variable creation.
    * `src/modules/library/functions/display_blocks.py` — FPS, Show_Image, Observe_Variable, Draw_Rectangle, Draw_Circle.
    * `src/modules/library/functions/logic_blocks.py` — Wait_Seconds, Print_Message.
* **Bilingual Function Descriptions**: Every function block in `definitions.py` now has `desc_vi`, `returns.desc_vi`, and `params[].desc_vi` fields for Vietnamese translations. The function library panel (`function_library.py`) and editor tooltips (`advanced_editor.py`) automatically switch based on `lang`.
* **Hint System Compatibility**: All new blocks use the recognized type vocabulary (`Image`, `Image (ndarray)`, `Text (str)`, `Number`, `Number (float)`, `Boolean`, `List`, etc.) so `_scan_variable_types()` in `advanced_editor.py` correctly registers variables and shows "Connect Logic" / "Type Mismatch" hints.

### 📚 Curriculum Examples (35 New, 38 Total)
* **Status**: ✅ **COMPLETED**
* **Progressive Difficulty**:
    * **Beginner** (13 examples, #4–#16): Vision-only — camera basics, image filters, save/load, mirror mode, brightness, rotation, text overlay, shapes, edge detection, color spaces, cropping, blur, grayscale. **No AI blocks**.
    * **Intermediate** (12 examples, #1–#2 original + #17–#26): AI detection + overlays — smart face counter, image processing pipeline, HSV explorer, face-triggered filter, object counter, FPS monitor, face annotations, timed capture, repeat series, custom detector.
    * **Advanced** (13 examples, #3 original + #27–#38): Multi-category integration — security camera, smart photo booth, AI gallery, face-following robot, multi-model comparison, object tracker stats, smart doorbell, obstacle avoider, night vision, attendance logger, AI art filter, motor dashboard.
* **Color Scheme**: Beginner = Green `#22c55e`, Intermediate = Yellow `#eab308`, Advanced = Orange `#f97316`.
* **All new examples use `Show_Image` + `Observe_Variable`** instead of `Update_Dashboard` for separation of concerns.
* **Robotics examples** (30, 34, 38) include `# ⚠️ WARNING: This example requires ORC Hub hardware` comment.
* **File Format**: `{number}_{snake_case_name}.py` with metadata headers: TITLE, TITLE_VI, LEVEL, ICON, COLOR, DESC, DESC_VI.

### 🎯 Level Navigation Bar (Examples Tab)
* **Status**: ✅ **COMPLETED**
* **Design**: Frosted purple-blue-cyan gradient pill bar (`QFrame#levelNavBar`) with 3 `LevelBadge` icon circles (⭐ Beginner, 🚀 Intermediate, 🏆 Advanced). Active badge gets a white frosted bubble; inactive badges show semi-transparent icons with hover glow.
* **Widget**: `LevelBadge(QWidget)` with `setAttribute(Qt.WA_StyledBackground, True)` for stylesheet background rendering. Uses `QWidget#lvlActive` / `QWidget#lvlInactive` objectName selectors.
* **Filtering**: `_apply_level_filter()` uses `setVisible(True/False)` on `(level, card)` tuples — no widget recreation. `_on_level_selected()` updates badge states and scrolls to top.
* **Layout**: `_setup_level_navigation()` replaces the flat `hubContentLayout` with Level_Navigation_Bar + `QScrollArea` at runtime. Called after `hubStackedWidget` is found in `__init__`.
* **Dual Resolution**: Nav bar height 36px (small) / 50px (normal). Badge circles 28px (small) / 40px (normal). Updated in `refresh_ui_resolution()`.
* **Default**: Beginner level selected on launch.
* **⚠️ Init Order**: `_setup_level_navigation()` MUST be called AFTER `hubStackedWidget` is assigned (line ~935), not before. Previous bug: calling it at line ~851 caused silent failure because `hubStackedWidget` was `None`.

### 🎨 Hub Tab Unified Design (Examples / Functions / Workspace)
* **Status**: ✅ **COMPLETED**
* **Design**: Active tab gets frosted white bubble (`rgba(255,255,255,0.92)`) with purple text (`#6d28d9`); inactive tabs get semi-transparent background with white text and hover glow. Matches the level navigation bar aesthetic.
* **Implementation**: `_switch_hub_tab(index)` calls `_update_hub_tab_styles(active_index)` which applies resolution-aware stylesheets. Connected via `tabExamples/tabFunctions/tabWorkspace` click signals.
* **Resolution-aware**: Font sizes and padding scale with `is_small` flag in `_update_hub_tab_styles()`.

### 🔧 Function Library Info Panel Resolution Scaling
* **Status**: ✅ **COMPLETED**
* **Fix**: `FunctionInfoPanel` now stores `self._is_small` and uses it for all label sizes, code block heights, and font sizes. Previously `_bold_label()` had `is_small=False` hardcoded.
* **Scaling**: Section titles 10px/14px, param/return descriptions 10px/16px, snippet block 28-50px/42-84px height, source code block 120px/200px height with 5pt/7pt font.

### 📦 Clean Module Import System (V3)
* **Status**: ✅ **COMPLETED**
* **Problem**: Drag-and-drop generated verbose per-function imports like `from src.modules.library.functions.ai_blocks import Init_Camera` — one line per function, cluttering student code.
* **Solution**: Replaced with clean `import module` style. Each module is a short, descriptive name. Functions are called with module prefix (e.g., `camera.Init_Camera()`).
* **Architecture**: Thin shortcut modules at the project root re-export from the actual source files in `src/modules/library/functions/`. The project root is on `PYTHONPATH` (set by `QProcess` in `main.py`), so `import camera` resolves to `camera.py` at root.
* **Module Mapping**:
    | Shortcut Module | Source File | Contents |
    |-----------------|-------------|----------|
    | `camera.py` | `camera_blocks.py` | Init_Camera, Get_Camera_Frame, Close_Camera, Save_Frame, Load_Image |
    | `ai_vision.py` | `ai_vision_blocks.py` | Load_YuNet_Model, Run_YuNet_Model, Load/Run_ONNX_Model, Load/Run_Engine_Model |
    | `drawing.py` | `drawing_blocks.py` | Draw_Detections, Draw_Detections_MultiClass, Draw_Engine_Detections, Update_Dashboard |
    | `display.py` | `display_blocks.py` | Show_FPS, Show_Image, Observe_Variable, Draw_Rectangle, Draw_Circle |
    | `image.py` | `image_processing.py` | convert_to_gray, resize_image, apply_blur, detect_edges, flip_image, adjust_brightness, rotate_image, crop_image, draw_text, convert_to_hsv |
    | `logic.py` | `logic_blocks.py` | Wait_Seconds, Print_Message |
    | `variables.py` | `variables.py` | Create_Text, Create_Number, Create_Decimal, Create_Boolean, Create_List |
    | `robotics.py` | `robotics.py` | DC_Run, DC_Stop, Get_Speed, Set_Servo |
* **Student Code Example**:
    ```python
    import camera
    import ai_vision
    import drawing

    detector = ai_vision.Load_YuNet_Model('projects/model/face_detection_yunet_2023mar.onnx')
    cap = camera.Init_Camera()

    while True:
        frame = camera.Get_Camera_Frame(cap)
        ai_vision.Run_YuNet_Model(detector, frame)
        _, faces = detector.detect(frame)
        count = drawing.Draw_Detections(frame, faces, label="Face")
        drawing.Update_Dashboard(frame, var_name="Faces", var_value=count)
    ```
* **definitions.py Changes**: Every function entry's `import_statement` is now `"import camera"` / `"import ai_vision"` / etc. The `usage` field includes the module prefix (e.g., `"camera.Init_Camera()"`). The `source_module` field points to the actual source file (e.g., `"src.modules.library.functions.camera_blocks"`).
* **Hint System Update**: All regex patterns in `advanced_editor.py` (`_scan_variable_types`, `scan_for_blanks`) now use `(?:\w+\.)?` optional prefix before function names to match both `Init_Camera(...)` and `camera.Init_Camera(...)`. Substring checks in `_show_assistance` and `prompt_builder.py` work naturally since `camera.Init_Camera` contains `Init_Camera`.
* **Backward Compatibility**: The original `ai_blocks.py` source file is preserved — existing student projects in `projects/code/` that use the old `from src.modules.library.functions.ai_blocks import ...` style continue to work.
* **All 38 curriculum examples** updated to use the new module names.

### 🎨 Editor Selection Color Fix
* **Status**: ✅ **COMPLETED**
* **Fix**: Changed `setSelectionForegroundColor` from `white` to navy `#1e293b` in `advanced_editor.py`. Selected text now shows dark navy against the light purple (`#c4b5fd`) selection background for better readability.

## Updated File Structure (New Files)
* `camera.py`: Root-level shortcut module → `import camera` for student scripts.
* `ai_vision.py`: Root-level shortcut module → `import ai_vision` for student scripts.
* `drawing.py`: Root-level shortcut module → `import drawing` for student scripts.
* `display.py`: Root-level shortcut module → `import display` for student scripts.
* `image.py`: Root-level shortcut module → `import image` for student scripts.
* `logic.py`: Root-level shortcut module → `import logic` for student scripts.
* `variables.py`: Root-level shortcut module → `import variables` for student scripts.
* `robotics.py`: Root-level shortcut module → `import robotics` for student scripts.
* `src/modules/library/functions/camera_blocks.py`: Camera functions (split from ai_blocks.py).
* `src/modules/library/functions/ai_vision_blocks.py`: AI model loading & inference (split from ai_blocks.py).
* `src/modules/library/functions/drawing_blocks.py`: Detection drawing & dashboard (split from ai_blocks.py).
* `src/modules/library/functions/variables.py`: Variable constructor blocks (Create_Text, Create_Number, Create_Decimal, Create_Boolean, Create_List).
* `src/modules/library/functions/display_blocks.py`: Display blocks (Show_FPS, Show_Image, Observe_Variable, Draw_Rectangle, Draw_Circle).
* `src/modules/library/functions/logic_blocks.py`: Logic utility blocks (Wait_Seconds, Print_Message).
* `curriculum/my_first_camera.py` through `curriculum/motor_speed_dashboard.py`: 38 curriculum example files (numeric prefixes removed, ORDER metadata added).

## Updated Next Steps
* [x] **Expanded Function Library**: 20 new blocks across 7 categories (including new Variables ✏️ category).
* [x] **35 New Curriculum Examples**: Progressive Beginner → Intermediate → Advanced path.
* [x] **Level Navigation Bar**: Frosted gradient pill bar with animated badge filtering.
* [x] **Hub Tab Unified Design**: Frosted white bubble active state for Examples/Functions/Workspace tabs.
* [x] **Bilingual Function Descriptions**: All `desc_vi`, `returns.desc_vi`, `params[].desc_vi` fields in definitions.py.
* [x] **Function Info Panel Resolution Scaling**: All section titles, descriptions, and code blocks scale with resolution mode.
* [x] **Save_Frame Default Path**: Images saved to `projects/data/saved/` by default.
* [x] **Editor Tooltip Translation**: `_lang` attribute on `AdvancedPythonEditor` synced from `set_language()`, "Returns" label translated.
* [x] **Original Example Reclassification**: `face_detection.py` moved from Beginner to Intermediate (uses AI blocks). `llm_chatbot.py` color updated to orange.
* [x] **Clean Module Import System (V3)**: Split `ai_blocks.py` into `camera`, `ai_vision`, `drawing`. Renamed `display_blocks` → `display`, `image_processing` → `image`, `logic_blocks` → `logic`. All 38 curriculum examples and `definitions.py` updated. Hint system regex patterns updated with `(?:\w+\.)?` optional module prefix.
* [x] **Editor Selection Color Fix**: Changed selection foreground from white to navy `#1e293b` for better readability against purple selection background.
* [x] **KDI App Mascot (Hatchling)**: Created high-quality SVG assets for the KDI Mascot in 5 distinct emotional states (Neutral, Happy, Questioning, Sad, Error) for interactive app feedback, saved to `src/modules/courses/`.
