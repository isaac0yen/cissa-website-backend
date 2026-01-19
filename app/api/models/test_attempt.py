"""Test Attempt, AttemptQuestion, and TestAttemptAnswer data models"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.core.base.model import BaseTableModel


class TestAttempt(BaseTableModel):
    __tablename__ = "test_attempts"

    test_id = Column(
        String, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id = Column(
        String,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score = Column(Integer, nullable=False, default=0)
    max_score = Column(Integer, nullable=False)
    status = Column(
        String, nullable=False, default="in_progress", index=True
    )  # 'in_progress', 'submitted', 'expired'
    started_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(
        DateTime(timezone=True), nullable=False
    )  # Server-side expiration
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    test = relationship("Test", backref="attempts")
    student = relationship("StudentProfile", backref="test_attempts")
    attempt_questions = relationship(
        "AttemptQuestion", back_populates="attempt", cascade="all, delete-orphan"
    )
    answers = relationship(
        "TestAttemptAnswer", back_populates="attempt", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "test_id": self.test_id,
            "student_id": self.student_id,
            "score": self.score,
            "max_score": self.max_score,
            "status": self.status,
            "started_at": self.started_at,
            "expires_at": self.expires_at,
            "completed_at": self.completed_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return f"TestAttempt: {self.student_id} - {self.test_id} ({self.status})"


class AttemptQuestion(BaseTableModel):
    __tablename__ = "attempt_questions"

    attempt_id = Column(
        String,
        ForeignKey("test_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        String, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    question_order = Column(Integer, nullable=False)  # order shown to student

    # Relationships
    attempt = relationship("TestAttempt", back_populates="attempt_questions")
    question = relationship("Question", backref="attempt_questions")

    # Table constraints
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "attempt_id": self.attempt_id,
            "question_id": self.question_id,
            "question_order": self.question_order,
            "created_at": self.created_at,
        }

    def __str__(self):
        return (
            f"AttemptQuestion: Order {self.question_order} in Attempt {self.attempt_id}"
        )


class TestAttemptAnswer(BaseTableModel):
    __tablename__ = "test_attempt_answers"

    attempt_id = Column(
        String,
        ForeignKey("test_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        String, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    option_id = Column(
        String, ForeignKey("question_options.id", ondelete="SET NULL"), nullable=True
    )
    is_correct = Column(Boolean, nullable=False, default=False)

    # Relationships
    attempt = relationship("TestAttempt", back_populates="answers")
    question = relationship("Question", backref="answers")
    option = relationship("QuestionOption", backref="answers")

    # Table constraints
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_answer"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "attempt_id": self.attempt_id,
            "question_id": self.question_id,
            "option_id": self.option_id,
            "is_correct": self.is_correct,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return f"Answer: {'✓' if self.is_correct else '✗'} - Attempt {self.attempt_id}"
