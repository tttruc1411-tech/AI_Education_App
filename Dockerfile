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
LABEL description="AI Coding Lab — PyQt6 desktop app for Jetson Orin Nano"
LABEL jetpack="6"

# ── Environment ───────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # X11 display forwarding — set at runtime via 'run.sh'
    DISPLAY=:0 \
    QT_X11_NO_MITSHM=1 \
    # Tell Qt to use the xcb platform (X11) inside the container
    QT_QPA_PLATFORM=xcb \
    # Keeps pip from spamming the build log
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ── System Dependencies ───────────────────────────────────────
# Qt6 runtime libraries + X11 client + camera/video essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Qt6 runtime (PyQt6 needs these)
    libqt6gui6 \
    libqt6widgets6 \
    libqt6core6 \
    libqt6opengl6 \
    libqt6xml6 \
    libqt6network6 \
    qt6-base-dev \
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
# PyQt6-QScintilla is the syntax-highlighted code editor.
RUN pip install --upgrade pip setuptools wheel

# Install packages that work fine straight from PyPI on aarch64
RUN pip install \
    "PyQt6>=6.4.0" \
    "PyQt6-QScintilla>=2.14.0" \
    "numpy>=1.24.0" \
    "scikit-learn>=1.3.0" \
    "joblib>=1.3.0" \
    "matplotlib>=3.7.0"

# ── OpenCV with GStreamer / V4L2 support ──────────────────────
# The headless variant avoids pulling in GUI libs twice.
# The Jetson JetPack SDK already ships libopencv; if you prefer that
# version, replace this block with: RUN apt-get install -y python3-opencv
RUN pip install "opencv-python-headless>=4.8.0"

# ── ONNX Runtime (GPU build for Jetson) ──────────────────────
# The standard onnxruntime wheel from PyPI is CPU-only.
# The GPU build for JetPack 6 / aarch64 is distributed by NVIDIA:
#   https://elinux.org/Jetson_Zoo#ONNX_Runtime
# We pull the pre-built wheel directly (adjust version/URL if needed).
ARG ONNXRUNTIME_VERSION=1.18.0
ARG ONNXRUNTIME_WHEEL=onnxruntime_gpu-${ONNXRUNTIME_VERSION}-cp310-cp310-linux_aarch64.whl
ARG ONNXRUNTIME_URL=https://nvidia.box.com/shared/static/48dtuob7meiw6ebgfsfqakc9vse62sg4.whl

RUN wget -q -O /tmp/${ONNXRUNTIME_WHEEL} ${ONNXRUNTIME_URL} && \
    pip install /tmp/${ONNXRUNTIME_WHEEL} && \
    rm /tmp/${ONNXRUNTIME_WHEEL}

# ── Ultralytics / YOLOv8 ─────────────────────────────────────
# Install without pulling in a conflicting torch version.
RUN pip install "ultralytics>=8.0.0" --extra-index-url https://pypi.ngc.nvidia.com

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
