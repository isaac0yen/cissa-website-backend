from sqlalchemy.orm import Session, Query
from sqlalchemy import func
from typing import Optional

from app.core.base.repository import BaseRepository
from app.api.models.event import Event


class EventRepository(BaseRepository[Event]):
    """
    Event repository class for CRUD operations on Event model.
    This class inherits from BaseRepository and provides specific methods for Event model.
    Attributes:
        model (Type[Event]): The SQLAlchemy Event model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(Event, db)

    def get_by_slug_or_id(self, identifier: str) -> Optional[Event]:
        """Retrieve an event by its slug, falling back to its ID.

        Looks up by slug first (the SEO-friendly identifier); if no match is
        found, tries the primary key. This keeps legacy UUID links working.

        Args:
            identifier (str): A slug or an event ID.

        Returns:
            Optional[Event]: The matching event, or None.
        """
        event = (
            self.db.query(self.model)
            .filter(self.model.slug == identifier)
            .first()
        )
        if event:
            return event
        return self.get(identifier)

    def slug_exists(self, slug: str) -> bool:
        """Check whether a slug is already used by an event."""
        return (
            self.db.query(self.model).filter(self.model.slug == slug).first()
            is not None
        )

    # filters

    # filter upcoming events (events that have a start date in the future)
    def filter_upcoming_events(self, query: Query[Event]) -> Query[Event]:
        """Filter upcoming events

        Filter based on start date and time
            - If the start date is in the future, it's an upcoming event.
            - If the start date is today and the start time is in the future, it's an upcoming event.
            - If the end date is in the future, it's an upcoming event.
            - If the end date is today and the end time is in the future, it's an upcoming event.

        Returns:
            Query[Event]: A SQLAlchemy query object with the applied filter.
        """

        return query.filter(
            (self.model.start_date > func.current_date())
            | (
                (self.model.start_date == func.current_date())
                & (self.model.start_time > func.current_time())
            )
            | (self.model.end_date > func.current_date())
            | (
                (self.model.end_date == func.current_date())
                & (self.model.end_time > func.current_time())
            )
        )

    # filter past events (events that have an end date in the past)
    def filter_past_events(self, query: Query[Event]) -> Query[Event]:
        """Filter past events

        Filter based on end date and time
            - If the end date is in the past, it's a past event.
            - If the end date is today and the end time is in the past, it's a past event.
            - If the end date is today and the end time is null and the start time is in the past, it's a past event.
            - If the end date is null and the start date is in the past, it's a past event.
            - If the end date is null and the start date is today and the start time is in the past, it's a past event.

        Returns:
            Query[Event]: A SQLAlchemy query object with the applied filter.
        """

        return query.filter(
            (self.model.end_date < func.current_date())
            | (
                (self.model.end_date == func.current_date())
                & (self.model.end_time < func.current_time())
            )
            | (
                (self.model.end_date == func.current_date())
                & (self.model.end_time == None) # noqa: E711
                & (self.model.start_time < func.current_time())
            )
            | (
                (self.model.end_date == None) # noqa: E711
                & (self.model.start_date < func.current_date())
            )
            | (
                (self.model.end_date == None) # noqa: E711
                & (self.model.start_date == func.current_date())
                & (self.model.start_time < func.current_time())
            )
        )

    def search_by_title(
        self, query: Query[Event], title: Optional[str]
    ) -> Query[Event]:
        """Search events by title (case-insensitive).

        Args:
            title (str): The title or partial title to search for.

        Returns:
            Query[Event]: A SQLAlchemy query object with the applied filter.
        """
        if title:
            return query.filter(self.model.title.ilike(f"%{title}%"))
        return query

    # filter based on location type (e.g., online, in-person)
    # there are only two location types, so we can use an enum for this in the future
    def filter_by_location_type(
        self, query: Query[Event], location_type: Optional[str]
    ) -> Query[Event]:
        """Filter events by location type (case-insensitive).

        Args:
            location_type (str): The location type to filter by (e.g., 'online', 'in-person').

        Returns:
            Query[Event]: A SQLAlchemy query object with the applied filter.
        """
        if location_type:
            return query.filter(self.model.location_type == location_type)
        return query
