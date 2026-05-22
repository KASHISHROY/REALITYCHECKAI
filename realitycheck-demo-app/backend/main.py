import os
from uuid import uuid4

from fastapi import APIRouter, FastAPI, Response


DATABASE_URL = os.getenv("DATABASE_URL")
SESSION_SECRET = os.environ["SESSION_SECRET"]
REDIS_URL = os.getenv("REDIS_URL")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")

app = FastAPI(title="Acme Ops Portal")
router = APIRouter(prefix="/api/v1")


@router.get("/users")
def list_users():
    return [{"id": 1, "name": "Ada"}]


@router.post("/sessions")
def create_session(response: Response):
    session_id = f"session-{uuid4()}"
    response.set_cookie("session_id", session_id, httponly=True)
    return {"session_id": session_id}


@router.get("/items")
def list_items():
    return [{"id": 10, "name": "Reality widget"}]


@router.post("/purchases")
def create_purchase():
    return {"status": "queued"}


@router.get("/me")
def current_user():
    return {"id": 1, "role": "admin"}


@router.get("/status")
def status():
    return {
        "database": bool(DATABASE_URL),
        "redis_configured": bool(REDIS_URL),
        "internal_token": bool(INTERNAL_API_TOKEN),
    }


app.include_router(router)
