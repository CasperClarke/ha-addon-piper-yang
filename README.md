# Piper Yang - Home Assistant Add-on

Piper TTS add-on with **0.2 second sentence spacing** between phrases. Uses the same Wyoming Piper server as the official add-on, with patches applied for `sentence_silence` support.

Optimized for the **en_US-yang-medium** voice (default), but works with any Piper voice.

## Features

- 0.2s pause between sentences (configurable)
- Same Wyoming integration and Zeroconf discovery as official Piper add-on
- All official Piper voices plus custom voices in `/share/piper`
- Yang voice as default (place `en_US-yang-medium.onnx` and `.onnx.json` in `/share/piper`)

## Installation

1. In Home Assistant: **Settings** → **Add-ons** → **Add-on store** → **⋮** (top right) → **Repositories**
2. Add: `https://github.com/CasperClarke/ha-addon-piper-yang`
3. Click **Refresh**, then find **Piper Yang** in the Add-on store
4. Install and start it

## Configuration

| Option            | Default              | Description                              |
|-------------------|----------------------|------------------------------------------|
| voice             | en_US-yang-medium    | Piper voice to use                       |
| speaker           | 0                    | Speaker ID (multi-speaker voices)        |
| length_scale      | 1.0                  | Speech speed                             |
| noise_scale       | 0.667                | Audio variation                          |
| noise_w           | 0.333                | Phoneme width noise                      |
| **sentence_silence** | **0.2**          | **Seconds of pause between sentences**   |
| debug_logging     | false                | Enable debug logs                        |
| update_voices     | true                 | Update voices list at startup            |

## Custom Yang Voice

Copy your Yang voice files to `/share/piper/`:

- `en_US-yang-medium.onnx`
- `en_US-yang-medium.onnx.json`

Use **File editor**, **Samba**, or `scp`. The voice will be discovered automatically.

## Switching from Official Piper

1. **Stop** the official Piper add-on.
2. **Install** Piper Yang and **start** it.
3. Use the same port (10200) and Zeroconf name. Home Assistant will discover it automatically.
4. If needed, restart the Voice Assistant or reconfigure the TTS integration.

## Building

### GitHub Actions (automatic)

Pushes to `main` trigger a build. Images are pushed to `ghcr.io/casperclarke/{arch}-addon-piper-yang`.

### Local build and push

For faster testing without waiting for CI:

```bash
# 1. Log in to ghcr.io (GitHub PAT with write:packages)
docker login ghcr.io

# 2. Build and push aarch64 (for Raspberry Pi)
./build-and-push.sh           # version from config.yaml
./build-and-push.sh 2.2.2.2   # custom version
```

Requires: `docker-buildx-plugin` and optionally QEMU for cross-platform builds.

### Local run (no push)

Test the container locally before pushing:

```bash
./run-locally.sh
```

Builds for amd64, runs with mock config. Piper listens on port 10200. Stop with `docker stop piper-yang-local` from another terminal.
