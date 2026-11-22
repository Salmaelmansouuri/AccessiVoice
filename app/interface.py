"""AccessiVoice : tableau de bord, navigation accessible, voix, profil et demandes fictives.

Aucune API ou schema de base n'est change. Les commandes vocales restent locales et
les operations qui ecrivent en base necessitent toujours une confirmation explicite.
"""
from __future__ import annotations
import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from app.tts import build_player_html
from app.ui_v5 import PAGES, filter_services, available_cities, dashboard_counts, service_title, response_meta

API = os.getenv('ACCESSIVOICE_API_URL', 'http://127.0.0.1:8000').rstrip('/')
st.set_page_config(page_title='AccessiVoice', page_icon='🎙️', layout='wide', initial_sidebar_state='expanded')

# Toutes ces variables sont locales a la session du navigateur.
DEFAULTS = {
    'av_nav_v5': PAGES[0],
    'large_text_access': False,
    'high_contrast_access': False,
    'speech_rate_access': 0.95,
    'av_service_city': 'Toutes les villes',
    'av_requests_city': 'Toutes les villes',
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def api_get(route: str, timeout: int = 6):
    response = requests.get(API + route, timeout=timeout)
    response.raise_for_status()
    return response.json()


def api_post(route: str, payload: dict, timeout: int = 20):
    response = requests.post(API + route, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def navigate(page: str, city: str | None = None):
    """Navigation via rappel utilisateur, jamais une execution automatique d'action."""
    st.session_state['av_nav_v5'] = page
    if city:
        st.session_state['av_service_city'] = city
        st.session_state['av_requests_city'] = city


def show_result(data: dict):
    st.session_state['last_result'] = data


def speak_answer(message: str):
    # La lecture ne demarre que lorsque l'utilisateur clique sur Lire la reponse.
    if isinstance(message, str) and message.strip():
        components.html(build_player_html(message, st.session_state['speech_rate_access']),
                        height=130, scrolling=False)


def apply_accessibility_styles():
    large = st.session_state['large_text_access']
    contrast = st.session_state['high_contrast_access']
    css = '''
    <style>
      .block-container { max-width: 1320px; padding-top: 1.5rem; padding-bottom: 3rem; }
      .av-kicker { text-transform: uppercase; font-size: .8rem; font-weight: 700;
                   letter-spacing: .13em; color: #147d85; margin: 0 0 .4rem; }
      .av-heading { font-size: clamp(1.8rem, 3vw, 2.65rem); font-weight: 760;
                    line-height: 1.15; letter-spacing: -.035em; margin: .1rem 0 .6rem; }
      .av-subtitle { color: #617184; font-size: 1rem; max-width: 780px; margin-bottom: 1.2rem; }
      .av-hero { padding: 1.4rem 1.65rem; border-radius: 16px; border: 1px solid #d7e7ed;
                 background: linear-gradient(115deg, #ecf8f7 0%, #f2f7ff 100%);
                 color: #14354c; margin: 0 0 1.5rem; }
      .av-hero strong { color: #075b66; }
      .av-safe { font-size: .86rem; color: #455d6c; }
      .av-footer { border-top: 1px solid #d3dce2; margin-top: 2rem; padding-top: 1rem;
                   color: #667780; font-size: .82rem; }
      .stApp button:focus-visible, .stApp input:focus-visible, .stApp select:focus-visible {
          outline: 3px solid #e6a300 !important; outline-offset: 3px !important;
      }
      div[data-testid="stMetric"] { background: rgba(19, 120, 128, .045);
                                      border: 1px solid rgba(19, 120, 128, .17);
                                      border-radius: 14px; padding: 18px; }
      div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {
          min-height: 44px; border-radius: 10px; font-weight: 650;
      }
      [data-testid="stSidebar"] { border-right: 1px solid rgba(80, 125, 145, .17); }
      @media (max-width: 760px) { .block-container { padding: 1rem; }
                                    .av-hero { padding: 1.1rem; } }
      @media (prefers-reduced-motion: reduce) { *, *::before, *::after {
            animation-duration: .01ms !important; transition-duration: .01ms !important; } }
    </style>
    '''
    if large:
        css += '''<style>
          .stApp, .stApp p, .stApp label, .stApp input, .stApp button {font-size: 1.13rem !important;}
          .stApp button {min-height: 54px !important;}
          [data-testid="stMarkdownContainer"] p {line-height: 1.72 !important;}
          </style>'''
    if contrast:
        css += '''<style>
          [data-testid="stAppViewContainer"] {background: #ffffff !important; color: #0a1a2d !important;}
          .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label {color: #0a1a2d !important;}
          .av-hero {background: #ffffff !important; color: #061b31 !important;
                    border: 3px solid #002b55 !important;}
          .av-subtitle, .av-safe, .av-kicker {color: #18364e !important;}
          .stApp [data-testid="stButton"] button,
          .stApp [data-testid="stFormSubmitButton"] button {
            background: #002b55 !important; color: #ffffff !important; border: 2px solid #002b55 !important;
          }
          div[data-testid="stMetric"] {background: #fff !important; border: 2px solid #002b55 !important;}
          </style>'''
    st.markdown(css, unsafe_allow_html=True)


# La navigation et les options persistent lors du changement de page.
with st.sidebar:
    st.markdown('### 🎙️ AccessiVoice')
    st.caption('Assistant vocal intelligent')
    st.radio('Navigation principale', PAGES, key='av_nav_v5', label_visibility='collapsed')
    st.divider()
    st.markdown('**Accès rapide**')
    st.toggle('Texte agrandi', key='large_text_access')
    st.toggle('Contraste renforcé', key='high_contrast_access')
    st.caption('Clavier : Tab pour naviguer, Entrée pour valider.')
    st.divider()
    st.caption('Démonstration sur des données fictives uniquement.')

apply_accessibility_styles()
page = st.session_state['av_nav_v5']
try:
    api_get('/health', timeout=3)
    api_online = True
except requests.RequestException:
    api_online = False


def page_header(kicker: str, heading: str, subtitle: str):
    st.markdown(f'<div class="av-kicker">{kicker}</div><div class="av-heading">{heading}</div>'
                f'<div class="av-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def status_note():
    if api_online:
        st.caption('🟢 API connectée — démonstration locale')
    else:
        st.error('🔴 API arrêtée. Relancez LANCER_ACCESSIVOICE.bat et gardez la fenêtre noire ouverte.')


def load_optional(route: str, key: str) -> list:
    if not api_online:
        return []
    try:
        return api_get(route).get(key, [])
    except requests.RequestException:
        st.warning('Impossible de récupérer les données depuis ' + route + '.')
        return []


if page == PAGES[0]:
    page_header('ACCUEIL · TABLEAU DE BORD', 'Une interface numérique plus simple',
                'Parlez naturellement, consultez des services et accomplissez des actions de démonstration.')
    st.markdown('''<div class="av-hero"><strong>Bonjour 👋</strong><p>
        AccessiVoice vous aide à retrouver des services et à effectuer des démarches fictives
        avec la voix ou le clavier.</p><div class="av-safe">🔒 Les informations sont locales et fictives.</div>
        </div>''', unsafe_allow_html=True)
    status_note()
    services = load_optional('/services', 'services')
    requests_history = load_optional('/demandes', 'demandes')
    interactions = load_optional('/interactions', 'interactions')
    counts = dashboard_counts(services, requests_history, interactions)
    c1, c2, c3 = st.columns(3, gap='medium')
    # Ne pas afficher zero si l'API est hors ligne.
    c1.metric('Services disponibles', counts['services'] if api_online else '—')
    c2.metric('Demandes fictives récentes', counts['demandes'] if api_online else '—')
    c3.metric('Interactions récentes', counts['interactions'] if api_online else '—')
    st.caption('Les compteurs de demandes et interactions portent sur les derniers éléments retournés par l’API, pas sur un total historique exhaustif.')
    st.subheader('Que souhaitez-vous faire ?')
    a, b, c = st.columns(3, gap='medium')
    with a:
        with st.container(border=True):
            st.markdown('**🎙️ Parler à AccessiVoice**')
            st.caption('Posez une question en français ou saisissez-la au clavier.')
            st.button('Ouvrir l’assistant', use_container_width=True,
                      on_click=navigate, args=(PAGES[1],))
    with b:
        with st.container(border=True):
            st.markdown('**🔎 Trouver un service**')
            st.caption('Découvrez les services fictifs disponibles par ville.')
            st.button('Explorer les services', use_container_width=True,
                      on_click=navigate, args=(PAGES[2],))
    with c:
        with st.container(border=True):
            st.markdown('**🧾 Faire une demande**')
            st.caption('Choisissez un service, puis confirmez sa demande fictive.')
            st.button('Créer une demande', use_container_width=True,
                      on_click=navigate, args=(PAGES[3],))
    st.subheader('Activité de démonstration')
    if requests_history:
        for req in requests_history[:3]:
            st.write(f"Demande n°{req['id']} · {req['objet']} · {req['statut']}")
    else:
        st.caption('Aucune demande récente à afficher.')
    st.info('Pour tester la voix : ouvrez « Assistant vocal », puis prononcez « Quels services sont disponibles à Casablanca ? ».')

elif page == PAGES[1]:
    page_header('ASSISTANT · VOIX ET TEXTE', 'Parlez, AccessiVoice vous répond',
                'Deux façons de communiquer : une phrase écrite ou un enregistrement audio.')
    status_note()
    col_text, col_voice = st.columns(2, gap='large')
    with col_text:
        with st.container(border=True):
            st.subheader('⌨️ Écrire une demande')
            with st.form('commande', clear_on_submit=False):
                phrase = st.text_input('Votre demande', placeholder='Quels services sont disponibles à Casa Blanca ?')
                clicked = st.form_submit_button('Envoyer la commande', use_container_width=True)
            if clicked:
                if not phrase.strip():
                    st.warning('Veuillez saisir une demande.')
                else:
                    try:
                        show_result(api_post('/execute', {'texte': phrase}, timeout=45))
                    except requests.RequestException as exc:
                        st.error(f'Impossible de traiter la commande : {str(exc)[:160]}')
    with col_voice:
        with st.container(border=True):
            st.subheader('🎙️ Commande vocale')
            audio = st.audio_input('Parler (microphone)')
            if st.button('Transcrire et exécuter', use_container_width=True):
                if audio is None:
                    st.warning('Enregistrez d’abord une phrase avec votre microphone.')
                else:
                    try:
                        with st.spinner('Reconnaissance vocale locale en cours…'):
                            response = requests.post(
                                API + '/voice', files={'file': ('audio.wav', audio.getvalue(), 'audio/wav')},
                                timeout=180)
                        if response.status_code == 503:
                            try:
                                detail = response.json().get('detail', 'Indisponible.')
                            except ValueError:
                                detail = response.text[:200]
                            st.error('Reconnaissance vocale : ' + detail)
                            st.caption('Consultez les journaux du serveur dans logs/api.log.')
                        else:
                            response.raise_for_status()
                            show_result(response.json())
                    except requests.RequestException as exc:
                        st.error(f'Erreur audio ou API : {str(exc)[:180]}')
    last = st.session_state.get('last_result')
    if last:
        st.subheader('Résultat de votre demande')
        with st.container(border=True):
            st.write('**Commande reconnue :**', last.get('texte', ''))
            st.success(last.get('reponse', ''))
            speak_answer(last.get('reponse', ''))
            intent, confidence, city = response_meta(last)
            st.caption(f'Intention : {intent} · confiance : {confidence:.2f}')
            if city:
                st.caption('📍 Ville détectée : ' + city)
            action = last.get('action_proposee')
            if action == 'modifier_profil' or action == 'consulter_profil':
                st.info('Ouvrez la rubrique Profil fictif pour consulter ou modifier les données.')
                st.button('👤 Accéder au profil', on_click=navigate, args=(PAGES[4],))
            elif action == 'creer_demande':
                st.info('Choisissez un service dans la rubrique Demandes, puis confirmez explicitement.')
                st.button('🧾 Accéder aux demandes', on_click=navigate, args=(PAGES[3], city))
            elif intent == 'rechercher_service':
                st.button('🔎 Voir les services correspondants', on_click=navigate,
                          args=(PAGES[2], city))
    with st.expander('Exemples de commandes'):
        st.markdown('''- Quels services sont disponibles à Casa Blanca ?
- Je veux consulter mes informations.
- Je veux modifier mon profil.
- Je veux effectuer une demande.
- Comment utiliser cette application ?
- Je veux quitter.''')

elif page == PAGES[2]:
    page_header('CATALOGUE · SERVICES', 'Explorer les services disponibles',
                'Les services ci-dessous sont fictifs. Ils servent à montrer la recherche et le filtrage par ville.')
    status_note()
    services = load_optional('/services', 'services')
    cities = ['Toutes les villes'] + available_cities(services)
    if st.session_state['av_service_city'] not in cities:
        st.session_state['av_service_city'] = 'Toutes les villes'
    chosen_city = st.selectbox('Filtrer par ville', cities, key='av_service_city')
    filtered = filter_services(services, chosen_city)
    st.caption(f'{len(filtered)} service(s) dans la sélection.')
    if filtered:
        for service in filtered:
            with st.container(border=True):
                st.markdown(f"**{service['nom']}**")
                st.write(service.get('description', ''))
                st.caption('📍 ' + service['ville'])
        st.button('🧾 Faire une demande pour un service', on_click=navigate,
                  args=(PAGES[3], None if chosen_city == 'Toutes les villes' else chosen_city))
    elif api_online:
        st.info('Aucun service disponible pour ce filtre.')

elif page == PAGES[3]:
    page_header('DÉMARCHES · CONFIRMATION', 'Faire une demande fictive',
                'Sélectionnez un service. Aucun enregistrement ne se fait sans votre confirmation.')
    status_note()
    st.info('Ces opérations modifient uniquement la base SQLite fictive, jamais un service extérieur.')
    services = load_optional('/services', 'services')
    cities = ['Toutes les villes'] + available_cities(services)
    if st.session_state['av_requests_city'] not in cities:
        st.session_state['av_requests_city'] = 'Toutes les villes'
    chosen_city = st.selectbox('Ville du service', cities, key='av_requests_city')
    available = filter_services(services, chosen_city)
    if available:
        by_id = {int(service['id']): service for service in available}
        with st.form('submit-demo-request'):
            service_id = st.selectbox('Service disponible', options=list(by_id),
                                      format_func=lambda i: service_title(by_id[i]))
            confirm_request = st.form_submit_button('Confirmer la demande fictive', use_container_width=True)
        if confirm_request:
            try:
                r = api_post('/demandes', {'service_id': int(service_id)}, timeout=8)
                req = r['demande']
                st.session_state['av_request_confirmation'] = (
                    f"Demande fictive n°{req['id']} enregistrée : {req['service']} ({req['ville']}).")
            except requests.RequestException as exc:
                st.error(f'Demande non enregistrée : {str(exc)[:140]}')
    elif api_online:
        st.info('Aucun service disponible dans cette ville.')
    if st.session_state.get('av_request_confirmation'):
        st.success(st.session_state['av_request_confirmation'])
        speak_answer(st.session_state['av_request_confirmation'])
    st.subheader('Historique des demandes fictives')
    reqs = load_optional('/demandes', 'demandes')
    if reqs:
        for req in reqs:
            with st.container(border=True):
                st.write(f"**Demande n°{req['id']}** · {req['objet']}")
                st.caption(f"Statut : {req['statut']} · Date : {req['date']}")
    elif api_online:
        st.caption('Aucune demande fictive enregistrée pour le moment.')

elif page == PAGES[4]:
    page_header('PROFIL · DÉMONSTRATION', 'Consulter et modifier un profil fictif',
                'Ce profil est un exemple local. Ne saisissez pas de vraies informations personnelles.')
    status_note()
    try:
        user = api_get('/profil-demo').get('profil')
        if user:
            with st.container(border=True):
                st.write(f"**Profil actuel :** {user['prenom']} {user['nom']}")
                st.caption(f"Adresse fictive : {user['email']}")
                with st.form('edit-demo-profile'):
                    new_nom = st.text_input('Nom fictif', value=user['nom'])
                    new_prenom = st.text_input('Prénom fictif', value=user['prenom'])
                    new_email = st.text_input('Adresse fictive (format e-mail)', value=user['email'])
                    save_profile = st.form_submit_button('Enregistrer les modifications du profil fictif')
                if save_profile:
                    try:
                        r = requests.patch(API + '/profil-demo',
                                           json={'nom': new_nom, 'prenom': new_prenom, 'email': new_email},
                                           timeout=8)
                        if r.status_code == 422:
                            st.error('Vérifiez les champs : nom, prénom et adresse au format e-mail sont requis.')
                        else:
                            r.raise_for_status()
                            st.session_state['av_profile_confirmation'] = 'Le profil fictif a bien été enregistré.'
                            st.write('**Profil mis à jour :**', r.json()['profil'])
                    except requests.RequestException as exc:
                        st.error(f'Profil non modifié : {str(exc)[:140]}')
            if st.session_state.get('av_profile_confirmation'):
                st.success(st.session_state['av_profile_confirmation'])
                speak_answer(st.session_state['av_profile_confirmation'])
        else:
            st.warning('Aucun profil fictif trouvé.')
    except requests.RequestException:
        st.warning('API indisponible pour consulter le profil.')

elif page == PAGES[5]:
    page_header('JOURNAL · INTERACTIONS', 'Historique des interactions',
                'Consultez les commandes précédemment adressées à l’assistant de démonstration.')
    status_note()
    interactions = load_optional('/interactions', 'interactions')
    if interactions:
        for item in interactions:
            with st.container(border=True):
                st.caption(f"{item['date']} · Intention : {item['intention']}")
                st.write('**Demande :**', item['commande'])
                st.write('**Réponse :**', item['reponse'])
    elif api_online:
        st.caption('Aucune interaction enregistrée pour le moment.')

elif page == PAGES[6]:
    page_header('RÉGLAGES · ACCESSIBILITÉ', 'Une application adaptable à chacun',
                'Personnalisez l’affichage et la lecture audio. Les paramètres restent dans cette session.')
    status_note()
    st.subheader('Affichage')
    st.write('Les options « Texte agrandi » et « Contraste renforcé » sont disponibles à tout moment dans la barre latérale.')
    st.subheader('Voix et lecture')
    st.select_slider('Vitesse de la réponse orale', options=[0.75, 0.85, 0.95, 1.05, 1.15],
                     key='speech_rate_access')
    st.write(f"Vitesse sélectionnée : {st.session_state['speech_rate_access']:.2f}×")
    st.caption('La lecture est déclenchée uniquement par le bouton « Lire la réponse » du lecteur.')
    st.subheader('Tester le lecteur')
    speak_answer('Bonjour. Bienvenue sur AccessiVoice, votre assistant de démonstration accessible.')
    st.subheader('Conseils de navigation')
    st.markdown('''- **Tab** : passer au contrôle suivant.
- **Entrée ou Espace** : activer le contrôle sélectionné.
- Utilisez un navigateur avec une voix française installée pour une meilleure lecture.
- Le résultat vocal et les services sont fictifs ; aucune accessibilité certifiée n’est revendiquée.''')

st.markdown('<div class="av-footer">AccessiVoice · Prototype pédagogique local · Données fictives · '
            'Voix, NLP, services et actions avec confirmation</div>', unsafe_allow_html=True)
