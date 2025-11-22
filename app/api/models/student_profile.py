"""Student Profile data model"""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base.model import BaseTableModel


class StudentProfile(BaseTableModel):
    __tablename__ = "student_profiles"

    user_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    # Relationship to User
    user = relationship("User", backref="student_profile", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return f"Student Profile: {self.first_name} {self.last_name}"
