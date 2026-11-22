"""Launch the local AccessiVoice API + UI together and stop both on exit.

Use via LANCER_ACCESSIVOICE.bat on Windows, or `python scripts/launch.py`.
No admin rights, no network ports exposed beyond the local machine.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'logs'
LOGS.mkdir(exist_ok=True)
PYTHON = Path(sys.executable)


def available(port: int) -> bool:
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            return False
        return True


def choose(start: int, end: int) -> int:
    for port in range(start, end):
        if available(port):
            return port
    raise RuntimeError(f'Aucun port libre entre {start} et {end - 1}')


def ready(url: str, proc: subprocess.Popen, seconds: float = 45.0) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
            pass
        time.sleep(0.45)
    return False


def tail(filename: Path, lines: int = 35) -> None:
    if filename.exists():
        print(f'\n--- Fichier diagnostic: {filename} ---')
        for line in filename.read_text(encoding='utf-8', errors='replace').splitlines()[-lines:]:
            print(line)


def run() -> int:
    print('\n=== ACCESSIVOICE | DEMARRAGE AUTOMATIQUE ===\n', flush=True)
    model_file = ROOT / 'models' / 'intent_model.joblib'
    if not model_file.exists():
        print('[1/3] Entrainement du modele de texte ...', flush=True)
        result = subprocess.run([str(PYTHON), '-m', 'scripts.train'], cwd=ROOT)
        if result.returncode:
            return result.returncode
    else:
        print('[1/3] Modele de texte pret.', flush=True)

    api_port = choose(8000, 8050)
    ui_port = choose(8501, 8550)
    api_url = f'http://127.0.0.1:{api_port}'
    ui_url = f'http://127.0.0.1:{ui_port}'
    env = os.environ.copy()
    env['ACCESSIVOICE_API_URL'] = api_url
    env['PYTHONUNBUFFERED'] = '1'
    # Each launch owns only its child processes. Avoid --reload, which would spawn a third process.
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    api_log = LOGS / 'api.log'
    ui_log = LOGS / 'interface.log'
    processes: list[subprocess.Popen] = []
    try:
        with api_log.open('w', encoding='utf-8') as api_out, ui_log.open('w', encoding='utf-8') as ui_out:
            print(f'[2/3] Demarrage API sur {api_url} ...', flush=True)
            api = subprocess.Popen(
                [str(PYTHON), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(api_port)],
                cwd=ROOT, env=env, stdout=api_out, stderr=subprocess.STDOUT,
                creationflags=flags,
            )
            processes.append(api)
            if not ready(api_url + '/health', api):
                print('ERREUR : le backend ne demarre pas. Voir ci-dessous.', flush=True)
                tail(api_log)
                return 1
            print('      API OK !', flush=True)
            print(f'[3/3] Demarrage interface sur {ui_url} ...', flush=True)
            ui = subprocess.Popen(
                [str(PYTHON), '-m', 'streamlit', 'run', 'app/interface.py',
                 '--server.address', '127.0.0.1', '--server.port', str(ui_port),
                 '--server.headless', 'true', '--browser.gatherUsageStats', 'false'],
                cwd=ROOT, env=env, stdout=ui_out, stderr=subprocess.STDOUT,
                creationflags=flags,
            )
            processes.append(ui)
            if not ready(ui_url + '/_stcore/health', ui):
                print('ERREUR : interface non demarree. Voir ci-dessous.', flush=True)
                tail(ui_log)
                return 1
            print('\nACCESSIVOICE EST PRET !')
            print(f'Interface : {ui_url}')
            print(f'API       : {api_url}/docs')
            print('Pour tout arreter : Ctrl+C dans cette fenetre.\n', flush=True)
            webbrowser.open(ui_url)
            while api.poll() is None and ui.poll() is None:
                time.sleep(0.7)
            print('Un des serveurs s\'est arrete. Derniers journaux :')
            tail(api_log, 15)
            tail(ui_log, 15)
            return 1
    except KeyboardInterrupt:
        print('\nArret des services ...', flush=True)
        return 0
    finally:
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
        for proc in reversed(processes):
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        print('Services AccessiVoice arretes.', flush=True)


if __name__ == '__main__':
    sys.exit(run())
