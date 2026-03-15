#!/bin/bash
# Build Piper Yang add-on locally and push to ghcr.io
#
# Prerequisites:
#   1. docker login ghcr.io (GitHub PAT with write:packages)
#   2. docker-buildx plugin (install manually if needed)
#   3. QEMU for aarch64 emulation (script will try to set up automatically)
#
# Usage: ./build-and-push.sh [version]
#   ./build-and-push.sh           # builds 2.2.2.1
#   ./build-and-push.sh 2.2.2.2   # builds custom version

set -e
cd "$(dirname "$0")/piper-yang"

VERSION="${1:-2.2.2.1}"
REGISTRY="ghcr.io/casperclarke"

# Require buildx for cross-platform build + push
if ! docker buildx version &>/dev/null; then
  echo "Docker buildx is required but not installed."
  echo "Install it with:  sudo apt install docker-buildx-plugin"
  exit 1
fi

# Register QEMU/binfmt so amd64 host can emulate aarch64 during build
echo "Ensuring QEMU emulation for aarch64..."
docker run --privileged --rm tonistiigi/binfmt --install all 2>/dev/null || {
  echo "Could not install QEMU emulation. If you get 'exec format error', run:"
  echo "  sudo docker run --privileged --rm tonistiigi/binfmt --install all"
  echo ""
}

echo "Building Piper Yang add-on v${VERSION}..."
echo ""

# Build for aarch64 (Raspberry Pi)
echo "Building aarch64 image..."
docker buildx build \
  --platform linux/aarch64 \
  --build-arg BUILD_FROM=ghcr.io/home-assistant/aarch64-base-debian:bookworm \
  --build-arg BUILD_ARCH=aarch64 \
  --build-arg WYOMING_PIPER_VERSION=2.2.2 \
  --tag "${REGISTRY}/aarch64-addon-piper-yang:${VERSION}" \
  --tag "${REGISTRY}/aarch64-addon-piper-yang:latest" \
  --push \
  .

echo ""
echo "Pushed ${REGISTRY}/aarch64-addon-piper-yang:${VERSION}"
echo ""
echo "To use: Update the Piper Yang add-on in Home Assistant (or reinstall)."
