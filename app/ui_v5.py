"""Petites fonctions de présentation V5, sans effets sur la base ou sur les API."""
from __future__ import annotations
from collections.abc import Mapping

PAGES = (
    '🏠 Tableau de bord',
    '🎙️ Assistant vocal',
    '🔎 Services',
    '🧾 Demandes',
    '👤 Profil fictif',
    '📜 Historique',
    '⚙️ Accessibilité',
)


def filter_services(services: list[dict], ville: str | None) -> list[dict]:
    """Filtre une liste locale de services; ne modifie pas la base."""
    if not ville or ville == 'Toutes les villes':
        return list(services)
    return [s for s in services if str(s.get('ville', '')).casefold() == ville.casefold()]


def available_cities(services: list[dict]) -> list[str]:
    return sorted({str(s.get('ville', '')).strip() for s in services if s.get('ville')})


def dashboard_counts(services: list[dict], demandes: list[dict], interactions: list[dict]) -> dict[str, int]:
    return {'services': len(services), 'demandes': len(demandes), 'interactions': len(interactions)}


def service_title(service: Mapping) -> str:
    return f"{service.get('nom', 'Service')} — {service.get('ville', 'Ville non précisée')}"


def response_meta(result: Mapping) -> tuple[str, float, str | None]:
    """Métadonnées robustes même quand un champ manque dans une ancienne réponse."""
    intent = str(result.get('intention') or 'non renseignée')
    try:
        confidence = max(0.0, min(1.0, float(result.get('confiance') or 0)))
    except (ValueError, TypeError):
        confidence = 0.0
    entities = result.get('entites') or {}
    city = entities.get('ville') if isinstance(entities, Mapping) else None
    return intent, confidence, city
