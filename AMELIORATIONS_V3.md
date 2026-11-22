# AccessiVoice V3 — actions concrètes sur un service numérique fictif

## Ajouts à la V2

- **Consulter le profil fictif** depuis l'interface et `GET /profil-demo`.
- **Modifier le profil fictif** (nom, prénom et adresse de test) via `PATCH /profil-demo`. Les données sont validées côté API, puis conservées dans SQLite.
- **Créer une demande fictive** pour un service disponible, après clic explicite sur **Confirmer la demande fictive**, via `POST /demandes`.
- **Suivre les demandes** avec `GET /demandes`.
- Les commandes vocales « consulter mes informations », « modifier mon profil » et « effectuer une demande » affichent des indications et orientent vers les formulaires. **La voix seule n'enregistre pas de nouvelle demande ni ne modifie un profil.**
- La V2 est préservée : Whisper local (WAV direct), classifier existant, variantes « Casa Blanca », filtre par ville, historique.

## Données et sécurité

La base locale est une **démonstration**, sans authentification ni connexion à une administration. Elle contient des données fictives. **Ne jamais y saisir de vrais noms, adresses personnelles ou demandes sensibles.** Elle n'est pas destinée à une mise en ligne publique.

La migration `init_db()` ajoute la colonne optionnelle `service_id` aux anciennes bases V2, sans effacer les enregistrements. L'installateur de correctif effectue une sauvegarde des fichiers sources et de la base SQLite, si elle existe.

## Démo rapide

1. Demander oralement « Quels services sont disponibles à Casa Blanca ? » : seulement les services de Casablanca.
2. Dire « Je veux consulter mes informations » : l'application présente le profil fictif.
3. Dire « Je veux modifier mon profil » : ouvrir **Profil de démonstration**, changer des valeurs fictives puis **Enregistrer**.
4. Dire « Je veux effectuer une demande » : ouvrir **Demandes de service**, sélectionner « Aide administrative — Casablanca », puis **Confirmer la demande fictive**.
5. Vérifier que la demande apparaît dans l'historique des demandes.

## Validation

42 tests automatisés Pytest ont réussi dans l'environnement de développement, y compris la migration V2, les validations, la création de demandes, la conservation du filtrage par ville et les tests du contrat de transcription audio simulée. La V3 **n'a pas encore été testée sur le PC de l'utilisateur** : une vérification manuelle de l'interface est requise après application du correctif.

## Installation sans réinstallation

Arrêter AccessiVoice (`Ctrl+C` dans son lanceur). Extraire **tout** `AccessiVoice_MAJ_V3_Actions.zip`, puis double-cliquer sur `APPLIQUER_V3.bat`. Les fichiers Python modifiés sont copiés dans `AccessiVoice_FINAL_CORRIGE` ; l'environnement `.venv`, les modèles `.joblib` et les données existantes sont conservés. Relancer le lanceur habituel du projet.
