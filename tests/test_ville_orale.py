"""Regression tests based on the real microphone transcript seen in the demo."""
import pytest
from app.engine import extract_entities


@pytest.mark.parametrize(('text','expected'), [
    ('Quels services sont disponibles à Casablanca ?', 'Casablanca'),
    ("Qu'est-ce service sont disponibles à Casa Blanca ?", 'Casablanca'),
    ('Je cherche des services à Casa-Blanca', 'Casablanca'),
    ('Quels services il y a à Casablanka ?', 'Casablanca'),
    ('Je suis à Casa, quels services sont disponibles ?', 'Casablanca'),
    ('Je cherche des services à Rabat', 'Rabat'),
    ('Les services à Marrakech', 'Marrakech'),
    ('Les services à Marrakesh', 'Marrakech'),
    ('Quels services sont disponibles ?', None),
])
def test_city_spoken_variations(text, expected):
    assert extract_entities(text)['ville'] == expected


def test_real_voice_transcript_filters_casablanca(client):
    response = client.post('/execute', json={'texte': "Qu'est-ce service sont disponibles à Casa Blanca ?"})
    assert response.status_code == 200
    data = response.json()
    assert data['intention'] == 'rechercher_service'
    assert data['entites']['ville'] == 'Casablanca'
    assert len(data['donnees']['services']) == 2
    assert all(service['ville'] == 'Casablanca' for service in data['donnees']['services'])
    assert 'Rabat' not in data['reponse']
    assert 'Marrakech' not in data['reponse']


def test_query_without_city_keeps_all_available_services(client):
    response = client.post('/execute', json={'texte': 'Quels services sont disponibles ?'})
    assert response.status_code == 200
    data = response.json()
    assert data['intention'] == 'rechercher_service'
    assert data['entites']['ville'] is None
    assert len(data['donnees']['services']) == 4


def test_voice_pipeline_with_whisper_spelling_city(client, monkeypatch):
    """Exercise /voice with a simulated transcription, without claiming a live-mic test."""
    import sys
    import types
    from app.main import local_whisper_model
    class DummyWhisper:
        def transcribe(self, audio, language):
            assert language == 'fr'
            return [types.SimpleNamespace(text="Qu'est-ce service sont disponibles à Casa Blanca ?")], None
    monkeypatch.setitem(sys.modules, 'faster_whisper', types.SimpleNamespace(WhisperModel=DummyWhisper))
    monkeypatch.setattr('app.main.local_whisper_model', lambda model_name: DummyWhisper())
    response = client.post('/voice', files={'file': ('test.wav', b'RIFFtest', 'audio/wav')})
    assert response.status_code == 200
    assert response.json()['entites']['ville'] == 'Casablanca'
    assert all(s['ville'] == 'Casablanca' for s in response.json()['donnees']['services'])
