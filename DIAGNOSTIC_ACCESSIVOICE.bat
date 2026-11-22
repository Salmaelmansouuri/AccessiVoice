@echo off
setlocal
cd /d "%~dp0"
set "OUT=DIAGNOSTIC.txt"
>"%OUT%" echo ===== ACCESSIVOICE : DIAGNOSTIC =====
>>"%OUT%" echo Version : WAV direct, PyAV 18.1.0
if exist ".venv\Scripts\python.exe" (
  >>"%OUT%" ".venv\Scripts\python.exe" -c "import sys, importlib.metadata as m; print('Python:',sys.version); print('faster-whisper:',m.version('faster-whisper')); print('PyAV:',m.version('av')); print('NumPy:',m.version('numpy'))"
) else (
  >>"%OUT%" echo Environnement .venv absent.
)
>>"%OUT%" echo.
>>"%OUT%" echo ===== LOGS BACKEND =====
if exist "logs\api.log" (
  powershell -NoProfile -Command "Get-Content -Path 'logs\api.log' -Tail 80" >>"%OUT%"
) else (
  >>"%OUT%" echo Aucun fichier logs/api.log disponible.
)
echo Diagnostic cree: %CD%\%OUT%
echo Tu peux envoyer ce fichier si le test vocal echoue encore.
pause
endlocal
