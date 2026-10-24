"""Register and login endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import Token, UserCreate, UserPrivate
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


def create_user(db: Session, data: UserCreate, role: str = "user") -> User:
    """Shared helper (also used by the admin router). Checks duplicates, hashes password, saves."""
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    user = User(username=data.username, email=data.email.lower(),
                hashed_password=hash_password(data.password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=UserPrivate, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, data)


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email + password. (The form field is called 'username' by the OAuth2
    standard, but we put the EMAIL in it.)"""
    user = db.query(User).filter(User.email == form.username.lower()).first()
    # Same error for "no user" and "wrong password" so attackers can't guess which emails exist.
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return Token(access_token=create_access_token(user.id))
