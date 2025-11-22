"""Test, Question, and QuestionOption data models"""

from sqlalchemy import Column, String, Integer, Boolean, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.base.model import BaseTableModel


class Test(BaseTableModel):
    __tablename__ = "tests"

    course_code = Column(String, unique=True, nullable=False, index=True)
    course_title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    questions_per_attempt = Column(
        Integer, nullable=False
    )  # number of questions to randomly select
    price = Column(Numeric(10, 2), nullable=False)  # price in NGN
    is_published = Column(Boolean, nullable=False, default=False, index=True)

    # Relationships
    questions = relationship(
        "Question", back_populates="test", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "course_code": self.course_code,
            "course_title": self.course_title,
            "duration": self.duration,
            "questions_per_attempt": self.questions_per_attempt,
            "price": float(self.price),
            "is_published": self.is_published,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return f"Test: {self.course_code} - {self.course_title}"


class Question(BaseTableModel):
    __tablename__ = "questions"

    test_id = Column(
        String, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_text = Column(Text, nullable=False)

    # Relationships
    test = relationship("Test", back_populates="questions")
    options = relationship(
        "QuestionOption", back_populates="question", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "test_id": self.test_id,
            "question_text": self.question_text,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return f"Question: {self.question_text[:50]}..."


class QuestionOption(BaseTableModel):
    __tablename__ = "question_options"

    question_id = Column(
        String,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    option_text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)

    # Relationships
    question = relationship("Question", back_populates="options")

    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "option_text": self.option_text,
            "is_correct": self.is_correct,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return f"Option: {self.option_text[:30]}... ({'✓' if self.is_correct else '✗'})"
