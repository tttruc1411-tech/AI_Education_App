# ============================================================
#  AI Education App — Jetson Orin Nano Dockerfile
#  Target:  NVIDIA Jetson Orin Nano (JetPack 6 / L4T r36.x)
#  Base:    nvcr.io/nvidia/pytorch (aarch64 / iGPU build)
#  Run:     ./run.sh   (or docker compose up)
# ============================================================

# ── Stage 1: Base ────────────────────────────────────────────
# Uses NVIDIA's official PyTorch container for Jetson (JetPack 6, aarch64).
# This bundles: CUDA 12.2, cuDNN 9, TensorRT 10, PyTorch 2.3 + torchvision.
# Check for the latest Jetson-compatible tag at:
#   https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch
FROM nvcr.io/nvidia/pytorch:24.08-py3-igpu

LABEL maintainer="KDI AI Education Project"
LABEL description="AI Coding Lab — PyQt5 desktop app for Jetson Orin Nano"
LABEL jetpack="6"

# ── Environment ───────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Skip the desktop-GPU driver version check — irrelevant on Jetson
    # where CUDA is part of the L4T BSP and always matches the hardware
    NVIDIA_DISABLE_REQUIRE=1 \
    # X11 display forwarding — set at runtime via 'run.sh'
    DISPLAY=:0 \
    QT_X11_NO_MITSHM=1 \
    # Tell Qt to use the xcb platform (X11) inside the container
    QT_QPA_PLATFORM=xcb \
    # Keeps pip from spamming the build log
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ── System Dependencies ───────────────────────────────────────
# Qt5 runtime libraries + X11 client + camera/video essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Qt5 runtime (PyQt5 needs these)
    libqt5gui5 \
    libqt5widgets5 \
    libqt5core5a \
    libqt5opengl5 \
    libqt5xml5 \
    libqt5network5 \
    qtbase5-dev \
    python3-pyqt5 \
    python3-pyqt5.qsci \
    # X11 / display forwarding
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libdbus-1-3 \
    x11-utils \
    # Camera / video (OpenCV)
    libv4l-dev \
    v4l-utils \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    # Build tools (needed for some pip packages on aarch64)
    build-essential \
    python3-dev \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python: Core Scientific Stack ────────────────────────────
# NOTE: torch & torchvision are already provided by the base image.
# We upgrade/install the remaining packages from requirements.txt.
# QScintilla (PyQt5 version) is the syntax-highlighted code editor.
RUN pip install --upgrade pip setuptools wheel

# Pin numpy<2 — the base image ships NumPy 2.x but OpenCV and other
# pre-compiled aarch64 packages were built against NumPy 1.x ABI.
RUN pip install \
    "numpy>=1.24.0,<2" \
    "scikit-learn>=1.3.0" \
    "joblib>=1.3.0" \
    "matplotlib>=3.7.0"

# ── OpenCV with GStreamer / V4L2 support ──────────────────────
# The headless variant avoids pulling in GUI libs twice.
# The Jetson JetPack SDK already ships libopencv; if you prefer that
# version, replace this block with: RUN apt-get install -y python3-opencv
RUN pip install "opencv-python-headless>=4.8.0"

# ── ONNX Runtime (GPU build for Jetson) ──────────────────────
# The standard 'onnxruntime' wheel from PyPI is CPU-only (no CUDA provider).
# For GPU inference on Jetson (JetPack 6, CUDA 12.6, cuDNN 9.3, TensorRT 10.3),
# you need onnxruntime-gpu built for aarch64 + CUDA 12.
#
# Option A — NVIDIA pre-built wheel (preferred, check for latest):
#   Browse: https://elinux.org/Jetson_Zoo#ONNX_Runtime
#   Or:     https://github.com/dusty-nv/jetson-containers
#
# Option B — Build from source:
#   git clone --recursive https://github.com/microsoft/onnxruntime
#   ./build.sh --config Release --use_cuda --cuda_home /usr/local/cuda \
#              --cudnn_home /usr --use_tensorrt --tensorrt_home /usr \
#              --build_wheel --parallel --skip_tests
#
# Override ONNXRUNTIME_URL at build time with the correct wheel for your setup:
#   docker build --build-arg ONNXRUNTIME_URL=<your_url> .
ARG ONNXRUNTIME_VERSION=1.20.0
ARG ONNXRUNTIME_WHEEL=onnxruntime_gpu-${ONNXRUNTIME_VERSION}-cp310-cp310-linux_aarch64.whl
ARG ONNXRUNTIME_URL=""

RUN if [ -n "${ONNXRUNTIME_URL}" ]; then \
        wget -q -O /tmp/${ONNXRUNTIME_WHEEL} ${ONNXRUNTIME_URL} && \
        pip install /tmp/${ONNXRUNTIME_WHEEL} && \
        rm /tmp/${ONNXRUNTIME_WHEEL}; \
    else \
        echo "WARNING: No ONNXRUNTIME_URL provided — installing CPU-only fallback." && \
        pip install "onnxruntime>=1.18.0"; \
    fi

# ── Ultralytics / YOLOv8 ─────────────────────────────────────
# Install without pulling in a conflicting torch version.
RUN pip install "ultralytics>=8.0.0" --extra-index-url https://pypi.ngc.nvidia.com

# ── NumPy ABI fix ────────────────────────────────────────────
# MUST run AFTER all pip installs. The base image and some packages
# pull in NumPy 2.x, but OpenCV (and other aarch64 binaries) were
# compiled against NumPy 1.x ABI. Force downgrade as the final step.
RUN pip install "numpy>=1.24.0,<2"

# ── Application Code ──────────────────────────────────────────
WORKDIR /app

# Copy project (respects .dockerignore)
COPY . /app

# Create writable project folders used at runtime
RUN mkdir -p projects/code projects/data projects/model

# ── Entrypoint ────────────────────────────────────────────────
# The GUI needs a real display — make sure you run with X11 forwarding.
# See run.sh for the recommended 'docker run' command.
CMD ["python3", "main.py"]
