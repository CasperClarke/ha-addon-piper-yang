#!/usr/bin/env python3
"""Apply sentence-silence patches to wyoming-piper and piper-tts."""
import re
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

# 2. wyoming_piper/handler.py - pass sentence_silence to syn_config AND add silence between sentences
handler_py = SITE / "wyoming_piper" / "handler.py"
text = handler_py.read_text()

# 2a. Pass sentence_silence to syn_config
if "syn_config.sentence_silence" not in text:
    marker = "syn_config.noise_w_scale = self.cli_args.noise_w_scale\n\n        wav_writer"
    insert = "syn_config.noise_w_scale = self.cli_args.noise_w_scale\n\n        if getattr(self.cli_args, \"sentence_silence\", 0) > 0:\n            syn_config.sentence_silence = self.cli_args.sentence_silence\n\n        wav_writer"
    text = text.replace(marker, insert)
    print("Patched wyoming_piper/handler.py (syn_config)")

    # 2b. Add add_silence_after param to _handle_synthesize
if "add_silence_after" not in text:
    text = text.replace(
        "send_start: bool = True, send_stop: bool = True\n    ) -> bool:",
        "send_start: bool = True, send_stop: bool = True, add_silence_after: bool = False\n    ) -> bool:",
    )
    # 2c. Add silence chunks after the audio loop, before "if send_stop"
    silence_block = '''
        # Inject silence between sentences (handler-level; each sentence = separate _handle_synthesize)
        if add_silence_after:
            silence_sec = getattr(self.cli_args, "sentence_silence", 0) or 0
            _LOGGER.debug("Piper Yang: add_silence_after=True, sentence_silence=%.2f", silence_sec)
        if add_silence_after and getattr(self.cli_args, "sentence_silence", 0) > 0:
            silence_sec = self.cli_args.sentence_silence
            total_silence_bytes = int(silence_sec * rate) * channels * width
            chunk_size = bytes_per_sample * self.cli_args.samples_per_chunk
            num_silence_chunks = max(1, (total_silence_bytes + chunk_size - 1) // chunk_size)
            silence_chunk = b"\\x00\\x00" * (self.cli_args.samples_per_chunk * channels)
            for _ in range(num_silence_chunks):
                await self.write_event(
                    AudioChunk(audio=silence_chunk, rate=rate, width=width, channels=channels).event(),
                )

'''
    # Match "if send_stop:" with possible whitespace variations (use lambda to avoid re parsing \x in replacement)
    pattern = r"(\n\s+if send_stop:\s*\n\s+await self\.write_event\(AudioStop\(\)\.event\(\)\))"
    if re.search(pattern, text):
        text = re.sub(pattern, lambda m: silence_block + m.group(1), text, count=1)
    else:
        # Fallback: insert before "if send_stop"
        text = text.replace(
            "\n        if send_stop:\n            await self.write_event(AudioStop().event())",
            silence_block + "\n        if send_stop:\n            await self.write_event(AudioStop().event())",
        )
    # 2d. Call site: pass add_silence_after=True for non-final sentences (for loop)
    text = text.replace(
        "send_start=(i == 0), send_stop=False\n        )",
        "send_start=(i == 0), send_stop=False, add_silence_after=True\n        )",
    )
    # 2e. Streaming: pass add_silence_after=True (adds silence between streamed sentences)
    text = text.replace(
        "await self._handle_synthesize(self._synthesize)",
        "await self._handle_synthesize(self._synthesize, add_silence_after=True)",
        1,  # Only first occurrence (SynthesizeChunk loop)
    )
    print("Patched wyoming_piper/handler.py (add_silence_after)")
else:
    print("wyoming_piper/handler.py (add_silence_after) already patched")

handler_py.write_text(text)

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
