"""Convert the browser's PCM WAV to Whisper's expected mono float32, 16 kHz.

Avoids passing a WAV path to faster-whisper's PyAV decoder. This avoids the
PyAV 19 `metadata_errors` API incompatibility for Streamlit microphone audio.
Non-PCM codecs continue through faster-whisper's normal decoder (PyAV pinned).
"""
from __future__ import annotations

import io
import wave
from fractions import Fraction

import numpy as np
from scipy.signal import resample_poly


def pcm_wav_to_whisper(data: bytes, sample_rate: int = 16000) -> np.ndarray:
    """Decode PCM mono/stereo WAV bytes to normalized mono float32 sample array.

    Supports standard 8, 16, 24 and 32-bit integer PCM. Raises wave.Error or
    ValueError for unsupported WAV encodings; callers can use a codec fallback.
    """
    with wave.open(io.BytesIO(data), 'rb') as source:
        if source.getcomptype() != 'NONE':
            raise ValueError(f'Compression WAV non prise en charge: {source.getcomptype()}')
        channels = source.getnchannels()
        src_rate = source.getframerate()
        width = source.getsampwidth()
        count = source.getnframes()
        if channels < 1 or channels > 8 or src_rate < 1000 or src_rate > 192000:
            raise ValueError('En-tete WAV invalide')
        if count < 1:
            raise ValueError('Enregistrement vide')
        if count / src_rate > 120:
            raise ValueError('Audio trop long : 120 secondes maximum')
        frames = source.readframes(count)

    if width == 1:
        samples = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif width == 2:
        samples = np.frombuffer(frames, dtype='<i2').astype(np.float32) / 32768.0
    elif width == 3:
        chunks = np.frombuffer(frames, dtype=np.uint8)
        if chunks.size % 3:
            raise ValueError('WAV 24 bits incomplet')
        triplets = chunks.reshape(-1, 3).astype(np.int32)
        values = triplets[:, 0] | (triplets[:, 1] << 8) | (triplets[:, 2] << 16)
        samples = ((values ^ 0x800000) - 0x800000).astype(np.float32) / 8388608.0
    elif width == 4:
        samples = np.frombuffer(frames, dtype='<i4').astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f'WAV PCM : resolution de {8*width} bits non prise en charge')

    if samples.size % channels:
        raise ValueError('Trame WAV incomplete')
    audio = samples.reshape(-1, channels).mean(axis=1, dtype=np.float32)
    if src_rate != sample_rate:
        divisor = Fraction(sample_rate, src_rate)
        audio = resample_poly(audio, divisor.numerator, divisor.denominator)
    return np.ascontiguousarray(audio, dtype=np.float32)
