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
                "desc_vi": "Khởi tạo camera mặc định (ID: 0)",
                "params": [],
                "returns": {
                    "type": "Capture Object",
                    "desc": "A handle to the active camera device",
                    "desc_vi": "Đối tượng kết nối với camera đang hoạt động",
                },
                "usage": "capture_camera = Init_Camera()",
                "import_statement": "from src.modules.library.functions.ai_blocks import Init_Camera",
                "source_func": "Init_Camera",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Get_Camera_Frame": {
                "desc": "Capture the current live frame from the initialized camera",
                "desc_vi": "Chụp khung hình hiện tại từ camera đã khởi tạo",
                "params": [
                    {
                        "name": "capture_camera",
                        "type": "Capture Object",
                        "desc": "The camera handle returned by Init_Camera",
                        "desc_vi": "Đối tượng camera được trả về từ Init_Camera",
                    },
                ],
                "returns": {
                    "type": "Image",
                    "desc": "The live picture (frame) to analyze",
                    "desc_vi": "Hình ảnh trực tiếp (khung hình) để phân tích",
                },
                "usage": "camera_frame = Get_Camera_Frame(capture_camera = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Get_Camera_Frame",
                "source_func": "Get_Camera_Frame",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Close_Camera": {
                "desc": "Safely shut down the camera driver and close all windows",
                "desc_vi": "Tắt camera an toàn và đóng tất cả cửa sổ",
                "params": [
                     {"name": "capture_camera", "type": "Capture Object", "desc": "The camera handle returned by Init_Camera", "desc_vi": "Đối tượng camera được trả về từ Init_Camera"}
                ],
                "returns": {"type": "None", "desc": "Clean Shutdown", "desc_vi": "Tắt máy sạch sẽ"},
                "usage": "Close_Camera(capture_camera = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Close_Camera",
                "source_func": "Close_Camera",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Save_Frame": {
                "desc": "Save a camera frame to disk as an image file",
                "desc_vi": "Lưu khung hình từ camera thành tệp ảnh",
                "params": [
                    {"name": "camera_frame", "type": "Image", "desc": "The frame to save", "desc_vi": "Khung hình cần lưu"},
                    {"name": "file_path", "type": "Text (str)", "desc": "File path to save the image (e.g., 'snapshot.jpg')", "desc_vi": "Đường dẫn tệp để lưu ảnh (ví dụ: 'snapshot.jpg')"},
                ],
                "returns": {"type": "None", "desc": "Saves image to disk", "desc_vi": "Lưu ảnh vào ổ đĩa"},
                "usage": "Save_Frame(camera_frame = None, file_path = 'snapshot.jpg')",
                "import_statement": "from src.modules.library.functions.ai_blocks import Save_Frame",
                "source_func": "Save_Frame",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Load_Image": {
                "desc": "Load an image from a file on disk",
                "desc_vi": "Tải ảnh từ tệp trên ổ đĩa",
                "params": [
                    {"name": "file_path", "type": "Text (str)", "desc": "File path to the image (go to Workspace and choose a file)", "desc_vi": "Đường dẫn đến tệp ảnh (vào Workspace và chọn tệp)"},
                ],
                "returns": {"type": "Image (ndarray)", "desc": "The loaded image, or None if file not found", "desc_vi": "Ảnh đã tải, hoặc None nếu không tìm thấy tệp"},
                "usage": "loaded_image = Load_Image(file_path = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Load_Image",
                "source_func": "Load_Image",
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
                "desc_vi": "Chuyển ảnh màu sang ảnh xám",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "A color (BGR) image — e.g. from cv2.imread or a camera frame",
                        "desc_vi": "Ảnh màu (BGR) — ví dụ từ cv2.imread hoặc khung hình camera",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Single-channel grayscale image (H × W)",
                    "desc_vi": "Ảnh xám một kênh (H × W)",
                },
                "usage": "grayscale_image = convert_to_gray(input_image = None)",
                "import_statement": "from src.modules.library.functions.image_processing import convert_to_gray",
                "source_func": "convert_to_gray",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "resize_image": {
                "desc": "Resize an image to specific dimensions",
                "desc_vi": "Thay đổi kích thước ảnh theo chiều rộng và chiều cao",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "Input image to process (or go to Workspace and choose an image file)",
                        "desc_vi": "Ảnh đầu vào cần xử lý (hoặc vào Workspace và chọn tệp ảnh)",
                    },
                    {
                        "name": "width",
                        "type": "Number (int)",
                        "desc": "Target width in pixels",
                        "desc_vi": "Chiều rộng mong muốn (pixel)",
                    },
                    {
                        "name": "height",
                        "type": "Number (int)",
                        "desc": "Target height in pixels",
                        "desc_vi": "Chiều cao mong muốn (pixel)",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Resized image with shape (height × width × channels)",
                    "desc_vi": "Ảnh đã thay đổi kích thước (chiều cao × chiều rộng × kênh màu)",
                },
                "usage": "resized_image = resize_image(input_image = None, width = '640', height = '480')",
                "import_statement": "from src.modules.library.functions.image_processing import resize_image",
                "source_func": "resize_image",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "apply_blur": {
                "desc": "Apply Gaussian blur to smooth an image",
                "desc_vi": "Làm mờ ảnh bằng bộ lọc Gaussian",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "The source image to blur",
                        "desc_vi": "Ảnh gốc cần làm mờ",
                    },
                    {
                        "name": "kernel_size",
                        "type": "Number (int)",
                        "desc": "Size of the blur kernel — must be odd (default: 5)",
                        "desc_vi": "Kích thước bộ lọc — phải là số lẻ (mặc định: 5)",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Blurred image, same shape as input",
                    "desc_vi": "Ảnh đã làm mờ, cùng kích thước với ảnh gốc",
                },
                "usage": "blurred_image = apply_blur(input_image = None, kernel_size = '5')",
                "import_statement": "from src.modules.library.functions.image_processing import apply_blur",
                "source_func": "apply_blur",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "detect_edges": {
                "desc": "Detect edges in an image using the Canny algorithm",
                "desc_vi": "Phát hiện cạnh trong ảnh bằng thuật toán Canny",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "The source image (color or grayscale)",
                        "desc_vi": "Ảnh gốc (màu hoặc xám)",
                    },
                    {
                        "name": "threshold1",
                        "type": "Number (int)",
                        "desc": "Lower hysteresis threshold — controls weak edge sensitivity (default: 100)",
                        "desc_vi": "Ngưỡng dưới — điều chỉnh độ nhạy cạnh yếu (mặc định: 100)",
                    },
                    {
                        "name": "threshold2",
                        "type": "Number (int)",
                        "desc": "Upper hysteresis threshold — controls strong edge detection (default: 200)",
                        "desc_vi": "Ngưỡng trên — điều chỉnh phát hiện cạnh mạnh (mặc định: 200)",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Binary edge map — white pixels are edges, black is background",
                    "desc_vi": "Bản đồ cạnh — điểm trắng là cạnh, đen là nền",
                },
                "usage": "edge_map = detect_edges(input_image = None, threshold1 = '100', threshold2 = '200')",
                "import_statement": "from src.modules.library.functions.image_processing import detect_edges",
                "source_func": "detect_edges",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "flip_image": {
                "desc": "Flip an image horizontally, vertically, or both",
                "desc_vi": "Lật ảnh theo chiều ngang, dọc hoặc cả hai",
                "params": [
                    {
                        "name": "input_image",
                        "type": "Image (ndarray)",
                        "desc": "The source image to flip",
                        "desc_vi": "Ảnh gốc cần lật",
                    },
                    {
                        "name": "direction",
                        "type": "Text (str)",
                        "desc": "'horizontal' (left-right), 'vertical' (upside-down), or 'both' (default: 'horizontal')",
                        "desc_vi": "'horizontal' (trái-phải), 'vertical' (lộn ngược), hoặc 'both' (mặc định: 'horizontal')",
                    },
                ],
                "returns": {
                    "type": "Image (ndarray)",
                    "desc": "Flipped image, same shape as input",
                    "desc_vi": "Ảnh đã lật, cùng kích thước với ảnh gốc",
                },
                "usage": "flipped_image = flip_image(input_image = None, direction = 'horizontal')",
                "import_statement": "from src.modules.library.functions.image_processing import flip_image",
                "source_func": "flip_image",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "adjust_brightness": {
                "desc": "Adjust image brightness by a factor (>1 brighter, <1 darker)",
                "desc_vi": "Điều chỉnh độ sáng ảnh (>1 sáng hơn, <1 tối hơn)",
                "params": [
                    {"name": "input_image", "type": "Image (ndarray)", "desc": "The source image to adjust", "desc_vi": "Ảnh gốc cần điều chỉnh"},
                    {"name": "factor", "type": "Number (float)", "desc": "Brightness multiplier (default: 1.5)", "desc_vi": "Hệ số nhân độ sáng (mặc định: 1.5)"},
                ],
                "returns": {"type": "Image (ndarray)", "desc": "Brightness-adjusted image", "desc_vi": "Ảnh đã điều chỉnh độ sáng"},
                "usage": "bright_image = adjust_brightness(input_image = None, factor = '1.5')",
                "import_statement": "from src.modules.library.functions.image_processing import adjust_brightness",
                "source_func": "adjust_brightness",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "rotate_image": {
                "desc": "Rotate an image by a specified angle without cropping",
                "desc_vi": "Xoay ảnh theo góc chỉ định mà không bị cắt",
                "params": [
                    {"name": "input_image", "type": "Image (ndarray)", "desc": "The source image to rotate", "desc_vi": "Ảnh gốc cần xoay"},
                    {"name": "angle", "type": "Number (int)", "desc": "Rotation angle in degrees (default: 90)", "desc_vi": "Góc xoay tính bằng độ (mặc định: 90)"},
                ],
                "returns": {"type": "Image (ndarray)", "desc": "Rotated image with expanded canvas", "desc_vi": "Ảnh đã xoay với khung mở rộng"},
                "usage": "rotated = rotate_image(input_image = None, angle = '90')",
                "import_statement": "from src.modules.library.functions.image_processing import rotate_image",
                "source_func": "rotate_image",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "crop_image": {
                "desc": "Crop a rectangular region from an image",
                "desc_vi": "Cắt một vùng hình chữ nhật từ ảnh",
                "params": [
                    {"name": "input_image", "type": "Image (ndarray)", "desc": "The source image to crop", "desc_vi": "Ảnh gốc cần cắt"},
                    {"name": "x", "type": "Number (int)", "desc": "Left edge of crop region in pixels", "desc_vi": "Cạnh trái vùng cắt (pixel)"},
                    {"name": "y", "type": "Number (int)", "desc": "Top edge of crop region in pixels", "desc_vi": "Cạnh trên vùng cắt (pixel)"},
                    {"name": "width", "type": "Number (int)", "desc": "Width of crop region in pixels", "desc_vi": "Chiều rộng vùng cắt (pixel)"},
                    {"name": "height", "type": "Number (int)", "desc": "Height of crop region in pixels", "desc_vi": "Chiều cao vùng cắt (pixel)"},
                ],
                "returns": {"type": "Image (ndarray)", "desc": "Cropped image region", "desc_vi": "Vùng ảnh đã cắt"},
                "usage": "cropped = crop_image(input_image = None, x = '0', y = '0', width = '100', height = '100')",
                "import_statement": "from src.modules.library.functions.image_processing import crop_image",
                "source_func": "crop_image",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "draw_text": {
                "desc": "Draw text on an image at a specified position",
                "desc_vi": "Vẽ chữ lên ảnh tại vị trí chỉ định",
                "params": [
                    {"name": "input_image", "type": "Image (ndarray)", "desc": "The source image to draw on", "desc_vi": "Ảnh gốc để vẽ lên"},
                    {"name": "text", "type": "Text (str)", "desc": "The text to overlay", "desc_vi": "Chữ cần hiển thị"},
                    {"name": "x", "type": "Number (int)", "desc": "Horizontal position in pixels (default: 10)", "desc_vi": "Vị trí ngang tính bằng pixel (mặc định: 10)"},
                    {"name": "y", "type": "Number (int)", "desc": "Vertical position in pixels (default: 30)", "desc_vi": "Vị trí dọc tính bằng pixel (mặc định: 30)"},
                ],
                "returns": {"type": "Image (ndarray)", "desc": "Image with text overlay", "desc_vi": "Ảnh có chữ hiển thị"},
                "usage": "labeled = draw_text(input_image = None, text = 'Hello', x = '10', y = '30')",
                "import_statement": "from src.modules.library.functions.image_processing import draw_text",
                "source_func": "draw_text",
                "source_module": "src.modules.library.functions.image_processing",
            },
            "convert_to_hsv": {
                "desc": "Convert a BGR color image to HSV color space",
                "desc_vi": "Chuyển ảnh màu BGR sang không gian màu HSV",
                "params": [
                    {"name": "input_image", "type": "Image (ndarray)", "desc": "A color (BGR) image", "desc_vi": "Ảnh màu (BGR)"},
                ],
                "returns": {"type": "Image (ndarray)", "desc": "HSV image (Hue, Saturation, Value)", "desc_vi": "Ảnh HSV (Sắc độ, Độ bão hòa, Giá trị)"},
                "usage": "hsv_image = convert_to_hsv(input_image = None)",
                "import_statement": "from src.modules.library.functions.image_processing import convert_to_hsv",
                "source_func": "convert_to_hsv",
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
                "desc_vi": "Khởi tạo mô hình YuNet chuyên dụng để phát hiện khuôn mặt",
                "params": [
                    {
                        "name": "model_path",
                        "type": "Text (str)",
                        "desc": "The file path (go to Workspace and choose your model/file)",
                        "desc_vi": "Đường dẫn tệp (vào Workspace và chọn mô hình/tệp)",
                    },
                ],
                "returns": {
                    "type": "AI Detector",
                    "desc": "A OpenCV FaceDetectorYN handle",
                    "desc_vi": "Đối tượng phát hiện khuôn mặt OpenCV FaceDetectorYN",
                },
                "usage": "ai_detector = Load_YuNet_Model(model_path = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Load_YuNet_Model",
                "source_func": "Load_YuNet_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Run_YuNet_Model": {
                "desc": "Auto-set input size for AI detector based on frame",
                "desc_vi": "Tự động thiết lập kích thước đầu vào cho AI dựa trên khung hình",
                "params": [
                    {
                        "name": "ai_detector",
                        "type": "AI Object",
                        "desc": "The YuNet or other OpenCV model",
                        "desc_vi": "Mô hình YuNet hoặc OpenCV khác",
                    },
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to analyze",
                        "desc_vi": "Khung hình camera cần phân tích",
                    },
                ],
                "returns": {
                    "type": "None",
                    "desc": "Modifies detector in-place",
                    "desc_vi": "Cập nhật trực tiếp bộ phát hiện",
                },
                "usage": "Run_YuNet_Model(ai_detector = None, camera_frame = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Run_YuNet_Model",
                "source_func": "Run_YuNet_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Load_ONNX_Model": {
                "desc": "Load an ONNX AI model natively using Microsoft ONNX Runtime",
                "desc_vi": "Tải mô hình AI ONNX bằng Microsoft ONNX Runtime",
                "params": [
                    {
                        "name": "model_path",
                        "type": "Text (str)",
                        "desc": "Path to the .onnx model file",
                        "desc_vi": "Đường dẫn đến tệp mô hình .onnx",
                    },
                ],
                "returns": {
                    "type": "AI Session",
                    "desc": "An active ONNX runtime session object",
                    "desc_vi": "Phiên ONNX runtime đang hoạt động",
                },
                "usage": "model_session = Load_ONNX_Model(model_path = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Load_ONNX_Model",
                "source_func": "Load_ONNX_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Run_ONNX_Model": {
                "desc": "Process a frame through an AI model (auto-formatting)",
                "desc_vi": "Xử lý khung hình qua mô hình AI (tự động định dạng)",
                "params": [
                    {
                        "name": "model_session",
                        "type": "AI Session",
                        "desc": "The active ONNX session loaded previously",
                        "desc_vi": "Phiên ONNX đã tải trước đó",
                    },
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to process",
                        "desc_vi": "Khung hình camera cần xử lý",
                    },
                    {
                        "name": "img_size",
                        "type": "Number (int)",
                        "desc": "The expected square vision size, usually 640 or 320",
                        "desc_vi": "Kích thước ảnh vuông, thường là 640 hoặc 320",
                    },
                ],
                "returns": {
                    "type": "Array",
                    "desc": "Raw output predictions from the AI",
                    "desc_vi": "Kết quả dự đoán thô từ AI",
                },
                "usage": "predictions = Run_ONNX_Model(model_session = None, camera_frame = None, img_size = '640')",
                "import_statement": "from src.modules.library.functions.ai_blocks import Run_ONNX_Model",
                "source_func": "Run_ONNX_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Load_Engine_Model": {
                "desc": "Load a high-speed TensorRT (.engine) model for Jetson",
                "desc_vi": "Tải mô hình TensorRT (.engine) tốc độ cao cho Jetson",
                "params": [
                    {
                        "name": "model_path",
                        "type": "Text (str)",
                        "desc": "Path to the .engine model file",
                        "desc_vi": "Đường dẫn đến tệp mô hình .engine",
                    },
                ],
                "returns": {
                    "type": "AI Model",
                    "desc": "An optimized YOLO engine object",
                    "desc_vi": "Đối tượng YOLO engine đã tối ưu",
                },
                "usage": "engine_model = Load_Engine_Model(model_path = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Load_Engine_Model",
                "source_func": "Load_Engine_Model",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Run_Engine_Model": {
                "desc": "Run ultra-fast inference using a TensorRT engine",
                "desc_vi": "Chạy suy luận siêu nhanh bằng TensorRT engine",
                "params": [
                    {
                        "name": "engine_model",
                        "type": "AI Model",
                        "desc": "The loaded .engine model object",
                        "desc_vi": "Đối tượng mô hình .engine đã tải",
                    },
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to process",
                        "desc_vi": "Khung hình camera cần xử lý",
                    },
                    {
                        "name": "img_size",
                        "type": "Number",
                        "desc": "Must match the training size: 320 or 640 only",
                        "desc_vi": "Phải khớp kích thước huấn luyện: chỉ 320 hoặc 640",
                        "default": 640,
                        "choices": [320, 640],
                    },
                ],
                "returns": {
                    "type": "Array",
                    "desc": "List of detections [x1, y1, x2, y2, conf, cls]",
                    "desc_vi": "Danh sách phát hiện [x1, y1, x2, y2, độ tin cậy, lớp]",
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
                "desc_vi": "Vẽ khung và nhãn lên các đối tượng phát hiện được (khuôn mặt, v.v.)",
                "params": [
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to draw on",
                        "desc_vi": "Khung hình camera để vẽ lên",
                    },
                    {
                        "name": "results",
                        "type": "Array",
                        "desc": "The detection array from YuNet",
                        "desc_vi": "Mảng kết quả phát hiện từ YuNet",
                    },
                    {
                        "name": "label",
                        "type": "Text (str)",
                        "desc": "Label text to display (default: 'Detected')",
                        "desc_vi": "Nhãn hiển thị (mặc định: 'Detected')",
                    },
                ],
                "returns": {
                    "type": "Number (int)",
                    "desc": "Count of objects detected",
                    "desc_vi": "Số lượng đối tượng phát hiện được",
                },
                "usage": "detect_count = Draw_Detections(camera_frame = None, results = None, label = 'Face')",
                "import_statement": "from src.modules.library.functions.ai_blocks import Draw_Detections",
                "source_func": "Draw_Detections",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Draw_Detections_MultiClass": {
                "desc": "Draw bounding boxes from raw ONNX multi-class output",
                "desc_vi": "Vẽ khung bao từ kết quả ONNX đa lớp",
                "params": [
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to draw on",
                        "desc_vi": "Khung hình camera để vẽ lên",
                    },
                    {
                        "name": "outputs",
                        "type": "Array",
                        "desc": "Raw ONNX tensor output from inference",
                        "desc_vi": "Kết quả tensor ONNX thô từ suy luận",
                    },
                    {
                        "name": "classes",
                        "type": "List",
                        "desc": "List of string class names",
                        "desc_vi": "Danh sách tên các lớp đối tượng",
                    },
                    {
                        "name": "conf_threshold",
                        "type": "Number (float)",
                        "desc": "Minimum confidence required (default: 0.50)",
                        "desc_vi": "Độ tin cậy tối thiểu (mặc định: 0.50)",
                    },
                ],
                "returns": {
                    "type": "Number (int)",
                    "desc": "Count of objects detected",
                    "desc_vi": "Số lượng đối tượng phát hiện được",
                },
                "usage": "total_objects = Draw_Detections_MultiClass(camera_frame = None, outputs = None, classes = None, conf_threshold = '0.50')",
                "import_statement": "from src.modules.library.functions.ai_blocks import Draw_Detections_MultiClass",
                "source_func": "Draw_Detections_MultiClass",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Draw_Engine_Detections": {
                "desc": "Draw bounding boxes from .engine model results",
                "desc_vi": "Vẽ khung bao từ kết quả mô hình .engine",
                "params": [
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The camera frame to draw on",
                        "desc_vi": "Khung hình camera để vẽ lên",
                    },
                    {
                        "name": "results",
                        "type": "Array",
                        "desc": "The detections list from Run_Engine_Model",
                        "desc_vi": "Danh sách phát hiện từ Run_Engine_Model",
                    },
                    {
                        "name": "classes",
                        "type": "List",
                        "desc": "Optional list of class names (default: None)",
                        "desc_vi": "Danh sách tên lớp tùy chọn (mặc định: None)",
                    },
                    {
                        "name": "conf_threshold",
                        "type": "Number (float)",
                        "desc": "Minimum confidence to draw (default: 0.25)",
                        "desc_vi": "Độ tin cậy tối thiểu để vẽ (mặc định: 0.25)",
                    },
                ],
                "returns": {
                    "type": "Number (int)",
                    "desc": "Total count of objects detected",
                    "desc_vi": "Tổng số đối tượng phát hiện được",
                },
                "usage": "obj_count = Draw_Engine_Detections(camera_frame = None, results = None, classes = None, conf_threshold = 0.25)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Draw_Engine_Detections",
                "source_func": "Draw_Engine_Detections",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Update_Dashboard": {
                "desc": "Send image and results to the app UI in one block",
                "desc_vi": "Gửi ảnh và kết quả đến giao diện ứng dụng cùng lúc",
                "params": [
                    {
                        "name": "camera_frame",
                        "type": "Image",
                        "desc": "The frame to stream to 'Live Feed'",
                        "desc_vi": "Khung hình để truyền đến 'Live Feed'",
                    },
                    {
                        "name": "var_name",
                        "type": "Text (str)",
                        "desc": "Name of variable to track in Results panel",
                        "desc_vi": "Tên biến để theo dõi trong bảng Kết quả",
                    },
                    {
                        "name": "var_value",
                        "type": "Any",
                        "desc": "Value to show in Results panel",
                        "desc_vi": "Giá trị hiển thị trong bảng Kết quả",
                    },
                ],
                "returns": {
                    "type": "None",
                    "desc": "Streams data to stdout via protocol",
                    "desc_vi": "Truyền dữ liệu qua giao thức stdout",
                },
                "usage": "Update_Dashboard(camera_frame = None, var_name = 'Objects', var_value = None)",
                "import_statement": "from src.modules.library.functions.ai_blocks import Update_Dashboard",
                "source_func": "Update_Dashboard",
                "source_module": "src.modules.library.functions.ai_blocks",
            },
            "Show_FPS": {
                "desc": "Calculate and overlay FPS counter on the frame",
                "desc_vi": "Tính và hiển thị bộ đếm FPS lên khung hình",
                "params": [
                    {"name": "camera_frame", "type": "Image", "desc": "The frame to annotate with FPS", "desc_vi": "Khung hình để ghi chú FPS"},
                ],
                "returns": {"type": "Image (ndarray)", "desc": "Frame with FPS overlay", "desc_vi": "Khung hình có hiển thị FPS"},
                "usage": "fps_frame = Show_FPS(camera_frame = None)",
                "import_statement": "from src.modules.library.functions.display_blocks import Show_FPS",
                "source_func": "Show_FPS",
                "source_module": "src.modules.library.functions.display_blocks",
            },
            "Show_Image": {
                "desc": "Stream a camera frame to the Live Feed panel",
                "desc_vi": "Truyền khung hình camera đến bảng Live Feed",
                "params": [
                    {"name": "camera_frame", "type": "Image", "desc": "The frame to stream to 'Live Feed'", "desc_vi": "Khung hình để truyền đến 'Live Feed'"},
                ],
                "returns": {"type": "None", "desc": "Streams image to stdout via IMG protocol", "desc_vi": "Truyền ảnh qua giao thức IMG"},
                "usage": "Show_Image(camera_frame = None)",
                "import_statement": "from src.modules.library.functions.display_blocks import Show_Image",
                "source_func": "Show_Image",
                "source_module": "src.modules.library.functions.display_blocks",
            },
            "Observe_Variable": {
                "desc": "Display a variable's value in the Results panel",
                "desc_vi": "Hiển thị giá trị biến trong bảng Kết quả",
                "params": [
                    {"name": "var_name", "type": "Text (str)", "desc": "Name of variable to track in Results panel", "desc_vi": "Tên biến để theo dõi trong bảng Kết quả"},
                    {"name": "var_value", "type": "Any", "desc": "Value to show in Results panel", "desc_vi": "Giá trị hiển thị trong bảng Kết quả"},
                ],
                "returns": {"type": "None", "desc": "Streams variable to stdout via VAR protocol", "desc_vi": "Truyền biến qua giao thức VAR"},
                "usage": "Observe_Variable(var_name = 'Result', var_value = None)",
                "import_statement": "from src.modules.library.functions.display_blocks import Observe_Variable",
                "source_func": "Observe_Variable",
                "source_module": "src.modules.library.functions.display_blocks",
            },
            "Draw_Rectangle": {
                "desc": "Draw a colored rectangle on the frame",
                "desc_vi": "Vẽ hình chữ nhật có màu lên khung hình",
                "params": [
                    {"name": "camera_frame", "type": "Image", "desc": "The frame to draw on", "desc_vi": "Khung hình để vẽ lên"},
                    {"name": "x", "type": "Number (int)", "desc": "Left edge in pixels", "desc_vi": "Cạnh trái (pixel)"},
                    {"name": "y", "type": "Number (int)", "desc": "Top edge in pixels", "desc_vi": "Cạnh trên (pixel)"},
                    {"name": "width", "type": "Number (int)", "desc": "Width in pixels", "desc_vi": "Chiều rộng (pixel)"},
                    {"name": "height", "type": "Number (int)", "desc": "Height in pixels", "desc_vi": "Chiều cao (pixel)"},
                    {"name": "color", "type": "Text (str)", "desc": "Color name: green, red, blue, yellow, white", "desc_vi": "Tên màu: green, red, blue, yellow, white"},
                ],
                "returns": {"type": "Image (ndarray)", "desc": "Frame with rectangle drawn", "desc_vi": "Khung hình có hình chữ nhật"},
                "usage": "framed = Draw_Rectangle(camera_frame = None, x = '10', y = '10', width = '100', height = '100', color = 'green')",
                "import_statement": "from src.modules.library.functions.display_blocks import Draw_Rectangle",
                "source_func": "Draw_Rectangle",
                "source_module": "src.modules.library.functions.display_blocks",
            },
            "Draw_Circle": {
                "desc": "Draw a colored circle on the frame",
                "desc_vi": "Vẽ hình tròn có màu lên khung hình",
                "params": [
                    {"name": "camera_frame", "type": "Image", "desc": "The frame to draw on", "desc_vi": "Khung hình để vẽ lên"},
                    {"name": "center_x", "type": "Number (int)", "desc": "Center X coordinate in pixels", "desc_vi": "Tọa độ X tâm (pixel)"},
                    {"name": "center_y", "type": "Number (int)", "desc": "Center Y coordinate in pixels", "desc_vi": "Tọa độ Y tâm (pixel)"},
                    {"name": "radius", "type": "Number (int)", "desc": "Circle radius in pixels", "desc_vi": "Bán kính hình tròn (pixel)"},
                    {"name": "color", "type": "Text (str)", "desc": "Color name: green, red, blue, yellow, white", "desc_vi": "Tên màu: green, red, blue, yellow, white"},
                ],
                "returns": {"type": "Image (ndarray)", "desc": "Frame with circle drawn", "desc_vi": "Khung hình có hình tròn"},
                "usage": "circled = Draw_Circle(camera_frame = None, center_x = '100', center_y = '100', radius = '50', color = 'red')",
                "import_statement": "from src.modules.library.functions.display_blocks import Draw_Circle",
                "source_func": "Draw_Circle",
                "source_module": "src.modules.library.functions.display_blocks",
            },
        },
    },

    "Logic Operations": {
        "color": "#06b6d4",  # Fun Cyan (Swapped from Robotics)
        "icon": "⚡",
        "functions": {
            "Loop_Forever": {
                "desc": "Create a 'while True' loop to keep your AI running continuously",
                "desc_vi": "Tạo vòng lặp 'while True' để AI chạy liên tục",
                "params": [],
                "returns": {"type": "Control Flow", "desc": "Infinite loop", "desc_vi": "Vòng lặp vô hạn"},
                "usage": "while True:\n    # 🔵 Start Loop\n    # Add your code here \n    \n    # 🔴 End Loop",
                "import_statement": "",
                "source_func": None,
                "source_module": None,
            },
            "If_Condition": {
                "desc": "Run code only IF a certain condition is met (e.g., face detected)",
                "desc_vi": "Chạy mã chỉ KHI điều kiện được thỏa mãn (ví dụ: phát hiện khuôn mặt)",
                "params": [
                    {"name": "condition", "type": "Check", "desc": "The test to perform (e.g. count > 0)", "desc_vi": "Điều kiện kiểm tra (ví dụ: count > 0)"}
                ],
                "returns": {"type": "Control Flow", "desc": "Conditional path", "desc_vi": "Nhánh có điều kiện"},
                "usage": "if condition:\n    # 🟣 Start If\n    # Code runs if condition is met\n\n    # ⚪ End If",
                "import_statement": "",
                "source_func": None,
                "source_module": None,
            },
            "If_Else_Control": {
                "desc": "Branching logic: do one thing IF true, otherwise do something ELSE",
                "desc_vi": "Logic rẽ nhánh: làm một việc NẾU đúng, ngược lại làm việc KHÁC",
                "params": [
                    {"name": "condition", "type": "Check", "desc": "The test to perform", "desc_vi": "Điều kiện kiểm tra"}
                ],
                "returns": {"type": "Control Flow", "desc": "Choice between two paths", "desc_vi": "Lựa chọn giữa hai nhánh"},
                "usage": "if condition:\n    # Path 1 (True)\n\nelse:\n    # Path 2 (False)\n\n# --- End Logic ---",
                "import_statement": "",
                "source_func": None,
                "source_module": None,
            },
            "Wait_Seconds": {
                "desc": "Pause execution for a specified number of seconds",
                "desc_vi": "Tạm dừng chương trình trong số giây chỉ định",
                "params": [
                    {"name": "seconds", "type": "Number (float)", "desc": "Number of seconds to wait (default: 1.0)", "desc_vi": "Số giây chờ (mặc định: 1.0)"},
                ],
                "returns": {"type": "None", "desc": "Pauses execution", "desc_vi": "Tạm dừng chương trình"},
                "usage": "Wait_Seconds(seconds = '1.0')",
                "import_statement": "from src.modules.library.functions.logic_blocks import Wait_Seconds",
                "source_func": "Wait_Seconds",
                "source_module": "src.modules.library.functions.logic_blocks",
            },
            "Repeat_N_Times": {
                "desc": "Create a for-loop that runs a fixed number of times",
                "desc_vi": "Tạo vòng lặp chạy một số lần cố định",
                "params": [
                    {"name": "count", "type": "Number (int)", "desc": "Number of times to repeat (default: 5)", "desc_vi": "Số lần lặp lại (mặc định: 5)"},
                ],
                "returns": {"type": "Control Flow", "desc": "Counted loop", "desc_vi": "Vòng lặp đếm"},
                "usage": "for i in range(5):\n    # 🔵 Start Repeat\n    # Add your code here\n    \n    # 🔴 End Repeat",
                "import_statement": "",
                "source_func": None,
                "source_module": None,
            },
            "Print_Message": {
                "desc": "Print a message to the console output",
                "desc_vi": "In thông báo ra cửa sổ console",
                "params": [
                    {"name": "message", "type": "Text (str)", "desc": "The message to print", "desc_vi": "Thông báo cần in"},
                ],
                "returns": {"type": "None", "desc": "Prints to console", "desc_vi": "In ra console"},
                "usage": "Print_Message(message = 'Hello!')",
                "import_statement": "from src.modules.library.functions.logic_blocks import Print_Message",
                "source_func": "Print_Message",
                "source_module": "src.modules.library.functions.logic_blocks",
            },
        }
    },
    "Variables": {
        "color": "#14b8a6",
        "icon": "✏️",
        "functions": {
            "Create_Text": {
                "desc": "Create a text string variable",
                "desc_vi": "Tạo biến chuỗi văn bản",
                "params": [{"name": "value", "type": "Text (str)", "desc": "The text value to store", "desc_vi": "Giá trị văn bản cần lưu"}],
                "returns": {"type": "Text (str)", "desc": "A text string value", "desc_vi": "Giá trị chuỗi văn bản"},
                "usage": "my_text = Create_Text(value = 'Hello')",
                "import_statement": "from src.modules.library.functions.variables import Create_Text",
                "source_func": "Create_Text",
                "source_module": "src.modules.library.functions.variables",
            },
            "Create_Number": {
                "desc": "Create an integer number variable",
                "desc_vi": "Tạo biến số nguyên",
                "params": [{"name": "value", "type": "Number", "desc": "The integer value to store", "desc_vi": "Giá trị số nguyên cần lưu"}],
                "returns": {"type": "Number", "desc": "An integer number value", "desc_vi": "Giá trị số nguyên"},
                "usage": "my_number = Create_Number(value = '0')",
                "import_statement": "from src.modules.library.functions.variables import Create_Number",
                "source_func": "Create_Number",
                "source_module": "src.modules.library.functions.variables",
            },
            "Create_Decimal": {
                "desc": "Create a decimal (floating-point) number variable",
                "desc_vi": "Tạo biến số thập phân",
                "params": [{"name": "value", "type": "Number (float)", "desc": "The decimal value to store", "desc_vi": "Giá trị thập phân cần lưu"}],
                "returns": {"type": "Number (float)", "desc": "A floating-point number value", "desc_vi": "Giá trị số thập phân"},
                "usage": "my_decimal = Create_Decimal(value = '0.0')",
                "import_statement": "from src.modules.library.functions.variables import Create_Decimal",
                "source_func": "Create_Decimal",
                "source_module": "src.modules.library.functions.variables",
            },
            "Create_Boolean": {
                "desc": "Create a true/false boolean variable",
                "desc_vi": "Tạo biến đúng/sai (boolean)",
                "params": [{"name": "value", "type": "Boolean", "desc": "True or False", "desc_vi": "True hoặc False"}],
                "returns": {"type": "Boolean", "desc": "A boolean value (True or False)", "desc_vi": "Giá trị boolean (True hoặc False)"},
                "usage": "my_flag = Create_Boolean(value = 'True')",
                "import_statement": "from src.modules.library.functions.variables import Create_Boolean",
                "source_func": "Create_Boolean",
                "source_module": "src.modules.library.functions.variables",
            },
            "Create_List": {
                "desc": "Create a list variable (e.g., class names for detection)",
                "desc_vi": "Tạo biến danh sách (ví dụ: tên lớp để phát hiện)",
                "params": [{"name": "value", "type": "List", "desc": "The list value to store", "desc_vi": "Giá trị danh sách cần lưu"}],
                "returns": {"type": "List", "desc": "A list value", "desc_vi": "Giá trị danh sách"},
                "usage": "my_list = Create_List(value = None)",
                "import_statement": "from src.modules.library.functions.variables import Create_List",
                "source_func": "Create_List",
                "source_module": "src.modules.library.functions.variables",
            },
        },
    },
    "Robotics": {
        "color": "#f43f5e",  # Vibrant Rose (Swapped from Logic)
        "icon": "🤖",
        "functions": {
            "DC_Run": {
                "desc": "Run a DC or encoder motor at a given speed (with optional duration)",
                "desc_vi": "Chạy động cơ DC hoặc encoder ở tốc độ chỉ định (có thể đặt thời gian)",
                "params": [
                    {"name": "pin", "type": "Text (str)", "desc": "Motor port: 'M1', 'M2', 'M3', 'M4', 'E1', or 'E2'", "desc_vi": "Cổng động cơ: 'M1', 'M2', 'M3', 'M4', 'E1', hoặc 'E2'"},
                    {"name": "speed", "type": "Number (int)", "desc": "Power from -100 to 100 (positive = forward, negative = backward)", "desc_vi": "Công suất từ -100 đến 100 (dương = tiến, âm = lùi)"},
                    {"name": "time_ms", "type": "Number (int)", "desc": "Duration in milliseconds — leave blank to run forever", "desc_vi": "Thời gian chạy (mili giây) — để trống để chạy mãi"},
                ],
                "returns": {"type": "None", "desc": "Motor runs until time expires or DC_Stop is called", "desc_vi": "Động cơ chạy cho đến khi hết thời gian hoặc gọi DC_Stop"},
                "usage": "DC_Run(pin = 'M1', speed = 50, time_ms = None)",
                "import_statement": "from src.modules.library.functions.robotics import DC_Run",
                "source_func": "DC_Run",
                "source_module": "src.modules.library.functions.robotics",
            },
            "DC_Stop": {
                "desc": "Stop a specific motor or all motors at once",
                "desc_vi": "Dừng một động cơ cụ thể hoặc tất cả động cơ cùng lúc",
                "params": [
                    {"name": "pin", "type": "Text (str)", "desc": "Motor port: 'M1'-'M4', 'E1'-'E2' — leave blank to stop ALL", "desc_vi": "Cổng động cơ: 'M1'-'M4', 'E1'-'E2' — để trống để dừng TẤT CẢ"},
                ],
                "returns": {"type": "None", "desc": "Motor(s) stop immediately", "desc_vi": "Động cơ dừng ngay lập tức"},
                "usage": "DC_Stop(pin = 'M1')",
                "import_statement": "from src.modules.library.functions.robotics import DC_Stop",
                "source_func": "DC_Stop",
                "source_module": "src.modules.library.functions.robotics",
            },
            "Get_Speed": {
                "desc": "Read encoder motor speed in RPM (E1 or E2 only)",
                "desc_vi": "Đọc tốc độ động cơ encoder theo RPM (chỉ E1 hoặc E2)",
                "params": [
                    {"name": "pin", "type": "Text (str)", "desc": "Encoder port: 'E1' or 'E2'", "desc_vi": "Cổng encoder: 'E1' hoặc 'E2'"},
                ],
                "returns": {"type": "Number (float)", "desc": "Current speed in RPM", "desc_vi": "Tốc độ hiện tại (RPM)"},
                "usage": "rpm = Get_Speed(pin = 'E1')",
                "import_statement": "from src.modules.library.functions.robotics import Get_Speed",
                "source_func": "Get_Speed",
                "source_module": "src.modules.library.functions.robotics",
            },
            "Set_Servo": {
                "desc": "Rotate a servo motor to a specific angle",
                "desc_vi": "Xoay động cơ servo đến góc chỉ định",
                "params": [
                    {"name": "pin", "type": "Text (str)", "desc": "Servo port: 'S1', 'S2', 'S3', or 'S4'", "desc_vi": "Cổng servo: 'S1', 'S2', 'S3', hoặc 'S4'"},
                    {"name": "angle", "type": "Number (int)", "desc": "Target angle from 0 to 180 degrees", "desc_vi": "Góc mục tiêu từ 0 đến 180 độ"},
                ],
                "returns": {"type": "None", "desc": "Servo holds the target angle", "desc_vi": "Servo giữ ở góc mục tiêu"},
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