"""Database tables. Each class = one table, each attribute = one column."""
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))  # NEVER store plain passwords
    bio: Mapped[str] = mapped_column(String(300), default="")
    role: Mapped[str] = mapped_column(String(10), default="user")  # "user" or "admin"
    created_at: Mapped[datetime] = mapped_column(default=now)

    # cascade="all, delete-orphan": deleting a user also deletes their content.
    questions: Mapped[list["Question"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    answers: Mapped[list["Answer"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    votes: Mapped[list["Vote"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    # Computed values used by the profile page
    @property
    def questions_count(self):
        return len(self.questions)

    @property
    def answers_count(self):
        return len(self.answers)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    body: Mapped[str] = mapped_column(Text)
    is_answered: Mapped[bool] = mapped_column(default=False)  # True once an answer is accepted
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=now)

    owner: Mapped[User] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="Answer.id"
    )

    @property
    def author_name(self):
        return self.owner.username

    @property
    def answers_count(self):
        return len(self.answers)


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    is_accepted: Mapped[bool] = mapped_column(default=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=now)

    owner: Mapped[User] = relationship(back_populates="answers")
    question: Mapped[Question] = relationship(back_populates="answers")
    votes: Mapped[list["Vote"]] = relationship(back_populates="answer", cascade="all, delete-orphan")

    @property
    def author_name(self):
        return self.owner.username

    @property
    def score(self):
        """Net score = upvotes (+1) plus downvotes (-1)."""
        return sum(v.value for v in self.votes)


class Vote(Base):
    __tablename__ = "votes"
    # Database-level rule: one user can have only ONE vote per answer.
    __table_args__ = (UniqueConstraint("user_id", "answer_id", name="one_vote_per_user_per_answer"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int]  # +1 = upvote, -1 = downvote
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"))

    user: Mapped[User] = relationship(back_populates="votes")
    answer: Mapped[Answer] = relationship(back_populates="votes")
