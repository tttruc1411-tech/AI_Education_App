# src/modules/library/definitions.py
#
# Each function entry has:
#   desc          — short one-line description
#   params        — list of {name, type, desc} dicts for the info panel
#   returns       — {type, desc} for the return value
#   usage         — the snippet injected into the editor when dragged
#   import_statement — the import line prepended automatically
#   source_func   — exact function name in the source file (for inspect.getsource)
#   source_module — dotted module path used to import the source at runtime

LIBRARY_FUNCTIONS = {
    "Camera": {
        "color": "#f97316",  # Orange 500
        "icon": "📸",
        "functions": {
            "Init_Camera": {
                "desc": "Initialize the default Jetson/Webcam camera (ID: 0)",
                "params": [],
                "returns": {
                    "type": "Capture Object",
                    "desc": "A handle to the active camera device",
                },
                "usage": "capture_camera = Init_Camera()",
                "import_statement": "from src.modules.library.functions.ai_blocks import Init_Camera",
                "source_func": "Init_Camera",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Get_Camera_Frame": {
                "desc": "Capture the current live frame from the initialized camera",
                "params": [
                    {
                        "name": "capture_camera",
                        "type": "Capture Object",
                        "desc": "The camera handle returned by Init_Camera",
                    },
                ],
                "returns": {
                    "type": "Image",
                    "desc": "The live picture (frame) to analyze",
                },
                "usage": "camera_frame = Get_Camera_Frame(capture_camera = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Get_Camera_Frame",
                "source_func": "Get_Camera_Frame",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Close_Camera": {
                "desc": "Safely shut down the camera driver and close all windows",
                "params": [
                     {"name": "capture_camera", "type": "Capture Object", "desc": "The camera handle returned by Init_Camera"}
                ],
                "returns": {"type": "None", "desc": "Clean Shutdown"},
                "usage": "Close_Camera(capture_camera = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Close_Camera",
                "source_func": "Close_Camera",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
        },
    },
    "Image Processing": {
        "color": "#10b981",  # Vibrant Mint (Distinct from Sky/Cyan)
        "icon": "🖼️",
        "functions": {
            "convert_to_gray": {
                "desc": "Convert a color image to grayscale",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "A color (BGR) image — e.g. from cv2.imread or a camera frame",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Single-channel grayscale image (H × W)",
                },
                "usage": "grayscale_image = convert_to_gray(input_image = None)",
                "import_statement": "from src.modules.library.functions.image_processing import convert_to_gray",
                "source_func": "convert_to_gray",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "resize_image": {
                "desc": "Resize an image to specific dimensions",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "Input image to process (or go to Workspace and choose an image file)",
                    },
                    {
                        "name": "width",
                        "type": "Number (int)",
                        "desc": "Target width in pixels",
                    },
                    {
                        "name": "height",
                        "type": "Number (int)",
                        "desc": "Target height in pixels",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Resized image with shape (height × width × channels)",
                },
                "usage": "resized_image = resize_image(input_image = None, width = '640', height = '480')",
                "import_statement": "from src.modules.library.functions.image_processing import resize_image",
                "source_func": "resize_image",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "apply_blur": {
                "desc": "Apply Gaussian blur to smooth an image",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "The source image to blur",
                    },
                    {
                        "name": "kernel_size",
                        "type": "Number (int)",
                        "desc": "Size of the blur kernel — must be odd (default: 5)",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Blurred image, same shape as input",
                },
                "usage": "blurred_image = apply_blur(input_image = None, kernel_size = '5')",
                "import_statement": "from src.modules.library.functions.image_processing import apply_blur",
                "source_func": "apply_blur",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "detect_edges": {
                "desc": "Detect edges in an image using the Canny algorithm",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "The source image (color or grayscale)",
                    },
                    {
                        "name": "threshold1",
                        "type": "Number (int)",
                        "desc": "Lower hysteresis threshold — controls weak edge sensitivity (default: 100)",
                    },
                    {
                        "name": "threshold2",
                        "type": "Number (int)",
                        "desc": "Upper hysteresis threshold — controls strong edge detection (default: 200)",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Binary edge map — white pixels are edges, black is background",
                },
                "usage": "edge_map = detect_edges(input_image = None, threshold1 = '100', threshold2 = '200')",
                "import_statement": "from src.modules.library.functions.image_processing import detect_edges",
                "source_func": "detect_edges",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "flip_image": {
                "desc": "Flip an image horizontally, vertically, or both",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "The source image to flip",
                    },
                    {
                        "name": "direction",
                        "type": "Text (str)",
                        "desc": "'horizontal' (left-right), 'vertical' (upside-down), or 'both' (default: 'horizontal')",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Flipped image, same shape as input",
                },
                "usage": "flipped_image = flip_image(input_image = None, direction = 'horizontal')",
                "import_statement": "from src.modules.library.functions.image_processing import flip_image",
                "source_func": "flip_image",
                "source_module": "src.modules.library.functions.image_processing",
            },
        },
    },
    "AI Vision Core": {
        "color": "#8b5cf6",  # Vibrant Violet (Contrast for light pink Brain icon)
        "icon": "🧠",
        "functions": {
            "Load_YuNet_Model": {
                "desc": "Initialize specialized YuNet model for real-time face detection",
                "params": [
                    {
                        "name": "model_path",
                        "type": "Text (str)",
                        "desc": "The file path (go to Workspace and choose your model/file)",
                    },
                ],
                "returns": {
                    "type": "AI Detector",
                    "desc": "A OpenCV FaceDetectorYN handle",
                },
                "usage": "ai_detector = Load_YuNet_Model(model_path = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Load_YuNet_Model",
                "source_func": "Load_YuNet_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Run_YuNet_Model": {
                "desc": "Auto-set input size for AI detector based on frame",
                "params": [
                    {
                        "name": "ai_detector",
                        "type": "AI Object",
                        "desc": "The YuNet or other OpenCV model",
                    },
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to analyze",
                    },
                ],
                "returns": {
                    "type": "None",
                    "desc": "Modifies detector in-place",
                },
                "usage": "Run_YuNet_Model(ai_detector = None, camera_frame = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Run_YuNet_Model",
                "source_func": "Run_YuNet_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Load_ONNX_Model": {
                "desc": "Load an ONNX AI model natively using Microsoft ONNX Runtime",
                "params": [
                    {
                        "name": "model_path",
                        "type": "Text (str)",
                        "desc": "Path to the .onnx model file",
                    },
                ],
                "returns": {
                    "type": "AI Session",
                    "desc": "An active ONNX runtime session object",
                },
                "usage": "model_session = Load_ONNX_Model(model_path = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Load_ONNX_Model",
                "source_func": "Load_ONNX_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Run_ONNX_Model": {
                "desc": "Process a frame through an AI model (auto-formatting)",
                "params": [
                    {
                        "name": "model_session",
                        "type": "AI Session",
                        "desc": "The active ONNX session loaded previously",
                    },
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to process",
                    },
                    {
                        "name": "img_size",
                        "type": "Number (int)",
                        "desc": "The expected square vision size, usually 640 or 320",
                    },
                ],
                "returns": {
                    "type": "Array",
                    "desc": "Raw output predictions from the AI",
                },
                "usage": "predictions = Run_ONNX_Model(model_session = None, camera_frame = None, img_size = '640')",
                "import_statement": "from src.modules.library.functions.ai_blocks import Run_ONNX_Model",
                "source_func": "Run_ONNX_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Load_Engine_Model": {
                "desc": "Load a high-speed TensorRT (.engine) model for Jetson",
                "params": [
                    {
                        "name": "model_path",
                        "type": "Text (str)",
                        "desc": "Path to the .engine model file",
                    },
                ],
                "returns": {
                    "type": "AI Model",
                    "desc": "An optimized YOLO engine object",
                },
                "usage": "engine_model = Load_Engine_Model(model_path = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Load_Engine_Model",
                "source_func": "Load_Engine_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Run_Engine_Model": {
                "desc": "Run ultra-fast inference using a TensorRT engine",
                "params": [
                    {
                        "name": "engine_model",
                        "type": "AI Model",
                        "desc": "The loaded .engine model object",
                    },
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to process",
                    },
                    {
                        "name": "img_size",
                        "type": "Number",
                        "desc": "Must match the training size: 320 or 640 only",
                        "default": 640,
                        "choices": [320, 640],
                    },
                ],
                "returns": {
                    "type": "Array",
                    "desc": "List of detections [x1, y1, x2, y2, conf, cls]",
                },
                "usage": "engine_results = Run_Engine_Model(engine_model = None, camera_frame = None, img_size = 640)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Run_Engine_Model",
                "source_func": "Run_Engine_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
        },
    },
    "Display & Dashboard": {
        "color": "#6366f1",  # Indigo 500
        "icon": "🎨",
        "functions": {
            "Draw_Detections": {
                "desc": "Draw boxes and labels on detected objects (faces, etc.)",
                "params": [
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to draw on",
                    },
                    {
                        "name": "results",
                        "type": "Array",
                        "desc": "The detection array from YuNet",
                    },
                    {
                        "name": "label",
                        "type": "Text (str)",
                        "desc": "Label text to display (default: 'Detected')",
                    },
                ],
                "returns": {
                    "type": "Number (int)",
                    "desc": "Count of objects detected",
                },
                "usage": "detect_count = Draw_Detections(camera_frame = None, results = None, label = 'Face')",
                "import_statement": "from src.modules.library.functions.ai_blocks import Draw_Detections",
                "source_func": "Draw_Detections",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Draw_Detections_MultiClass": {
                "desc": "Draw bounding boxes from raw ONNX multi-class output",
                "params": [
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to draw on",
                    },
                    {
                        "name": "outputs",
                        "type": "Array",
                        "desc": "Raw ONNX tensor output from inference",
                    },
                    {
                        "name": "classes",
                        "type": "List",
                        "desc": "List of string class names",
                    },
                    {
                        "name": "conf_threshold",
                        "type": "Number (float)",
                        "desc": "Minimum confidence required (default: 0.50)",
                    },
                ],
                "returns": {
                    "type": "Number (int)",
                    "desc": "Count of objects detected",
                },
                "usage": "total_objects = Draw_Detections_MultiClass(camera_frame = None, outputs = None, classes = None, conf_threshold = '0.50')",
                "import_statement": "from src.modules.library.functions.ai_blocks import Draw_Detections_MultiClass",
                "source_func": "Draw_Detections_MultiClass",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Draw_Engine_Detections": {
                "desc": "Draw bounding boxes from .engine model results",
                "params": [
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to draw on",
                    },
                    {
                        "name": "results",
                        "type": "Array",
                        "desc": "The detections list from Run_Engine_Model",
                    },
                    {
                        "name": "classes",
                        "type": "List",
                        "desc": "Optional list of class names (default: None)",
                    },
                    {
                        "name": "conf_threshold",
                        "type": "Number (float)",
                        "desc": "Minimum confidence to draw (default: 0.25)",
                    },
                ],
                "returns": {
                    "type": "Number (int)",
                    "desc": "Total count of objects detected",
                },
                "usage": "obj_count = Draw_Engine_Detections(camera_frame = None, results = None, classes = None, conf_threshold = 0.25)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Draw_Engine_Detections",
                "source_func": "Draw_Engine_Detections",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Update_Dashboard": {
                "desc": "Send image and results to the app UI in one block",
                "params": [
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The frame to stream to 'Live Feed'",
                    },
                    {
                        "name": "var_name",
                        "type": "Text (str)",
                        "desc": "Name of variable to track in Results panel",
                    },
                    {
                        "name": "var_value",
                        "type": "Any",
                        "desc": "Value to show in Results panel",
                    },
                ],
                "returns": {
                    "type": "None",
                    "desc": "Streams data to stdout via protocol",
                },
                "usage": "Update_Dashboard(camera_frame = None, var_name = 'Objects', var_value = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Update_Dashboard",
                "source_func": "Update_Dashboard",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
        },
    },

    "Logic Operations": {
        "color": "#06b6d4",  # Fun Cyan (Swapped from Robotics)
        "icon": "⚡",
        "functions": {
            "Loop_Forever": {
                "desc": "Create a 'while True' loop to keep your AI running continuously",
                "params": [],
                "returns": {"type": "Control Flow", "desc": "Infinite loop"},
                "usage": "while True:\n    # 🔵 Start Loop\n    # Add your code here \n    \n    # 🔴 End Loop",
                "import_statement": "",
                "source_func": None,
                "source_module": None,
            },
            "If_Condition": {
                "desc": "Run code only IF a certain condition is met (e.g., face detected)",
                "params": [
                    {"name": "condition", "type": "Check", "desc": "The test to perform (e.g. count > 0)"}
                ],
                "returns": {"type": "Control Flow", "desc": "Conditional path"},
                "usage": "if condition:\n    # 🟣 Start If\n    # Code runs if condition is met\n\n    # ⚪ End If",
                "import_statement": "",
                "source_func": None,
                "source_module": None,
            },
            "If_Else_Control": {
                "desc": "Branching logic: do one thing IF true, otherwise do something ELSE",
                "params": [
                    {"name": "condition", "type": "Check", "desc": "The test to perform"}
                ],
                "returns": {"type": "Control Flow", "desc": "Choice between two paths"},
                "usage": "if condition:\n    # Path 1 (True)\n\nelse:\n    # Path 2 (False)\n\n# --- End Logic ---",
                "import_statement": "",
                "source_func": None,
                "source_module": None,
            }
        }
    },
    "Robotics": {
        "color": "#f43f5e",  # Vibrant Rose (Swapped from Logic)
        "icon": "🤖",
        "functions": {
            "DC_Run": {
                "desc": "Run a DC or encoder motor at a given speed (with optional duration)",
                "params": [
                    {"name": "pin", "type": "Text (str)", "desc": "Motor port: 'M1', 'M2', 'M3', 'M4', 'E1', or 'E2'"},
                    {"name": "speed", "type": "Number (int)", "desc": "Power from -100 to 100 (positive = forward, negative = backward)"},
                    {"name": "time_ms", "type": "Number (int)", "desc": "Duration in milliseconds — leave blank to run forever"},
                ],
                "returns": {"type": "None", "desc": "Motor runs until time expires or DC_Stop is called"},
                "usage": "DC_Run(pin = 'M1', speed = 50, time_ms = None)",
                "import_statement": "from src.modules.library.functions.robotics import DC_Run",
                "source_func": "DC_Run",
                "source_module": "src.modules.library.functions.robotics",
            },
            "DC_Stop": {
                "desc": "Stop a specific motor or all motors at once",
                "params": [
                    {"name": "pin", "type": "Text (str)", "desc": "Motor port: 'M1'-'M4', 'E1'-'E2' — leave blank to stop ALL"},
                ],
                "returns": {"type": "None", "desc": "Motor(s) stop immediately"},
                "usage": "DC_Stop(pin = 'M1')",
                "import_statement": "from src.modules.library.functions.robotics import DC_Stop",
                "source_func": "DC_Stop",
                "source_module": "src.modules.library.functions.robotics",
            },
            "Get_Speed": {
                "desc": "Read encoder motor speed in RPM (E1 or E2 only)",
                "params": [
                    {"name": "pin", "type": "Text (str)", "desc": "Encoder port: 'E1' or 'E2'"},
                ],
                "returns": {"type": "Number (float)", "desc": "Current speed in RPM"},
                "usage": "rpm = Get_Speed(pin = 'E1')",
                "import_statement": "from src.modules.library.functions.robotics import Get_Speed",
                "source_func": "Get_Speed",
                "source_module": "src.modules.library.functions.robotics",
            },
            "Set_Servo": {
                "desc": "Rotate a servo motor to a specific angle",
                "params": [
                    {"name": "pin", "type": "Text (str)", "desc": "Servo port: 'S1', 'S2', 'S3', or 'S4'"},
                    {"name": "angle", "type": "Number (int)", "desc": "Target angle from 0 to 180 degrees"},
                ],
                "returns": {"type": "None", "desc": "Servo holds the target angle"},
                "usage": "Set_Servo(pin = 'S1', angle = 90)",
                "import_statement": "from src.modules.library.functions.robotics import Set_Servo",
                "source_func": "Set_Servo",
                "source_module": "src.modules.library.functions.robotics",
            },
        }
    },
    # "Array Operations": {
    #     "color": "#22c55e",  # Vibrant Green (Green 500)
    #     "functions": {
    #         "normalize_array": {
    #             "desc": "Scale array values to the 0–1 range using min-max normalization",
    #             "params": [
    #                 {
    #                     "name": "arr",
    #                     "type": "Array (ndarray)",
    #                     "desc": "Any NumPy array — 1-D, 2-D, or higher dimension",
    #                 },
    #             ],
    #             "returns": {
    #                 "type": "Array (ndarray)",
    #                 "desc": "float64 array with all values scaled between 0.0 and 1.0",
    #             },
    #             "usage": "normalized = normalize_array(arr)",
    #             "import_statement": "from src.modules.library.functions.array_operations import normalize_array",
    #             "source_func": "normalize_array",
    #             "source_module": "src.modules.library.functions.array_operations",
    #         },
    #         "create_image_matrix": {
    #             "desc": "Create a blank all-zero image matrix of a given size",
    #             "params": [
    #                 {
    #                     "name": "height",
    #                     "type": "Number (int)",
    #                     "desc": "Number of pixel rows",
    #                 },
    #                 {
    #                     "name": "width",
    #                     "type": "Number (int)",
    #                     "desc": "Number of pixel columns",
    #                 },
    #                 {
    #                     "name": "channels",
    #                     "type": "Number (int)",
    #                     "desc": "Color channels — 3 for BGR/RGB, 1 for grayscale (default: 3)",
    #                 },
    #             ],
    #             "returns": {
    #                 "type": "Array (ndarray)",
    #                 "desc": "Zero-filled uint8 array of shape (height × width × channels)",
    #             },
    #             "usage": "blank = create_image_matrix(height=480, width=640, channels=3)",
    #             "import_statement": "from src.modules.library.functions.array_operations import create_image_matrix",
    #             "source_func": "create_image_matrix",
    #             "source_module": "src.modules.library.functions.array_operations",
    #         },
    #         "flatten_array": {
    #             "desc": "Flatten a multi-dimensional array into a single 1-D array",
    #             "params": [
    #                 {
    #                     "name": "arr",
    #                     "type": "Array (ndarray)",
    #                     "desc": "Any NumPy array of arbitrary shape, e.g. an image (H × W × C)",
    #                 },
    #             ],
    #             "returns": {
    #                 "type": "Array (ndarray)",
    #                 "desc": "1-D array with all elements in row-major (C) order",
    #             },
    #             "usage": "flat = flatten_array(arr)",
    #             "import_statement": "from src.modules.library.functions.array_operations import flatten_array",
    #             "source_func": "flatten_array",
    #             "source_module": "src.modules.library.functions.array_operations",
    #         },
    #         "reshape_array": {
    #             "desc": "Reshape an array to new dimensions without changing its data",
    #             "params": [
    #                 {
    #                     "name": "arr",
    #                     "type": "Array (ndarray)",
    #                     "desc": "Source array to reshape",
    #                 },
    #                 {
    #                     "name": "new_shape",
    #                     "type": "Tuple (int, ...)",
    #                     "desc": "Target shape, e.g. (3, 4) or (-1, 784). Use -1 to auto-infer one dimension",
    #                 },
    #             ],
    #             "returns": {
    #                 "type": "Array (ndarray)",
    #                 "desc": "Array reshaped to new_shape — same total number of elements",
    #             },
    #             "usage": "reshaped = reshape_array(arr, new_shape=(28, 28))",
    #             "import_statement": "from src.modules.library.functions.array_operations import reshape_array",
    #             "source_func": "reshape_array",
    #             "source_module": "src.modules.library.functions.array_operations",
    #         },
    #         "compute_statistics": {
    #             "desc": "Compute descriptive statistics (mean, std, min, max, median) for a numeric array",
    #             "params": [
    #                 {
    #                     "name": "arr",
    #                     "type": "Array (ndarray)",
    #                     "desc": "Input numeric array of any shape",
    #                 },
    #             ],
    #             "returns": {
    #                 "type": "Dict",
    #                 "desc": "Dictionary with keys: mean, std, min, max, median, shape",
    #             },
    #             "usage": "stats = compute_statistics(arr)",
    #             "import_statement": "from src.modules.library.functions.array_operations import compute_statistics",
    #             "source_func": "compute_statistics",
    #             "source_module": "src.modules.library.functions.array_operations",
    #         },
    #         "one_hot_encode": {
    #             "desc": "One-hot encode an integer label array into a 2-D binary matrix",
    #             "params": [
    #                 {
    #                     "name": "labels",
    #                     "type": "Array (int)",
    #                     "desc": "1-D array of class indices, e.g. [0, 2, 1, 0]",
    #                 },
    #                 {
    #                     "name": "num_classes",
    #                     "type": "Number (int)",
    #                     "desc": "Total number of classes. If None, inferred as max(labels) + 1",
    #                 },
    #             ],
    #             "returns": {
    #                 "type": "Array (ndarray)",
    #                 "desc": "float32 matrix of shape (N × num_classes) — each row has a single 1.0",
    #             },
    #             "usage": "encoded = one_hot_encode(labels, num_classes=10)",
    #             "import_statement": "from src.modules.library.functions.array_operations import one_hot_encode",
    #             "source_func": "one_hot_encode",
    #             "source_module": "src.modules.library.functions.array_operations",
    #         },
    #     },
    # },


}