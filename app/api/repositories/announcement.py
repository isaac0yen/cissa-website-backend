from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.api.models.announcement import Announcement, Signatory


class AnnouncementRepository(BaseRepository[Announcement]):
    """
    Announcement repository class for CRUD operations on Announcement model.
    This class inherits from BaseRepository and provides specific methods for Announcement model.
    Attributes:
        model (Type[Announcement]): The SQLAlchemy Announcement model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(Announcement, db)

    def get_by_slug_or_id(self, identifier: str):
        """Retrieve an announcement by its slug, falling back to its ID.

        Looks up by slug first (the SEO-friendly identifier); if no match is
        found, tries the primary key. This keeps legacy UUID links working.

        Args:
            identifier (str): A slug or an announcement ID.

        Returns:
            Optional[Announcement]: The matching announcement, or None.
        """
        announcement = (
            self.db.query(self.model)
            .filter(self.model.slug == identifier)
            .first()
        )
        if announcement:
            return announcement
        return self.get(identifier)

    def slug_exists(self, slug: str) -> bool:
        """Check whether a slug is already used by an announcement."""
        return (
            self.db.query(self.model).filter(self.model.slug == slug).first()
            is not None
        )


class SignatoryRepository(BaseRepository[Signatory]):
    """
    Signatory repository class for CRUD operations on Signatory model.
    This class inherits from BaseRepository and provides specific methods for Signatory model.
    Attributes:
        model (Type[Signatory]): The SQLAlchemy Signatory model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(Signatory, db)
