"""V5: navigation, vue d'ensemble, ergonomie et non-regression des endpoints existants."""
from pathlib import Path
import pytest
from app.ui_v5 import (PAGES, available_cities, filter_services, dashboard_counts,
                       response_meta, service_title)


@pytest.fixture
def demos():
    return [
        {'id': 1, 'nom': 'Aide administrative', 'ville': 'Casablanca', 'description': 'Démarches'},
        {'id': 2, 'nom': 'Informatique', 'ville': 'Casablanca', 'description': 'Accompagnement'},
        {'id': 3, 'nom': 'Information', 'ville': 'Marrakech', 'description': 'Information'},
    ]


def test_seven_distinct_navigation_pages():
    assert len(PAGES) == 7
    assert len(set(PAGES)) == 7
    assert any('Assistant vocal' in p for p in PAGES)
    assert any('Accessibilité' in p for p in PAGES)


def test_city_filter_keeps_only_requested_city(demos):
    rows = filter_services(demos, 'Casablanca')
    assert len(rows) == 2
    assert all(x['ville'] == 'Casablanca' for x in rows)


def test_city_filter_case_insensitive(demos):
    assert len(filter_services(demos, 'CASABLANCA')) == 2


def test_city_filter_none_means_all(demos):
    assert filter_services(demos, None) == demos
    assert filter_services(demos, 'Toutes les villes') == demos


def test_city_filter_does_not_modify_original(demos):
    before = [dict(item) for item in demos]
    filter_services(demos, 'Marrakech')
    assert demos == before


def test_available_cities_sorted_unique(demos):
    assert available_cities(demos) == ['Casablanca', 'Marrakech']


def test_available_cities_no_missing_names():
    assert available_cities([{}, {'ville': ''}, {'ville': 'Rabat'}]) == ['Rabat']


def test_dashboard_metrics_report_returned_rows(demos):
    counts = dashboard_counts(demos, [{'id': 2}], [{'id': 3}, {'id': 4}])
    assert counts == {'services': 3, 'demandes': 1, 'interactions': 2}


def test_service_title(demos):
    assert service_title(demos[0]) == 'Aide administrative — Casablanca'


@pytest.mark.parametrize('bad_value', [-2, 2, 'invalide', None])
def test_confidence_robust_bounds(bad_value):
    _, conf, _ = response_meta({'confiance': bad_value})
    assert 0 <= conf <= 1


def test_response_meta_city_when_available():
    assert response_meta({'intention': 'rechercher_service', 'confiance': .62,
                          'entites': {'ville': 'Casablanca'}}) == ('rechercher_service', .62, 'Casablanca')


def test_response_meta_old_response_without_entities():
    assert response_meta({'intention': 'aide'}) == ('aide', 0, None)


def test_interface_has_no_automatic_requests_from_nlp():
    ui = (Path(__file__).parents[1] / 'app/interface.py').read_text(encoding='utf-8')
    assert 'if confirm_request:' in ui
    assert "api_post('/demandes'" in ui
    assert "api_post('/execute'" in ui
    assert "API + '/voice'" in ui
    assert 'st.audio_input' in ui
    assert 'st.sidebar' in ui
    assert 'st.metric' not in ui or '.metric(' in ui
    assert 'speak_answer(last.get(' in ui
    assert 'high_contrast_access' in ui and 'large_text_access' in ui
    assert 'build_player_html' in ui


def test_v5_keeps_all_api_routes_from_v4(client):
    assert client.get('/health').status_code == 200
    assert client.get('/services').status_code == 200
    assert client.get('/demandes').status_code == 200
    assert client.get('/profil-demo').status_code == 200
    assert client.get('/interactions').status_code == 200


def test_request_needs_explicit_post(client):
    before = len(client.get('/demandes').json()['demandes'])
    cmd = client.post('/execute', json={'texte': 'Je souhaite effectuer une demande'})
    assert cmd.status_code == 200
    assert len(client.get('/demandes').json()['demandes']) == before
