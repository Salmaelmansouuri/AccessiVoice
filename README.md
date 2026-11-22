# 🎙 AccessiVoice

**Prototype pédagogique : accéder à un service numérique fictif en français, par la voix ou le texte.**

## Nouveauté V5 : tableau de bord et navigation simple

Cette version propose un tableau de bord, un accès direct aux fonctionnalités,
une rubrique pour chaque parcours (Assistant, Services, Demandes, Profil,
Historique, Accessibilité) et des réglages de contraste et de typographie
persistant pendant la session. La commande vocale et la lecture à haute voix
sont conservées. **La base SQLite, le modèle Whisper et le classifieur NLP
ne sont pas modifiés par la mise à jour V5.**

Voir [`AMELIORATIONS_V5.md`](AMELIORATIONS_V5.md) pour l'installation et les tests.

## Nouveauté V3 : actions concrètes, sans services réels

Le prototype permet maintenant de **consulter et modifier un profil fictif** et de **créer puis retrouver des demandes fictives** sur les services disponibles. Les commandes vocales ou écrites reconnaissent l'intention et invitent à utiliser le formulaire concerné ; **une confirmation par bouton est nécessaire pour enregistrer une demande**. Le moteur NLP ne déclenche plus automatiquement une écriture quand l'utilisateur dit « je veux effectuer une demande ».

La migration vers V3 conserve la base SQLite V2 et ajoute une colonne optionnelle à la table `demandes`. Aucun modèle Whisper n'est à réinstaller. Voir `AMELIORATIONS_V3.md`.

## Nouveauté V2 : filtrage des villes dictées

Les variantes entendues par Whisper, dont **« Casa Blanca »**, **« Casa-Blanca »** et **« Casa »**, sont reconnues comme **Casablanca**. Une recherche de services à Casablanca ne renvoie plus les services des autres villes. L’interface indique aussi l’intention et la ville détectées après une commande vocale. Voir `AMELIORATIONS_V2.md`.

## Fonctionnement

`Micro / champ texte → Speech-to-Text (optionnel) → TF-IDF + régression logistique → intention + ville → moteur de traitement → SQLite → réponse`

L'application utilise 6 intentions (`rechercher_service`, `consulter_information`, `effectuer_action`, `modifier_information`, `aide`, `quitter`), un dataset CSV illustratif, une API FastAPI et une interface Streamlit. La reconnaissance audio repose sur **faster-whisper en option**. Les services, profils et demandes sont **entièrement fictifs**.

## Démarrage automatique sur Windows (recommandé)

**Double-cliquer sur `LANCER_ACCESSIVOICE.bat`** depuis un dossier extrait sur le Bureau. Le script crée un environnement Python **indépendant dans son propre dossier** (sans mélanger les anciennes installations), installe les dépendances manquantes si nécessaire, démarre l'API et Streamlit ensemble, choisit des ports libres et ouvre le navigateur automatiquement. **Garder la fenêtre noire ouverte** pendant l'utilisation ; `Ctrl+C` l'arrête proprement.

Cette méthode évite l'erreur `HTTPConnectionPool(... port=8000): Connection refused`, causée par une interface Streamlit ouverte sans API en cours d'exécution. L'API peut s'ouvrir sur un autre port si le port 8000 est occupé, grâce à la variable d'environnement `ACCESSIVOICE_API_URL` propagée automatiquement au client.

**Correction principale de cette version :** le WAV produit par le microphone de Streamlit est décodé en Python en PCM 16 kHz mono, puis envoyé à Whisper sous forme de tableau NumPy. Cela contourne entièrement le bug `metadata_errors` de PyAV 19 pour la voix enregistrée dans l'interface. Pour les autres formats audio, PyAV 18.1.0 reste verrouillé.

Si la reconnaissance vocale échoue, le message d'erreur détaillé est affiché par l'interface et dans `logs/api.log`. Le premier essai peut nécessiter le téléchargement du modèle `tiny` et Internet. La version de PyAV est bloquée à `18.1.0` pour éviter l’erreur `open() got an unexpected keyword argument metadata_errors` due à une incompatibilité avec PyAV 19. Le mode texte fonctionne même si la fonctionnalité vocale est indisponible.

## Prérequis

Python 3.11 ou 3.12 (recommandé : 3.12), connexion Internet pour l'installation et le premier téléchargement du modèle vocal, micro fonctionnel pour le mode voix.

### 1. Installation (PowerShell Windows)

```powershell
cd AccessiVoice
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Sur Linux/macOS : `python3 -m venv .venv && source .venv/bin/activate`.

### 2. Entraînement reproductible

```powershell
python -m scripts.train
```

Le script crée `models/intent_model.joblib` et `models/metrics.json` avec les résultats **réellement mesurés** sur un split stratifié (25 % test). Ces fichiers sont générés localement, pas nécessaires dans le dépôt Git.

### 3. Démarrer l'API (terminal n°1)

```powershell
uvicorn app.main:app --reload
```

Ouvrir la documentation interactive : http://127.0.0.1:8000/docs ; santé : http://127.0.0.1:8000/health.

### 4. Démarrer l'interface (terminal n°2)

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app/interface.py
```

Ouvrir l'adresse locale affichée par Streamlit (en général http://localhost:8501).

### 5. Activer le mode voix (facultatif)

```powershell
pip install -r requirements-voice.txt
```

