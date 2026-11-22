def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['statut'] == 'ok'


def test_services(client):
    response = client.get('/services', params={'ville': 'Casablanca'})
    assert response.status_code == 200
    assert len(response.json()['services']) >= 1
    assert all(x['ville'] == 'Casablanca' for x in response.json()['services'])


def test_prediction(client):
    response = client.post('/predict-intent', json={'texte': 'Quels services sont disponibles ?'})
    assert response.status_code == 200
    assert response.json()['intention'] == 'rechercher_service'


def test_execute_lookup(client):
    response = client.post('/execute', json={'texte': 'Je cherche des services à Casablanca'})
    assert response.status_code == 200
    assert 'Casablanca' in response.json()['reponse']
    assert response.json()['entites']['ville'] == 'Casablanca'


def test_help(client):
    response = client.post('/execute', json={'texte': 'Comment utiliser cette application ?'})
    assert response.status_code == 200
    assert response.json()['intention'] == 'aide'


def test_request_intent_prepares_action_without_creating(client):
    before = len(client.get('/demandes').json()['demandes'])
    response = client.post('/execute', json={'texte': 'Je veux effectuer une demande'})
    assert response.status_code == 200
    assert response.json()['action_proposee'] == 'creer_demande'
    assert len(client.get('/demandes').json()['demandes']) == before


def test_history(client):
    response = client.get('/interactions')
    assert response.status_code == 200
    assert len(response.json()['interactions']) > 0


def test_reject_empty(client):
    assert client.post('/execute', json={'texte': ''}).status_code == 422


def test_audio_reject_extension(client):
    response = client.post('/voice', files={'file': ('malware.exe', b'test', 'application/octet-stream')})
    assert response.status_code == 415


def test_audio_reject_empty(client):
    response = client.post('/voice', files={'file': ('empty.wav', b'', 'audio/wav')})
    assert response.status_code == 422


def test_voice_success_with_fake_transcriber(client, monkeypatch):
    """Integration contract without downloading a large external Whisper model."""
    import sys
    import types
    from app.main import local_whisper_model

    class DummyModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, path, language):
            assert language == 'fr'
            return [types.SimpleNamespace(text='Je cherche des services à Casablanca')], None

    monkeypatch.setitem(sys.modules, 'faster_whisper', types.SimpleNamespace(WhisperModel=DummyModel))
    local_whisper_model.cache_clear()
    try:
        response = client.post('/voice', files={'file': ('test.wav', b'RIFFtest', 'audio/wav')})
        assert response.status_code == 200
        assert response.json()['intention'] == 'rechercher_service'
    finally:
        local_whisper_model.cache_clear()


def test_voice_failure_includes_useful_diagnostic(client, monkeypatch):
    import sys
    import types
    from app.main import local_whisper_model

    class BrokenModel:
        def __init__(self, *args, **kwargs):
            raise RuntimeError('modele de test indisponible')

    monkeypatch.setitem(sys.modules, 'faster_whisper', types.SimpleNamespace(WhisperModel=BrokenModel))
    local_whisper_model.cache_clear()
    try:
        response = client.post('/voice', files={'file': ('test.wav', b'RIFFtest', 'audio/wav')})
        assert response.status_code == 503
        assert 'RuntimeError' in response.json()['detail']
        assert 'logs/api.log' in response.json()['detail']
    finally:
        local_whisper_model.cache_clear()
