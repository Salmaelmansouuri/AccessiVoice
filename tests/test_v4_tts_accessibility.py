"""Non-regression of speech synthesis component without Web APIs in Python."""
from pathlib import Path
import pytest
from app.tts import build_player_html


def test_has_user_controlled_play_and_stop():
    html = build_player_html('Votre demande a été enregistrée.')
    assert 'speechSynthesis' in html
    assert 'addEventListener(\'click\'' in html
    assert 'Lire la réponse' in html
    assert 'Arrêter' in html
    assert "utterance.lang = 'fr-FR'" in html
    assert 'synth.speak(utterance)' in html
    assert 'synth.cancel()' in html


def test_untrusted_text_cannot_break_script_block():
    example = '</script><script>alert("bad")</script> & <img src=x>'
    html = build_player_html(example)
    assert example not in html
    assert '\\u003c/script\\u003e' in html
    assert html.count('</script>') == 1
    assert '\\u0026' in html


def test_html_sanitizes_newlines_and_quotes():
    html = build_player_html('Elle dit : "C’est bon".\nÀ demain.')
    assert 'SpeechSynthesisUtterance' in html
    assert 'À demain' in html


def test_rate_is_bounded():
    assert 'const rate = 0.7;' in build_player_html('Bonjour', 0.1)
    assert 'const rate = 1.3;' in build_player_html('Bonjour', 10)


@pytest.mark.parametrize('text', ['', '   '])
def test_empty_answer_not_spoken(text):
    with pytest.raises(ValueError):
        build_player_html(text)


def test_v3_features_retained_in_ui():
    interface = (Path(__file__).parents[1] / 'app' / 'interface.py').read_text(encoding='utf-8')
    assert "'/voice'" in interface
    assert "'/profil-demo'" in interface
    assert "'/demandes'" in interface
    assert "'/interactions'" in interface
    assert 'high_contrast_access' in interface
    assert 'large_text_access' in interface
    assert 'speak_answer(last.get(' in interface
