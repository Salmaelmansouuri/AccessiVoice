"""Checks actual browser-format WAV decoding and the voice endpoint contract."""
import io
import sys
import types
import wave

import numpy as np
from app.voice_audio import pcm_wav_to_whisper


def build_wav(rate=48000, channels=2, duration=0.12):
    x = np.arange(int(rate * duration)) / rate
    tone = np.sin(2 * np.pi * 440 * x)
    pcm = (tone * 8192).astype('<i2')
    if channels == 2:
        pcm = np.column_stack([pcm, pcm]).ravel()
    out = io.BytesIO()
    with wave.open(out, 'wb') as f:
        f.setnchannels(channels)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(pcm.tobytes())
    return out.getvalue()


def test_mono_16k_pcm_is_decoded():
    decoded = pcm_wav_to_whisper(build_wav(rate=16000, channels=1))
    assert decoded.dtype == np.float32
    assert decoded.ndim == 1
    assert len(decoded) == 1920
    assert np.max(np.abs(decoded)) > 0.1


def test_stereo_48k_pcm_is_resampled():
    decoded = pcm_wav_to_whisper(build_wav(rate=48000, channels=2))
    assert decoded.dtype == np.float32
    assert len(decoded) == 1920
    assert np.max(np.abs(decoded)) > 0.1


def test_wav_to_endpoint_bypasses_pyav(client, monkeypatch):
    from app.main import local_whisper_model

    class DummyModel:
        def __init__(self, *args, **kwargs):
            pass
        def transcribe(self, audio, language):
            # Audio is ready for Whisper, NOT a file path: no PyAV decode.
            assert isinstance(audio, np.ndarray)
            assert audio.dtype == np.float32
            assert len(audio) == 1920
            assert language == 'fr'
            return [types.SimpleNamespace(text='Je cherche des services à Casablanca')], None

    monkeypatch.setitem(sys.modules, 'faster_whisper', types.SimpleNamespace(WhisperModel=DummyModel))
    local_whisper_model.cache_clear()
    try:
        response = client.post('/voice', files={'file': ('micro.wav', build_wav(), 'audio/wav')})
        assert response.status_code == 200, response.text
        assert response.json()['intention'] == 'rechercher_service'
    finally:
        local_whisper_model.cache_clear()


def test_zero_length_wav_is_rejected():
    import pytest
    with pytest.raises((ValueError, EOFError)):
        pcm_wav_to_whisper(build_wav(duration=0))
