"""Dispatch recognized intent to bounded demo actions, including spoken city variants."""
from __future__ import annotations
import re
from .database import list_services, demo_user, add_interaction
from .nlp import predict, normalize

# Whisper may write the SAME city as "Casablanca", "Casa Blanca" or "Casa".
# Match word boundaries to avoid accidentally recognizing a city in another word.
CITY_PATTERNS = (
    ("Casablanca", (r"\bcasa[\s-]*blan[ck]a\b", r"\bcasa\b")),
    ("Rabat", (r"\brabat\b",)),
    ("Marrakech", (r"\bmarrake(?:ch|sh)\b", r"\bmarrakech\b")),
)
SUPPORTED_CITIES = {"casablanca": "Casablanca", "rabat": "Rabat", "marrakech": "Marrakech"}


def extract_entities(text: str) -> dict[str, str | None]:
    """Resolve canonical city names from written or imperfect spoken French."""
    normalized = normalize(text)
    hits = []
    for city, patterns in CITY_PATTERNS:
        positions = [m.start() for pattern in patterns if (m := re.search(pattern, normalized))]
        if positions:
            hits.append((min(positions), city))
    hits.sort()
    return {"ville": hits[0][1] if hits else None}


def execute(text: str):
    result = predict(text)
    intent = result['intention']
    entities = extract_entities(text)
    confidence = result['confiance']
    info = {}
    action_proposee = None
    if confidence < 0.30:
        intent = 'inconnue'
        response = "Je n'ai pas compris la demande. Essayez une phrase plus précise ou demandez de l'aide."
    elif intent == 'rechercher_service':
        city = entities['ville']
        services = list_services(city)
        info['services'] = services
        if services:
            if city:
                response = f"Services disponibles à {city} : " + '; '.join(s['nom'] for s in services) + '.'
            else:
                response = 'Services disponibles (toutes les villes) : ' + '; '.join(f"{s['nom']} ({s['ville']})" for s in services) + '.'
        else:
            response = f"Aucun service disponible à {city} pour le moment." if city else "Aucun service disponible pour le moment."
    elif intent == 'consulter_information':
        user = demo_user()
        info['profil_demo'] = user
        action_proposee = 'consulter_profil'
        response = f"Profil de démonstration : {user['prenom']} {user['nom']}. Adresse : {user['email']}." if user else 'Aucun profil de démonstration.'
    elif intent == 'effectuer_action':
        action_proposee = 'creer_demande'
        info['services'] = list_services(entities['ville'])
        response = "Je peux préparer une demande fictive. Choisissez un service dans « Demandes de service » puis confirmez son enregistrement."
    elif intent == 'modifier_information':
        action_proposee = 'modifier_profil'
        response = "Pour modifier le profil fictif, ouvrez « Profil de démonstration » et enregistrez vos changements. Aucun vrai compte n'est modifié."
    elif intent == 'aide':
        response = "Vous pouvez chercher des services par ville, consulter ou modifier le profil fictif et préparer une demande de service. Les enregistrements nécessitent un clic de confirmation."
    elif intent == 'quitter':
        response = 'À bientôt ! Vous pouvez fermer cet onglet.'
    else:
        response = "Demande non prise en charge. Essayez : 'Quels services sont disponibles à Casablanca ?'"
    add_interaction(text, intent, response)
    return {'texte': text, 'intention': intent, 'confiance': confidence, 'entites': entities, 'reponse': response, 'donnees': info, 'action_proposee': action_proposee}
