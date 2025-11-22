"""Payment data model for Paystack integration"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base.model import BaseTableModel


class Payment(BaseTableModel):
    __tablename__ = "payments"

    student_id = Column(
        String,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_id = Column(
        String, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount = Column(Numeric(10, 2), nullable=False)  # amount in NGN
    currency = Column(String, nullable=False, default="NGN")
    paystack_reference = Column(String, unique=True, nullable=False, index=True)
    paystack_access_code = Column(String, nullable=True)
    status = Column(
        String, nullable=False, index=True
    )  # 'pending', 'success', 'failed'
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    student = relationship("StudentProfile", backref="payments")
    test = relationship("Test", backref="payments")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "test_id": self.test_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "paystack_reference": self.paystack_reference,
            "paystack_access_code": self.paystack_access_code,
            "status": self.status,
            "paid_at": self.paid_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return f"Payment: {self.paystack_reference} - {self.status}"
