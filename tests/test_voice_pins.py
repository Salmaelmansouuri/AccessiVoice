"""Evite les regressions sur la version de PyAV avec faster-whisper 1.2.1."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_voice_requirements_pin_pyav():
    req = (ROOT / 'requirements-voice.txt').read_text(encoding='utf-8')
    assert 'av==18.1.0' in req
    assert 'faster-whisper==1.2.1' in req

def test_windows_launcher_detects_av_version():
    script = (ROOT / 'LANCER_ACCESSIVOICE.bat').read_text(encoding='utf-8')
    assert "m.version('av') == '18.1.0'" in script
