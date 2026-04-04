#!/usr/bin/env bash
# ============================================================
#  run.sh — Build & launch the AI Education App on Jetson
#  Usage:   chmod +x run.sh && ./run.sh
# ============================================================

set -euo pipefail

IMAGE="ai-education-app:jetson"

# ── 1. Allow the container to connect to the host X server ───
echo "[run.sh] Granting X11 access to local connections..."
xhost +local:docker 2>/dev/null || true

# ── 2. Build the image (skip if already up-to-date) ──────────
echo "[run.sh] Building Docker image: ${IMAGE}..."
docker build -t "${IMAGE}" .

# ── 3. Run the container ──────────────────────────────────────
echo "[run.sh] Starting AI Education App..."
docker run --rm -it \
    --runtime=nvidia \
    --network=host \
    \
    `# GPU & display` \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e DISPLAY="${DISPLAY:-:0}" \
    -e QT_X11_NO_MITSHM=1 \
    -e QT_QPA_PLATFORM=xcb \
    \
    `# X11 socket` \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    \
    `# Persistent data volumes` \
    -v "$(pwd)/projects:/app/projects" \
    -v "$(pwd)/curriculum:/app/curriculum" \
    \
    `# Camera device(s)` \
    --device=/dev/video0 \
    \
    "${IMAGE}"
