"""Answer endpoints: answer, accept, vote, delete."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Answer, Question, User, Vote
from ..schemas import AnswerCreate, AnswerOut, VoteIn
from ..security import get_current_user

router = APIRouter(tags=["Answers"])


def get_answer_or_404(db: Session, answer_id: int) -> Answer:
    answer = db.get(Answer, answer_id)
    if not answer:
        raise HTTPException(404, "Answer not found")
    return answer


@router.post("/questions/{question_id}/answers", response_model=AnswerOut, status_code=201)
def post_answer(question_id: int, data: AnswerCreate, user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    if not db.get(Question, question_id):
        raise HTTPException(404, "Question not found")
    answer = Answer(body=data.body, question_id=question_id, owner_id=user.id)
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


@router.post("/answers/{answer_id}/accept", response_model=AnswerOut)
def accept_answer(answer_id: int, user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """Only the person who asked the question can mark an answer as accepted."""
    answer = get_answer_or_404(db, answer_id)
    question = answer.question
    if question.owner_id != user.id:
        raise HTTPException(403, "Only the question owner can accept an answer")
    # Only one accepted answer per question: clear the old one first
    for a in question.answers:
        a.is_accepted = False
    answer.is_accepted = True
    question.is_answered = True  # question now shows as "answered"
    db.commit()
    db.refresh(answer)
    return answer


@router.post("/answers/{answer_id}/vote", response_model=AnswerOut)
def vote_answer(answer_id: int, data: VoteIn, user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    """Upvote (+1) or downvote (-1). Voting again just CHANGES your previous vote."""
    answer = get_answer_or_404(db, answer_id)
    if answer.owner_id == user.id:
        raise HTTPException(400, "You cannot vote on your own answer")
    vote = db.query(Vote).filter(Vote.user_id == user.id, Vote.answer_id == answer_id).first()
    if vote:
        vote.value = data.value                       # update existing vote
    else:
        db.add(Vote(user_id=user.id, answer_id=answer_id, value=data.value))
    db.commit()
    db.refresh(answer)  # reload so the new score is calculated
    return answer


@router.delete("/answers/{answer_id}", status_code=204)
def delete_answer(answer_id: int, user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """Only the answer's author OR an admin can delete it."""
    answer = get_answer_or_404(db, answer_id)
    if answer.owner_id != user.id and user.role != "admin":
        raise HTTPException(403, "You can only delete your own answers")
    if answer.is_accepted:
        answer.question.is_answered = False  # no accepted answer anymore
    db.delete(answer)
    db.commit()
