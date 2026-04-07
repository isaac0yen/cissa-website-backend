"""Event data model"""

from sqlalchemy import Boolean, Column, Date, String, Time, Text

from app.core.base.model import BaseTableModel


class Event(BaseTableModel):
    __tablename__ = "events"

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    location = Column(String, nullable=False)
    location_type = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    requires_ticket = Column(Boolean, nullable=False, default=False)
    ticket_url = Column(String, nullable=True)
    session = Column(String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image_url": self.image_url,
            "location": self.location,
            "location_type": self.location_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "requires_ticket": self.requires_ticket,
            "ticket_url": self.ticket_url,
            "session": self.session,
            "created_at": self.created_at,
        }

    def __str__(self):
        return "Event: {}".format(self.title)
