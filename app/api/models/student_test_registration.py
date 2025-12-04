"""Student Test Registration data model"""

from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.base.model import BaseTableModel


class StudentTestRegistration(BaseTableModel):
    __tablename__ = "student_test_registration"

    student_id = Column(
        String,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_id = Column(
        String, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    payment_id = Column(
        String,
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=True,  # Allow direct registration without payment
        unique=True,
    )

    # Relationships
    student = relationship("StudentProfile", backref="test_registrations")
    test = relationship("Test", backref="registrations")
    payment = relationship("Payment", backref="registration", uselist=False)

    # Table constraints
    __table_args__ = (
        UniqueConstraint("student_id", "test_id", name="uq_student_test"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "test_id": self.test_id,
            "payment_id": self.payment_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return f"Registration: Student {self.student_id} - Test {self.test_id}"
