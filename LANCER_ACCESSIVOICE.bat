@echo off
setlocal EnableExtensions
chcp 65001 >nul
title AccessiVoice FINAL - Interface et API
cd /d "%~dp0"
echo.
echo  ACCESSIVOICE - VERSION CORRIGEE
 echo  ===================================
echo.
set "PY_RUN=.venv\Scripts\python.exe"
if not exist "%PY_RUN%" (
    echo [1/4] Creation d'un environnement propre dans CE dossier...
    py -3.12 -m venv .venv
    if errorlevel 1 (
        echo ECHEC : Python 3.12 est requis : py -3.12 --version
        pause
        exit /b 1
    )
)
"%PY_RUN%" -c "import fastapi, streamlit, sklearn, uvicorn, joblib, requests, scipy, numpy" >nul 2>&1
if errorlevel 1 (
    echo [2/4] Installation des bibliotheques du projet...
    "%PY_RUN%" -m pip install --prefer-binary -r requirements.txt
    if errorlevel 1 (
        echo ERREUR : impossible d'installer les dependances. Connexion Internet requise.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Bibliotheques de base OK.
)
"%PY_RUN%" -c "import importlib.metadata as m; from faster_whisper import WhisperModel; assert m.version('av') == '18.1.0', 'PyAV incompatible'" >nul 2>&1
if errorlevel 1 (
    echo [3/4] Installation de la voix compatible : faster-whisper + PyAV 18...
    "%PY_RUN%" -m pip install --prefer-binary -r requirements-voice.txt
    if errorlevel 1 (
        echo [AVERTISSEMENT] Whisper indisponible. Le mode texte fonctionnera.
        echo Verifier la connexion Internet puis relancer ce fichier.
    )
) else (
    echo [3/4] Whisper et PyAV compatibles OK.
)
echo [4/4] Demarrage des deux serveurs sur des ports libres...
"%PY_RUN%" scripts\launch.py
if errorlevel 1 (
    echo.
    echo ECHEC : consulter les fichiers logs\api.log et logs\interface.log.
    pause
)
endlocal
