import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.api.session.models import sync_engine as engine
from app.bootstrap import bootstrap


@pytest.fixture
def app() -> FastAPI:
    app = bootstrap()
    yield app


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


def test_load_handlers(client):
    response = client.post("/api/sessions")
    assert response.status_code == 422