Si une installation précédente utilisait PyAV 19 et que tu obtiens l’erreur `metadata_errors`, le lanceur Windows corrige automatiquement cette incompatibilité, même si `faster-whisper` est déjà présent. Pour une correction manuelle sur le Python du projet : `python -m pip install "av==18.1.0"`, puis redémarrer FastAPI et Streamlit.

Le premier appel audio télécharge le petit modèle Whisper `tiny` (variable `ACCESSIVOICE_WHISPER_MODEL=base` pour plus de précision). Pour éviter de transmettre des enregistrements à un service externe, la transcription est réalisée **localement** après téléchargement. Les fichiers temporaires sont supprimés après usage. La fonctionnalité dépend des permissions microphone et des bibliothèques audio sur la machine ; elle doit être validée lors de la démonstration finale.

## API

| Route | Fonction |
|---|---|
| `GET /health` | Statut de l'API |
| `GET /services?ville=Casablanca` | Liste des services fictifs disponibles |
| `POST /predict-intent` | Classe une phrase (`{"texte":"Quels services proposez-vous ?"}`) |
| `POST /execute` | Analyse la demande, recherche les services et propose les actions explicites |
| `POST /voice` | Audio vers texte puis action (option Whisper) |
| `GET /interactions` | Historique des commandes de démonstration |
| `GET /profil-demo` | Consulter le profil fictif |
| `PATCH /profil-demo` | Modifier le profil fictif |
| `GET /demandes` | Liste des demandes fictives enregistrées |
| `POST /demandes` | Enregistrer une demande fictive pour `service_id` après confirmation de l’utilisateur |

Exemple :

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/execute -Method Post -ContentType 'application/json' -Body '{"texte":"Quels services sont disponibles à Casablanca ?"}'
```

## Tests

```powershell
python -m pytest -q
```

Tests : migration V2, profil fictif, confirmation des demandes, santé API, liste et filtre des services, classification, exécution, historique, validation des entrées et formats audio invalides. Les tests ne remplacent **pas** une validation de reconnaissance vocale avec un vrai microphone.

## Données et IA

- `data/intents.csv` : phrases françaises d'apprentissage, créées pour ce prototype, et leurs intentions.
- `scripts/train.py` : pipeline TF-IDF de n-grammes de caractères + régression logistique, découpage stratifié, accuracy, précision macro, rappel macro, F1 macro et matrice de confusion.
- `app/engine.py` : repérage d'une ville parmi Casablanca / Rabat / Marrakech et routage vers les actions de démonstration.
- Base SQLite créée automatiquement au démarrage (services et profil fictifs).

**Limites :** dataset petit et artificiel ; reconnaissance des villes limitée ; faux profil sans authentification ; pas de connexion à un service réel ; modèle vocal non évalué sur un jeu audio représentatif ; aucune promesse d'accessibilité certifiée. Ce prototype ne doit **pas** être exposé en production en l'état.

## Déploiement Docker (API uniquement)

```powershell
docker compose up --build
```

Attention : le conteneur n'active pas `faster-whisper` ; l'interface Streamlit se lance séparément dans l'environnement Python local. Le port API est limité à la machine locale dans `compose.yaml`.

## Structure

```text
AccessiVoice/
├─ app/                 # API FastAPI, classifieur, routage, Streamlit, SQLite
├─ data/intents.csv     # Dataset pédagogique français
├─ models/              # Modèle et métriques générés localement
├─ scripts/train.py     # Entraînement / évaluation
├─ scripts/launch.py    # Démarre et surveille les deux serveurs
├─ LANCER_ACCESSIVOICE.bat # Double clic Windows
├─ DEMARRE_ICI.txt      # Instructions de lancement
├─ tests/               # Tests automatisés Pytest
├─ docs/                # Notes de soutenance et vérifications
├─ Dockerfile
├─ compose.yaml
├─ requirements.txt
├─ requirements-voice.txt
└─ README.md
```

## Publication GitHub

```powershell
git init
git add .
git commit -m "Prototype initial AccessiVoice"
git branch -M main
git remote add origin https://github.com/VOTRE-IDENTIFIANT/AccessiVoice.git
git push -u origin main
```

Créez au préalable le dépôt vide sur GitHub et remplacez `VOTRE-IDENTIFIANT`. N'ajoutez pas de données utilisateur réelles, de fichiers `.env` ou d'audios personnels au dépôt.

## Référence et contributions

Projet basé sur le document fourni « Cahier des charges AccessiVoice », sections 1 à 19. Les technologies proposées par ce document sont indicatives et non imposées. Renseigner les contributions effectives avant remise (ne pas attribuer des tâches non réalisées) ; voir `docs/CONTRIBUTIONS.md`.

## V4 — Réponse orale et accessibilité

La V4 ajoute un lecteur de réponse en français via la synthèse vocale du navigateur (API Web Speech, sans nouvelle dépendance Python). Après une requête texte ou microphone, cliquer sur **🔊 Lire la réponse** pour l'entendre, puis sur **■ Arrêter** si nécessaire. Le lecteur apparaît aussi après une modification du profil fictif ou l'enregistrement d'une demande fictive.

Ouvrir **⚙️ Options d’accessibilité** pour agrandir la typographie et les boutons, augmenter le contraste ou régler la vitesse de lecture. La lecture démarre après un clic, car la lecture automatique n'est pas toujours autorisée. Elle nécessite un navigateur compatible et une voix du système (de préférence en français). Voir `AMELIORATIONS_V4.md`.
