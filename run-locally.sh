#!/bin/bash
# Run Piper Yang add-on locally for testing (no push to ghcr.io)
# Builds for your current arch (amd64) - faster than aarch64 emulation
#
# Usage: ./run-locally.sh
# Stop with Ctrl+C. Check logs for s6/piper startup.

set -e
cd "$(dirname "$0")/piper-yang"

REGISTRY="ghcr.io/casperclarke"
IMAGE="${REGISTRY}/amd64-addon-piper-yang:local"
DATA_DIR="$(mktemp -d)"
trap "rm -rf ${DATA_DIR}" EXIT

# Create minimal options.json so bashio can read config
mkdir -p "${DATA_DIR}"
cat > "${DATA_DIR}/options.json" << 'EOF'
{
  "voice": "en_US-yang-medium",
  "speaker": 0,
  "length_scale": 1.0,
  "noise_scale": 0.667,
  "noise_w": 0.333,
  "sentence_silence": 0.2,
  "debug_logging": true,
  "update_voices": false
}
EOF

echo "Building for amd64 (local arch)..."
docker buildx build \
  --load \
  --platform linux/amd64 \
  --build-arg BUILD_FROM=ghcr.io/home-assistant/amd64-base-debian:bookworm \
  --build-arg BUILD_ARCH=amd64 \
  --build-arg WYOMING_PIPER_VERSION=2.2.2 \
  --tag "${IMAGE}" \
  .

echo ""
echo "Running container..."
echo "  Piper listens on port 10200. Test: echo '{\"type\":\"describe\"}' | nc localhost 10200"
echo "  To stop: docker stop piper-yang-local (from another terminal, or Ctrl+C)"
echo ""

docker run --rm -it --name piper-yang-local \
  -p 10200:10200 \
  -v "${DATA_DIR}:/data" \
  -v "${DATA_DIR}:/share/piper" \
  "${IMAGE}"
