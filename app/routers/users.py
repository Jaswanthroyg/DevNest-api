"""Profile endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserPrivate, UserPublic, UserUpdate
from ..security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPrivate)
def my_profile(user: User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserPrivate)
def update_my_profile(data: UserUpdate, user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if data.username and data.username != user.username:
        if db.query(User).filter(User.username == data.username).first():
            raise HTTPException(409, "Username already taken")
        user.username = data.username
    if data.bio is not None:
        user.bio = data.bio
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserPublic)
def public_profile(user_id: int, db: Session = Depends(get_db)):
    """Anyone can view a public profile (email is hidden by the UserPublic schema)."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user
