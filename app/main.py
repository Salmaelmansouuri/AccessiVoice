"""FastAPI for AccessiVoice (local educational demonstration)."""
from __future__ import annotations
import os
import tempfile
import logging
from functools import lru_cache
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field, field_validator
from .database import (init_db, list_services, recent_interactions, demo_user,
                       update_demo_user, create_service_request, list_requests)
from .nlp import predict
from .engine import execute
from .voice_audio import pcm_wav_to_whisper

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

logger = logging.getLogger('uvicorn.error')


@lru_cache(maxsize=1)
def local_whisper_model(model_name: str):
    # Charge une seule fois le modele pour eviter un telechargement a chaque requete.
    from faster_whisper import WhisperModel
    return WhisperModel(model_name, device='cpu', compute_type='int8')


app = FastAPI(title='AccessiVoice API', version='0.3.0', lifespan=lifespan,
              description='Prototype de commande vocale vers service numérique fictif.')

class Phrase(BaseModel):
    texte: str = Field(min_length=1, max_length=500)

@app.get('/health')
def health():
    return {'statut': 'ok', 'mode': 'démo locale', 'version': 'v3-actions-fictives'}

@app.get('/services')
def services(ville: str | None = None):
    if ville is not None and len(ville) > 80:
        raise HTTPException(422, 'Ville trop longue')
    return {'services': list_services(ville)}

@app.get('/interactions')
def interactions(limit: int = 10):
    return {'interactions': recent_interactions(limit)}

@app.post('/predict-intent')
def predict_intent(body: Phrase):
    return predict(body.texte)

@app.post('/execute')
def run_action(body: Phrase):
    return execute(body.texte)

class DemoProfileChange(BaseModel):
    nom: str = Field(min_length=1, max_length=70)
    prenom: str = Field(min_length=1, max_length=70)
    email: str = Field(min_length=5, max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @field_validator('nom', 'prenom', 'email')
    @classmethod
    def clean(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('Le champ ne peut pas être vide')
        return value


class DemoServiceRequest(BaseModel):
    service_id: int = Field(gt=0)


@app.get('/profil-demo')
def read_profile():
    """Profil fictif unique. Ne jamais utiliser avec de vraies données personnelles."""
    return {'profil': demo_user(), 'mode': 'demo'}


@app.patch('/profil-demo')
def change_profile(body: DemoProfileChange):
    try:
        user = update_demo_user(nom=body.nom, prenom=body.prenom, email=body.email)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {'profil': user, 'message': 'Profil fictif mis à jour.'}


@app.get('/demandes')
def read_requests(limit: int = 20):
    return {'demandes': list_requests(limit), 'mode': 'demo'}


@app.post('/demandes', status_code=201)
def submit_demo_request(body: DemoServiceRequest):
    """Nécessite une confirmation explicite dans l'interface; le NLP ne crée rien seul."""
    try:
        request = create_service_request(body.service_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return {'demande': request, 'message': 'Demande fictive enregistrée.'}


@app.post('/voice')
async def voice(file: UploadFile = File(...)):
    """Optional local speech recognition; requires requirements-voice.txt, first model download."""
    allowed = {'.wav', '.mp3', '.m4a', '.ogg', '.webm'}
    ext = Path(file.filename or 'audio.wav').suffix.lower()
    if ext not in allowed:
        raise HTTPException(415, 'Format audio non pris en charge.')
    data = await file.read(10 * 1024 * 1024 + 1)
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(413, 'Taille audio maximale : 10 Mo.')
    if not data:
        raise HTTPException(422, 'Fichier audio vide.')
    try:
        from faster_whisper import WhisperModel  # noqa: F401
    except (ImportError, OSError) as exc:
        logger.exception('Import de faster-whisper impossible')
        raise HTTPException(503, f'Bibliotheque vocale non chargee ({type(exc).__name__}). Voir logs/api.log') from exc
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as handle:
            handle.write(data)
            tmp = handle.name
        model = local_whisper_model(os.getenv('ACCESSIVOICE_WHISPER_MODEL', 'tiny'))
        # Browser audio (st.audio_input) is PCM WAV; decoding it ourselves
        # avoids the PyAV metadata_errors incompatibility entirely.
        audio_input = tmp
        if ext == '.wav':
            try:
                audio_input = pcm_wav_to_whisper(data)
                logger.info('Decodage WAV PCM direct, sans PyAV: %s echantillons', len(audio_input))
            except (ValueError, EOFError, OSError) as exc:
                logger.warning('WAV PCM non standard, utilisation decodeur PyAV: %s', exc)
            except Exception as exc:
                # wave.Error is an Exception, subclass of EOFError in some versions.
                import wave
                if not isinstance(exc, wave.Error):
                    raise
                logger.warning('WAV non standard, utilisation decodeur PyAV: %s', exc)
        segments, _ = model.transcribe(audio_input, language='fr')
        transcript = ' '.join(segment.text.strip() for segment in segments).strip()
        if not transcript:
            raise HTTPException(422, 'Parole non reconnue. Réessayez dans un endroit calme.')
        return execute(transcript)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception('Echec de la transcription vocale')
        # Demo locale uniquement. Fournir une cause actionnable au lieu d'un message opaque.
        details = str(exc).replace('\n', ' ')[:240]
        raise HTTPException(503, f'Whisper : {type(exc).__name__}: {details}. Details dans logs/api.log') from exc
    finally:
        if tmp:
            Path(tmp).unlink(missing_ok=True)
