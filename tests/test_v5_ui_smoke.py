"""Render every V5 page with simulated Streamlit controls and a fake local API.

This does NOT replace a real browser or a microphone test; it detects Python
exceptions and integration assumptions in all seven page branches.
"""
from __future__ import annotations
import runpy
import sys
import types
from pathlib import Path
from unittest.mock import patch
import pytest
from app.ui_v5 import PAGES


class FakeContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class FakeStreamlit(types.ModuleType):
    def __init__(self, page):
        super().__init__('streamlit')
        self.session_state = {'av_nav_v5': page}
        self.sidebar = FakeContext()
        self._context = FakeContext()

    def columns(self, *args, **kwargs):
        count = args[0] if isinstance(args[0], int) else len(args[0])
        return [FakeContext() for _ in range(count)]

    def container(self, *args, **kwargs):
        return self._context

    def expander(self, *args, **kwargs):
        return self._context

    def form(self, *args, **kwargs):
        return self._context

    def radio(self, label, options, key=None, **kwargs):
        return self.session_state.get(key, options[0])

    def toggle(self, label, key=None, **kwargs):
        self.session_state.setdefault(key, False)
        return self.session_state[key]

    def select_slider(self, label, key=None, **kwargs):
        return self.session_state.get(key, 0.95)

    def selectbox(self, label, options, key=None, **kwargs):
        return self.session_state.get(key, options[0])

    def text_input(self, label, value='', **kwargs):
        return value

    def button(self, *args, **kwargs):
        return False

    def form_submit_button(self, *args, **kwargs):
        return False

    def audio_input(self, *args, **kwargs):
        return None

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def fake_get(url, timeout=None):
    routes = {
        '/health': {'statut': 'ok'},
        '/services': {'services': [
            {'id': 1, 'nom': 'Aide administrative', 'description': 'Essai', 'ville': 'Casablanca'},
            {'id': 3, 'nom': 'Information citoyenne', 'description': 'Essai', 'ville': 'Marrakech'},
        ]},
        '/demandes': {'demandes': [
            {'id': 1, 'objet': 'Demande fictive', 'date': '2026-11-22', 'statut': 'enregistrée'}]},
        '/interactions': {'interactions': [
            {'date': '2026-11-22', 'commande': 'Bonjour', 'intention': 'aide', 'reponse': 'Bonjour'}]},
        '/profil-demo': {'profil': {'nom': 'Démo', 'prenom': 'Utilisateur', 'email': 'demo@example.invalid'}},
    }
    for route, body in routes.items():
        if url.endswith(route):
            return FakeResponse(body)
    raise RuntimeError('Unexpected API call ' + url)


@pytest.mark.parametrize('page', PAGES)
def test_page_renders_with_simulated_streamlit(page):
    st = FakeStreamlit(page)
    components = types.ModuleType('streamlit.components')
    comp_v1 = types.ModuleType('streamlit.components.v1')
    comp_v1.html = lambda *args, **kwargs: None
    components.v1 = comp_v1
    st.components = components
    location = Path(__file__).parents[1] / 'app' / 'interface.py'
    with patch.dict(sys.modules, {'streamlit': st, 'streamlit.components': components,
                                  'streamlit.components.v1': comp_v1}), \
         patch('requests.get', side_effect=fake_get):
        runpy.run_path(str(location), run_name='__v5_smoke__')
