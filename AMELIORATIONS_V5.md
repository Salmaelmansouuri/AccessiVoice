# AccessiVoice V5 — Tableau de bord et navigation accessible

## Objectif

Cette version améliore l'expérience d'utilisation, sans modifier les routes FastAPI,
le moteur NLP, la base SQLite, les données existantes ou le fonctionnement de Whisper.

## Nouveautés

- **Tableau de bord :** accès rapide à l'assistant, au catalogue et aux demandes.
  Les compteurs correspondent aux éléments récemment renvoyés par l'API, et non
  à des mesures historiques exhaustives.
- **Navigation par rubriques :** Accueil, Assistant vocal, Services, Demandes,
  Profil fictif, Historique, Accessibilité.
- **Catalogue filtrable par ville :** sélection Casablanca, Rabat, Marrakech,
  selon la liste des services actuellement disponibles.
- **Formulaire de demande fictive :** filtre par ville, confirmation explicite
  avant insertion, historique consultable.
- **Accessibilité :** texte agrandi, contraste renforcé, contrôles accessibles
  au clavier, options de lecture à vitesse réglable, indication du mode démo.
- **Voix :** transcription Whisper et lecture des réponses dans le navigateur
  (via les boutons Lire la réponse et Arrêter) inchangées.

## Mise à jour depuis la V4 Windows

1. Arrêter le lanceur AccessiVoice avec `Ctrl + C`.
2. Extraire `AccessiVoice_MAJ_V5_Dashboard.zip`.
3. Lancer `APPLIQUER_V5.bat` et confirmer avec `O`.
4. Relancer `LANCER_ACCESSIVOICE.bat` dans `AccessiVoice_FINAL_CORRIGE`.

La mise à jour fait une sauvegarde de l'ancienne interface et du README
avant de les remplacer. La base `data/accessivoice.sqlite3`, le modèle
`models/intent_model.joblib`, `.venv`, `app/tts.py`, `app/main.py`, et
les scripts du lanceur restent **inchangés**.

Le script prend en charge les dossiers Windows habituels Bureau / Desktop,
avec ou sans OneDrive. Si votre dossier est ailleurs, vous pouvez le faire
glisser sur le fichier `APPLIQUER_V5.bat` (chemin transmis en argument).

## Essais recommandés

1. Tableau de bord → **Ouvrir l'assistant**.
2. Assistant vocal → dire « Quels services sont disponibles à Casa Blanca ? ».
3. Vérifier qu'il répond avec les services de Casablanca, puis cliquer **Lire la réponse**.
4. Cliquer **Voir les services correspondants** pour vérifier le filtrage.
5. Ouvrir **Demandes**, choisir un service et **Confirmer la demande fictive**.
6. Vérifier l'historique, puis régler taille du texte / contraste dans la barre latérale.

## Tests automatisés

`python -m pytest -q` — tests de non-régression, logique de navigation,
helpers d'affichage et simulation Python des sept écrans Streamlit.

Les tests simulés ne valident pas l'affichage dans un navigateur réel,
la qualité de Whisper, la disponibilité de voix françaises installées,
ni la conformité aux normes WCAG. Ces points exigent des vérifications
sur un poste utilisateur.

## Sécurité et limites

L'application manipule une base et des utilisateurs fictifs ; aucune
connexion à un service administratif réel. Ne pas publier ce prototype
avec son API exposée à Internet ou y mettre des données personnelles.
