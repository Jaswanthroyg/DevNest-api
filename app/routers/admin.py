"""Admin-only endpoints. Every route here requires get_current_admin."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import AdminUserCreate, UserPrivate
from ..security import get_current_admin
from .auth import create_user

# Putting the dependency on the router protects ALL routes below at once.
router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])


@router.get("/users", response_model=list[UserPrivate])
def list_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).offset(skip).limit(limit).all()


@router.post("/users", response_model=UserPrivate, status_code=201)
def admin_create_user(data: AdminUserCreate, db: Session = Depends(get_db)):
    return create_user(db, data, role=data.role)


@router.delete("/users/{user_id}", status_code=204)
def admin_delete_user(user_id: int, admin: User = Depends(get_current_admin),
                      db: Session = Depends(get_db)):
    """Deletes the user AND all their questions, answers and votes (cascade)."""
    if user_id == admin.id:
        raise HTTPException(400, "Admins cannot delete themselves")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()

# Deleting questions/answers as admin uses the normal DELETE endpoints
# (they already allow admins), so no duplicate code is needed here.
