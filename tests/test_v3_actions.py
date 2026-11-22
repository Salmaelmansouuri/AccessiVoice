"""Actions V3: modifications demo uniquement, demande confirmée, migration V2, filtre intact."""
import sqlite3
import pytest
from app import database


def test_profile_is_fictitious(client):
    resp = client.get('/profil-demo')
    assert resp.status_code == 200
    assert resp.json()['mode'] == 'demo'
    assert 'nom' in resp.json()['profil']


def test_edit_profile_validated_and_persisted(client):
    before = client.get('/profil-demo').json()['profil']
    try:
        response = client.patch('/profil-demo', json={
            'nom': 'Exemple', 'prenom': 'Camille', 'email': 'camille@example.invalid'
        })
        assert response.status_code == 200
        assert response.json()['profil']['nom'] == 'Exemple'
        assert client.get('/profil-demo').json()['profil']['prenom'] == 'Camille'
    finally:
        client.patch('/profil-demo', json=before)


@pytest.mark.parametrize('payload', [
    {'nom': '', 'prenom': 'Exemple', 'email': 'x@example.invalid'},
    {'nom': 'Demo', 'prenom': '', 'email': 'x@example.invalid'},
    {'nom': 'Demo', 'prenom': 'Exemple', 'email': 'pas-un-email'},
])
def test_profile_rejects_invalid_data(client, payload):
    assert client.patch('/profil-demo', json=payload).status_code == 422


def test_create_request_requires_specific_service(client):
    assert client.post('/demandes', json={}).status_code == 422
    before = len(client.get('/demandes').json()['demandes'])
    r = client.post('/execute', json={'texte': 'Je veux effectuer une demande'})
    assert r.status_code == 200
    assert r.json()['action_proposee'] == 'creer_demande'
    assert len(client.get('/demandes').json()['demandes']) == before


def test_create_request_and_find_in_history(client):
    service = next(s for s in client.get('/services').json()['services'] if s['ville'] == 'Casablanca')
    r = client.post('/demandes', json={'service_id': service['id']})
    assert r.status_code == 201
    demande = r.json()['demande']
    assert demande['service_id'] == service['id']
    assert demande['ville'] == 'Casablanca'
    history = client.get('/demandes').json()['demandes']
    assert any(row['id'] == demande['id'] for row in history)


def test_unavailable_service_cannot_be_requested(client):
    assert client.post('/demandes', json={'service_id': 5}).status_code == 409


def test_missing_service_cannot_be_requested(client):
    assert client.post('/demandes', json={'service_id': 99999}).status_code == 404


def test_voice_lookup_filter_unchanged_in_v3(client):
    r = client.post('/execute', json={'texte': 'Quels services sont disponibles à Casa Blanca ?'})
    assert r.status_code == 200
    assert r.json()['entites']['ville'] == 'Casablanca'
    assert all(s['ville'] == 'Casablanca' for s in r.json()['donnees']['services'])


def test_profile_intents_propose_correct_action(client):
    for phrase, action in [
        ('Je veux consulter mes informations', 'consulter_profil'),
        ('Je veux modifier mes informations', 'modifier_profil'),
    ]:
        response = client.post('/execute', json={'texte': phrase})
        assert response.status_code == 200
        assert response.json()['action_proposee'] == action


def test_migrates_existing_v2_database_without_losing_requests(tmp_path, monkeypatch):
    legacy = tmp_path / 'ancienne.sqlite3'
    with sqlite3.connect(legacy) as con:
        con.execute('''CREATE TABLE demandes (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       objet TEXT NOT NULL,
                       statut TEXT NOT NULL DEFAULT 'enregistrée',
                       date TEXT NOT NULL DEFAULT (datetime('now')))''')
        con.execute("INSERT INTO demandes(objet) VALUES ('Ancienne demande V2')")
    monkeypatch.setattr(database, 'DB_PATH', legacy)
    database.init_db()
    all_requests = database.list_requests()
    assert len(all_requests) == 1
    assert all_requests[0]['objet'] == 'Ancienne demande V2'
    assert all_requests[0]['service_id'] is None
    assert database.create_service_request(1)['service'] == 'Aide administrative'
    assert len(database.list_requests()) == 2
