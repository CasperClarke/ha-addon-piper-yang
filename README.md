# Piper Yang - Home Assistant Add-on

Piper TTS add-on with **0.2 second sentence spacing** between phrases. Uses the same Wyoming Piper server as the official add-on, with patches applied for `sentence_silence` support.

Optimized for the **en_US-yang-medium** voice (default), but works with any Piper voice.

## Features

- 0.2s pause between sentences (configurable)
- Same Wyoming integration and Zeroconf discovery as official Piper add-on
- All official Piper voices plus custom voices in `/share/piper`
- Yang voice as default (place `en_US-yang-medium.onnx` and `.onnx.json` in `/share/piper`)

## Installation

### Option A: Local add-on (no GitHub)

1. Enable **Samba** or **Terminal & SSH** add-on so you can access the config.

2. Copy the `ha-addon-piper-yang` folder so your config looks like:
   ```
   config/
     addons/
       ha-addon-piper-yang/
         repository.yaml
         piper-yang/
           config.yaml
           Dockerfile
           ...
   ```

3. Add as a **local add-on repository**:
   - **Settings** → **Add-ons** → **Add-on store** → **⋮** → **Repositories**
   - Add: `file:///config/addons/ha-addon-piper-yang`
   - (Or use the path where `repository.yaml` lives.)

4. Refresh; **Piper Yang** should appear. Install and start it.

### Option B: GitHub repository

1. Fork this repo or push it to your GitHub.
2. Add the repo URL in **Settings** → **Add-ons** → **Repositories**:
   ```
   https://github.com/YOUR_USERNAME/ha-addon-piper-yang
   ```
3. Update `repository.yaml` with your repo URL.
4. Install **Piper Yang** from the Add-on store.

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

## Building locally

From the `ha-addon-piper-yang` directory:

```bash
# With Home Assistant CLI (if available)
ha addons build piper-yang --arch aarch64

# Or with Docker
docker run --rm -v $(pwd):/build -w /build/piper-yang \
  ghcr.io/home-assistant/aarch64-base-debian:bookworm \
  /bin/bash -c "pip install wyoming-piper... && ..."
```

For production, use the [Home Assistant Add-on Builder](https://github.com/home-assistant/addons-developer-documentation) or push to GitHub and let the HA build system build it.
