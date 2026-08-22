"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.embeddings import warm_up
from app.routes.reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    # Load (and, on first run, download) the embedding model now, so the
    # one-time delay happens at startup rather than mid-request the first
    # time a user opens a report's matches.
    warm_up()
    yield


app = FastAPI(title="Lost & Found Matcher API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports_router)
