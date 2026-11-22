"""Speech synthesis in the user's browser, without a Python TTS dependency.

The reader requires an explicit click. Browsers can block unattended playback.
Text is escaped before being embedded in the component's JavaScript.
"""
from __future__ import annotations

import json


def build_player_html(text: str, rate: float = 0.95) -> str:
    """Create a small, keyboard-accessible speech player (French preferred)."""
    if not isinstance(text, str):
        raise TypeError('La reponse doit etre du texte')
    message = text.strip()[:1800]
    if not message:
        raise ValueError('Aucune reponse a lire')
    rate = max(0.7, min(1.3, float(rate)))
    safe_message = (json.dumps(message, ensure_ascii=False)
                    .replace('<', '\\u003c').replace('>', '\\u003e')
                    .replace('&', '\\u0026')
                    .replace('\u2028', '\\u2028').replace('\u2029', '\\u2029'))
    return '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8" />
<style>
  html, body { margin: 0; padding: 0; font: 15px Arial, sans-serif; color: #18283b; background: transparent; }
  .reader { border: 1px solid #bfd8e3; background: #f2f9ff; border-radius: 12px; padding: 12px 14px; }
  .bar { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
  button { border: 2px solid #084f76; border-radius: 9px; background: #075b88; color: white;
           padding: 10px 15px; cursor: pointer; min-height: 44px; font-size: 15px; font-weight: 650; }
  button.stop { color: #183045; background: white; }
  button:focus-visible { outline: 3px solid #ffb000; outline-offset: 3px; }
  #status { margin: 8px 0 0; font-size: 13px; color: #34495e; min-height: 17px; }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style></head>
<body><section class="reader" aria-label="Lecture vocale de la réponse">
  <div class="bar">
    <button id="read" type="button" aria-label="Lire la réponse à voix haute">🔊 Lire la réponse</button>
    <button id="stop" type="button" class="stop" aria-label="Arrêter la lecture">■ Arrêter</button>
  </div>
  <p id="status" aria-live="polite">La lecture démarre en cliquant sur « Lire la réponse ».</p>
</section>
<script>
(() => {
  const message = SAFE_TEXT;
  const rate = SAFE_RATE;
  const synth = window.speechSynthesis;
  const status = document.getElementById('status');
  const read = document.getElementById('read');
  const stop = document.getElementById('stop');
  if (!synth || !window.SpeechSynthesisUtterance) {
    read.disabled = true;
    status.textContent = 'Synthèse vocale non disponible dans ce navigateur. Essayez Edge ou Chrome.';
    return;
  }
  read.addEventListener('click', () => {
    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = 'fr-FR';
    utterance.rate = rate;
    const voices = synth.getVoices();
    const french = voices.find(v => v.lang.toLowerCase() === 'fr-fr') ||
                   voices.find(v => v.lang.toLowerCase().startsWith('fr'));
    if (french) utterance.voice = french;
    utterance.onstart = () => { status.textContent = 'Lecture en cours…'; };
    utterance.onend = () => { status.textContent = 'Lecture terminée.'; };
    utterance.onerror = (event) => {
      if (event.error !== 'canceled' && event.error !== 'interrupted') {
        status.textContent = 'Lecture impossible : vérifiez le son ou la voix française de Windows.';
      }
    };
    synth.speak(utterance);
    status.textContent = 'Démarrage de la lecture…';
  });
  stop.addEventListener('click', () => {
    synth.cancel();
    status.textContent = 'Lecture arrêtée.';
  });
  window.addEventListener('pagehide', () => synth.cancel());
})();
</script></body></html>'''.replace('SAFE_TEXT', safe_message).replace('SAFE_RATE', repr(rate))
