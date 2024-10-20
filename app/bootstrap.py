from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.api.session.models import sync_engine
from app.api.session.session import router


def bootstrap():
    app = FastAPI()
    setup(app)
    load_handlers(app)
    return app


def load_handlers(app):
    app.include_router(
        router,
        prefix="/api",
        tags=["index"],
    )


def setup(app):
    create_db_and_tables()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_db_and_tables():
    SQLModel.metadata.create_all(sync_engine)
