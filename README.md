# 🎙️ AccessiVoice

**Assistant vocal intelligent pour faciliter l’accès aux services numériques — prototype pédagogique local.**

AccessiVoice permet de formuler des demandes en français, **à la voix ou au clavier**, d’identifier leur intention et de consulter des services de démonstration. L'application peut également lire ses réponses à haute voix, enregistrer une demande fictive après confirmation et proposer un affichage plus accessible.

> **Démonstration uniquement.** Les services et les demandes sont fictifs : AccessiVoice n’est pas relié à un portail administratif réel. Ne saisissez pas d’informations personnelles réelles.

## Fonctionnalités

| Module | Fonction |
|---|---|
| Assistant vocal | Enregistrement au microphone, transcription locale avec `faster-whisper` et traitement de la demande |
| Assistant texte | Saisie d’une demande, classification de l’intention, réponse affichée |
| Recherche de services | Recherche et filtrage géographique, notamment « Casa Blanca » → Casablanca |
| Demandes | Sélection d’un service puis **confirmation explicite** avant enregistrement dans SQLite |
| Profil fictif | Consultation et modification d’un profil de démonstration |
| Réponse parlée | Lecture et arrêt de la réponse via la synthèse vocale du navigateur |
| Tableau de bord | Accès aux rubriques, indicateurs des éléments récents et raccourcis |
| Accessibilité | Texte agrandi, contraste renforcé, navigation clavier et vitesse de lecture ajustable |
| Historique | Consultation des interactions et des demandes fictives |

## Architecture

```text
Utilisateur (voix / clavier)
          │
          ▼
Interface Streamlit
          │
          ├── Voix → Whisper local (audio → texte)
          │
          ▼
API FastAPI
          │
          ├── NLP : TF-IDF (n-grammes de caractères) + régression logistique
          ├── Identification de l'intention et de la ville
          └── Routage des fonctionnalités
                       │
                       ▼
              Base SQLite fictive
                       │
                       ▼
              Réponse textuelle
                       │
                       └── Lecture vocale (Web Speech API du navigateur)
```

Le système traite **six intentions** : `rechercher_service`, `consulter_information`, `effectuer_action`, `modifier_information`, `aide` et `quitter`. Les actions d’écriture exigent une validation par l'utilisateur dans l'interface.

## Technologies

- **Python 3.12**, FastAPI, Uvicorn, Streamlit et Requests
- **scikit-learn**, TF-IDF, régression logistique et Joblib pour la classification
- **faster-whisper** pour la reconnaissance vocale locale (facultative)
- **SQLite** pour les services, le profil et les demandes fictives
- **Web Speech API** pour la lecture de la réponse dans le navigateur
- **Pytest** pour les vérifications automatisées
- Docker Compose pour l’exécution de l’API seule (optionnel)

## Démarrer l’application sur Windows

**Prérequis :** Python 3.11 ou 3.12 (3.12 recommandé), navigateur récent, connexion Internet lors de la première installation et du premier téléchargement du modèle vocal, microphone pour la saisie vocale.

1. Téléchargez ou clonez le dépôt.
2. Ouvrez le dossier du projet sur Windows.
3. Double-cliquez sur **`LANCER_ACCESSIVOICE.bat`**.
4. Laissez la fenêtre de lancement ouverte et utilisez l’adresse locale affichée (en général `http://127.0.0.1:8501`).
5. Pour arrêter les serveurs, utilisez `Ctrl+C` dans la fenêtre de lancement.

Le lanceur prépare un environnement virtuel, installe les dépendances requises, entraîne le modèle de classification si nécessaire, sélectionne des ports libres et démarre l'API ainsi que l'interface. Le premier démarrage peut être plus long en raison de l'installation initiale.

### Installation manuelle

Dans PowerShell, depuis le dossier du projet :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m scripts.train
```

Lancer l'API dans un premier terminal :

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Puis l'interface dans un deuxième terminal :

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/interface.py
```

