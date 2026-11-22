"""Base SQLite locale, uniquement pour la demonstration AccessiVoice.

La migration V3 est additive: les donnees V2 et les anciennes demandes sont conservees.
"""
from __future__ import annotations
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv('ACCESSIVOICE_DB', str(ROOT / 'data' / 'accessivoice.sqlite3')))


@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db():
    with connect() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY, nom TEXT NOT NULL, prenom TEXT NOT NULL, email TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY, nom TEXT NOT NULL, description TEXT NOT NULL,
            ville TEXT NOT NULL, disponible INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, commande TEXT NOT NULL,
            intention TEXT NOT NULL, reponse TEXT NOT NULL,
            date TEXT NOT NULL DEFAULT (datetime('now')));
        CREATE TABLE IF NOT EXISTS demandes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, objet TEXT NOT NULL,
            statut TEXT NOT NULL DEFAULT 'enregistrée', date TEXT NOT NULL DEFAULT (datetime('now')),
            service_id INTEGER REFERENCES services(id));
        ''')
        # Migration d'une base V2 existante, sans DROP ni ecrasement.
        columns = {row['name'] for row in con.execute('PRAGMA table_info(demandes)')}
        if 'service_id' not in columns:
            con.execute('ALTER TABLE demandes ADD COLUMN service_id INTEGER REFERENCES services(id)')
        con.execute("INSERT OR IGNORE INTO utilisateurs(id, nom, prenom, email) VALUES (1, 'Démo', 'Utilisateur', 'demo@example.invalid')")
        services = [
            (1, 'Aide administrative', 'Assistance aux démarches administratives', 'Casablanca', 1),
            (2, 'Assistance informatique', 'Accompagnement aux outils numériques', 'Casablanca', 1),
            (3, 'Prise de rendez-vous', 'Accompagnement à la prise de rendez-vous', 'Rabat', 1),
            (4, 'Information citoyenne', 'Informations sur les services', 'Marrakech', 1),
            (5, 'Formation numérique', 'Initiation aux services en ligne', 'Casablanca', 0),
        ]
        con.executemany('''INSERT OR IGNORE INTO services(id, nom, description, ville, disponible)
                           VALUES (?, ?, ?, ?, ?)''', services)


def list_services(ville: str | None = None):
    with connect() as con:
        if ville:
            rows = con.execute('''SELECT id, nom, description, ville FROM services
                                  WHERE disponible = 1 AND lower(ville) = lower(?)
                                  ORDER BY nom''', (ville,)).fetchall()
        else:
            rows = con.execute('''SELECT id, nom, description, ville FROM services
                                  WHERE disponible = 1 ORDER BY ville, nom''').fetchall()
    return [dict(r) for r in rows]


def demo_user():
    with connect() as con:
        row = con.execute('SELECT nom, prenom, email FROM utilisateurs WHERE id = 1').fetchone()
    return dict(row) if row else None


def update_demo_user(*, nom: str, prenom: str, email: str):
    """Ne modifie que l'unique profil fictif, pas de compte reel."""
    with connect() as con:
        cur = con.execute('UPDATE utilisateurs SET nom = ?, prenom = ?, email = ? WHERE id = 1',
                          (nom.strip(), prenom.strip(), email.strip()))
        if cur.rowcount != 1:
            raise LookupError('Profil de demonstration absent')
    return demo_user()


def get_service(service_id: int):
    with connect() as con:
        row = con.execute('''SELECT id, nom, description, ville, disponible
                             FROM services WHERE id = ?''', (service_id,)).fetchone()
    return dict(row) if row else None


def create_service_request(service_id: int):
    """Enregistre une demande fictive sur un service disponible et existant."""
    with connect() as con:
        row = con.execute('''SELECT id, nom, ville, disponible FROM services WHERE id = ?''',
                          (service_id,)).fetchone()
        if row is None:
            raise LookupError('Service inexistant')
        if not row['disponible']:
            raise ValueError('Service indisponible pour le moment')
        objet = f"Demande fictive : {row['nom']} ({row['ville']})"
        cur = con.execute('INSERT INTO demandes(objet, service_id) VALUES (?, ?)',
                          (objet, service_id))
        request_id = cur.lastrowid
    return {'id': request_id, 'objet': objet, 'statut': 'enregistrée',
            'service_id': service_id, 'service': row['nom'], 'ville': row['ville']}


def create_request(objet: str):
    """Compatibilite historique: anciennes demandes de demonstration sans service."""
    with connect() as con:
        cur = con.execute('INSERT INTO demandes(objet) VALUES (?)', (objet,))
        return cur.lastrowid


def list_requests(limit: int = 20):
    with connect() as con:
        rows = con.execute('''SELECT d.id, d.objet, d.statut, d.date, d.service_id,
                                    s.nom AS service, s.ville AS ville
                             FROM demandes d LEFT JOIN services s ON s.id = d.service_id
                             ORDER BY d.id DESC LIMIT ?''', (max(1, min(limit, 50)),)).fetchall()
    return [dict(r) for r in rows]


def add_interaction(commande: str, intention: str, reponse: str):
    with connect() as con:
        con.execute('INSERT INTO interactions(commande, intention, reponse) VALUES (?, ?, ?)',
                    (commande, intention, reponse))


def recent_interactions(limit: int = 10):
    with connect() as con:
        rows = con.execute('''SELECT commande, intention, reponse, date FROM interactions
                              ORDER BY id DESC LIMIT ?''', (min(max(limit, 1), 50),)).fetchall()
    return [dict(r) for r in rows]
