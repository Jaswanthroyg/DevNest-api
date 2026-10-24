"""App entry point. Run with:  uvicorn app.main:app --reload"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, SessionLocal, engine
from .models import User
from .routers import admin, answers, auth, questions, users
from .security import hash_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once at startup: create tables and make sure a first admin exists."""
    Base.metadata.create_all(bind=engine)
    email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("ADMIN_PASSWORD", "admin12345")  # change this in production!
    with SessionLocal() as db:
        if not db.query(User).filter(User.email == email).first():
            db.add(User(username="admin", email=email,
                        hashed_password=hash_password(password), role="admin"))
            db.commit()
    yield


app = FastAPI(title="Tech Community API", version="1.0.0", lifespan=lifespan)

# Plug in each group of endpoints
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Tech Community API is running. Docs at /docs"}
