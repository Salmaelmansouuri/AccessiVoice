# AccessiVoice V4 — Synthèse vocale et accessibilité

## Nouveautés

- Lecture à voix haute de la dernière réponse (français privilégié) grâce à la fonction `speechSynthesis` du navigateur.
- Boutons **🔊 Lire la réponse** et **■ Arrêter** dans la zone de réponse, visibles après une commande textuelle ou vocale.
- Lecture possible de la confirmation de modification du profil fictif et d'enregistrement de demande fictive.
- Options d'accessibilité : textes agrandis, boutons plus grands, contraste renforcé, vitesse de lecture ajustable.
- Navigation clavier : utilisez Tab, Entrée ou Espace selon le contrôle. Statut de lecture annoncé aux lecteurs d'écran.

## Aucune réinstallation

La V4 ne modifie ni `app/main.py`, ni `app/engine.py`, ni `app/database.py`, ni `app/voice_audio.py`.
Elle conserve l'environnement `.venv`, Whisper, le modèle de classification, le filtre Casablanca et la base SQLite existante.
Elle ne nécessite aucune nouvelle bibliothèque Python.

## Comment tester

1. Arrêter le lanceur Windows (Ctrl+C) et appliquer `APPLIQUER_V4.bat` extrait du ZIP.
2. Relancer `LANCER_ACCESSIVOICE.bat` depuis `AccessiVoice_FINAL_CORRIGE`.
3. Donner la commande « Quels services sont disponibles à Casa Blanca ? ».
4. Après la réponse textuelle, cliquer sur **🔊 Lire la réponse**. Le navigateur doit prononcer la liste des services à Casablanca.
5. Cliquer sur **■ Arrêter** pour interrompre la lecture.
6. Ouvrir « ⚙️ Options d’accessibilité », activer les grands textes et le contraste, ajuster la vitesse, et refaire le test.
7. Vérifier que les écrans V3 de profil et de demandes continuent de fonctionner.

## Limites et vérification

La voix repose sur la synthèse vocale du **navigateur** et sur les voix disponibles sous Windows. Le clic sur Lire est volontaire : la lecture automatique peut être bloquée par les navigateurs. Si aucune voix française n'est installée, la prononciation peut être incorrecte ou la lecture indisponible. Dans ce cas, essayer Edge/Chrome et activer une voix française dans les paramètres de Windows.

La V4 a été contrôlée par des tests automatisés Python ; une vérification manuelle du son sur Windows est nécessaire.

Le prototype n'envoie pas de requête à des services administratifs réels. Éviter toute donnée personnelle réelle.