Pour activer le mode vocal si vous utilisez l'installation manuelle :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-voice.txt
```

`requirements-voice.txt` fixe notamment la version de PyAV compatible avec la configuration audio utilisée. Le modèle Whisper est téléchargé au premier usage de la transcription puis exécuté localement. La reconnaissance et la synthèse vocales dépendent aussi du microphone, du navigateur et des voix système disponibles.

## Utilisation et démonstration

Essayez les commandes suivantes dans la rubrique **Assistant vocal** :

- « Quels services sont disponibles à Casa Blanca ? »
- « Je veux consulter mes informations. »
- « Je veux modifier mon profil. »
- « Je veux effectuer une demande. »
- « Comment utiliser cette application ? »

Pour les demandes, ouvrez la rubrique **Demandes**, choisissez un service, puis cliquez sur **Confirmer la demande fictive**. La demande apparaît ensuite dans l’historique. Pour une réponse sonore, cliquez sur **Lire la réponse** après l'affichage du résultat.

## Évaluation du modèle NLP

Le dataset `data/intents.csv` comporte **156 phrases pédagogiques** réparties en six intentions. Le protocole d'évaluation utilise un découpage stratifié avec 25 % des phrases réservées au test.

| Mesure | Résultat |
|---|---:|
| Phrases d’entraînement | 117 |
| Phrases de test | 39 |
| Accuracy | 74,36 % |
| Précision macro | 73,25 % |
| Rappel macro | 74,60 % |
| F1 macro | 72,40 % |

Les résultats, la matrice de confusion et les graphiques sont accessibles dans `models/metrics.json` et `docs/`. **Attention :** ces scores mesurent la classification sur un petit dataset construit pour la démonstration ; ils ne constituent pas une évaluation sur des utilisateurs réels.

Le modèle final est réentraîné sur la totalité du dataset et enregistré localement dans `models/intent_model.joblib` (exclu de Git).

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Les tests couvrent notamment l'API, le filtrage des villes, la gestion du profil et des demandes, les fonctions vocales et la navigation. **Ils ne remplacent pas une vérification manuelle du microphone et de la lecture audio.**

## API (documentation interactive)

Avec l'API démarrée, consultez `http://127.0.0.1:8000/docs` si le port 8000 est libre.

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/health` | État de l'API |
| GET | `/services` | Liste et filtre de services (`?ville=Casablanca`) |
| POST | `/predict-intent` | Classification de texte |
| POST | `/execute` | Traitement et réponse à une commande |
| POST | `/voice` | Transcription audio et traitement |
| GET | `/interactions` | Historique des interactions |
| GET / PATCH | `/profil-demo` | Consultation / modification du profil fictif |
| GET / POST | `/demandes` | Consultation / création de demandes fictives |

Exemple de commande PowerShell :

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/execute -Method Post -ContentType 'application/json' -Body '{"texte":"Quels services sont disponibles à Casablanca ?"}'
```

## Arborescence

```text
AccessiVoice/
├── app/                    # API, moteur NLP, interface et SQLite
├── data/intents.csv        # Données d'entraînement illustratives
├── docs/                   # Documentation et graphiques d'évaluation
├── models/                 # Métriques publiées ; modèle entraîné ignoré par Git
├── scripts/                # Entraînement et lanceur des deux serveurs
├── tests/                  # Tests automatisés
├── .gitignore
├── LANCER_ACCESSIVOICE.bat
├── DIAGNOSTIC_ACCESSIVOICE.bat
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── requirements-voice.txt
└── README.md
```

## Limites et confidentialité

Il s’agit d’un prototype local : le profil n'a pas d'authentification, la liste des villes et services est limitée, le dataset est réduit et les systèmes administratifs réels ne sont pas connectés. Le modèle vocal n'a pas fait l'objet d'une évaluation représentative et **aucune certification d'accessibilité** n'est revendiquée. Ne déployez pas cette version telle quelle sur un serveur public.

La base locale SQLite, les enregistrements éventuels, les journaux et l'environnement `.venv` ne doivent pas être publiés sur GitHub. Le fichier `.gitignore` écarte ces fichiers locaux ; vérifiez également les contenus avant chaque publication.

## Contributions

La répartition réelle des contributions à compléter pour la remise figure dans `docs/CONTRIBUTIONS.md`. Consultez aussi `docs/DEMONSTRATION.md` pour préparer la démonstration.
