"""Question endpoints: ask, list/search, view, delete."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Question, User
from ..schemas import QuestionCreate, QuestionDetail, QuestionOut
from ..security import get_current_user

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("", response_model=QuestionOut, status_code=201)
def ask_question(data: QuestionCreate, user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    question = Question(title=data.title, body=data.body, owner_id=user.id)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.get("", response_model=list[QuestionOut])
def list_questions(
    q: Optional[str] = Query(None, description="Search in title/body"),
    answered: Optional[bool] = Query(None, description="Filter by answered status"),
    skip: int = Query(0, ge=0),             # pagination: how many to skip
    limit: int = Query(10, ge=1, le=50),    # pagination: page size (max 50)
    db: Session = Depends(get_db),
):
    """Public: anyone can browse questions. Newest first."""
    query = db.query(Question)
    if q:
        like = f"%{q}%"
        query = query.filter(Question.title.ilike(like) | Question.body.ilike(like))
    if answered is not None:
        query = query.filter(Question.is_answered == answered)
    return query.order_by(Question.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{question_id}", response_model=QuestionDetail)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(404, "Question not found")
    return question


@router.delete("/{question_id}", status_code=204)
def delete_question(question_id: int, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """Only the owner OR an admin can delete a question."""
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(404, "Question not found")
    if question.owner_id != user.id and user.role != "admin":
        raise HTTPException(403, "You can only delete your own questions")
    db.delete(question)  # answers and votes are deleted automatically (cascade)
    db.commit()
