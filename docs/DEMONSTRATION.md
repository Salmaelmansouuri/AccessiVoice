# Script de démonstration (3 à 5 minutes)

1. Expliquer le besoin d'accessibilité et préciser que les données sont fictives.
2. Ouvrir `http://127.0.0.1:8000/docs` et vérifier `/health`.
3. Ouvrir Streamlit. Entrer : « Quels services sont disponibles à Casablanca ? ».
4. Montrer la transcription textuelle, l'intention `rechercher_service`, la ville extraite et la liste renvoyée.
5. Entrer : « Je veux consulter mes informations. » ; montrer le profil fictif.
6. Entrer : « Je veux effectuer une demande. » ; montrer la référence fictive et l'historique.
7. Si Whisper a été installé et testé sur la machine, enregistrer la même commande avec le micro et illustrer toute la chaîne.
8. Afficher `models/metrics.json`, `python -m pytest -q`, puis discuter des limites.

**Avant l'oral :** tester micro, internet (si premier téléchargement Whisper), permissions navigateur, commandes réelles, vitesse de transcription et lisibilité de l'interface.
