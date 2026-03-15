#!/usr/bin/env python3
"""Apply sentence-silence patches to wyoming-piper and piper-tts."""
import site
from pathlib import Path

SITE = Path(site.getsitepackages()[0])

# 1. wyoming_piper/__main__.py - add --sentence-silence before --auto-punctuation
main_py = SITE / "wyoming_piper" / "__main__.py"
text = main_py.read_text()
if "--sentence-silence" not in text:
    # Insert after noise-w-scale block, before auto-punctuation
    marker = 'parser.add_argument(\n        "--auto-punctuation"'
    insert = '''parser.add_argument(
        "--sentence-silence",
        type=float,
        default=0.2,
        help="Seconds of silence between sentences (default: 0.2)",
    )
    #
    parser.add_argument(
        "--auto-punctuation"'''
    text = text.replace(marker, insert)
    main_py.write_text(text)
    print("Patched wyoming_piper/__main__.py")
else:
    print("wyoming_piper/__main__.py already patched")

# 2. wyoming_piper/handler.py - pass sentence_silence to syn_config
handler_py = SITE / "wyoming_piper" / "handler.py"
text = handler_py.read_text()
if "syn_config.sentence_silence" not in text:
    marker = "syn_config.noise_w_scale = self.cli_args.noise_w_scale\n\n        wav_writer"
    insert = "syn_config.noise_w_scale = self.cli_args.noise_w_scale\n\n        if getattr(self.cli_args, \"sentence_silence\", 0) > 0:\n            syn_config.sentence_silence = self.cli_args.sentence_silence\n\n        wav_writer"
    text = text.replace(marker, insert)
    handler_py.write_text(text)
    print("Patched wyoming_piper/handler.py")
else:
    print("wyoming_piper/handler.py already patched")

# 3. piper/config.py - add sentence_silence to SynthesisConfig
config_py = SITE / "piper" / "config.py"
text = config_py.read_text()
if "sentence_silence" not in text:
    old = '''    volume: float = 1.0
    """Multiplier for audio samples (< 1 is quieter, > 1 is louder)."""'''
    new = '''    volume: float = 1.0
    """Multiplier for audio samples (< 1 is quieter, > 1 is louder)."""

    sentence_silence: float = 0.0
    """Seconds of silence to add between sentences."""'''
    text = text.replace(old, new)
    config_py.write_text(text)
    print("Patched piper/config.py")
else:
    print("piper/config.py already patched")

# 4. piper/voice.py - add silence between chunks in synthesize_wav
voice_py = SITE / "piper" / "voice.py"
text = voice_py.read_text()
if "silence_sec" not in text:
    marker = "first_chunk = True\n        for audio_chunk in self.synthesize("
    insert = "first_chunk = True\n        silence_sec = (\n            getattr(syn_config, \"sentence_silence\", 0) or 0 if syn_config else 0\n        )\n        for audio_chunk in self.synthesize("
    text = text.replace(marker, insert)
    marker2 = "first_chunk = False\n\n            wav_file.writeframes(audio_chunk.audio_int16_bytes)"
    insert2 = "first_chunk = False\n            elif silence_sec > 0:\n                num_silence = int(silence_sec * audio_chunk.sample_rate)\n                wav_file.writeframes(b'\\x00\\x00' * num_silence)\n\n            wav_file.writeframes(audio_chunk.audio_int16_bytes)"
    text = text.replace(marker2, insert2)
    voice_py.write_text(text)
    print("Patched piper/voice.py")
else:
    print("piper/voice.py already patched")

print("Done.")
