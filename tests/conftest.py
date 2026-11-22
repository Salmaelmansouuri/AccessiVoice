import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope='session')
def client(tmp_path_factory):
    db = tmp_path_factory.mktemp('db') / 'test.sqlite3'
    os.environ['ACCESSIVOICE_DB'] = str(db)
    from app import database
    database.DB_PATH = Path(db)
    from app.main import app
    with TestClient(app) as client:
        yield client
