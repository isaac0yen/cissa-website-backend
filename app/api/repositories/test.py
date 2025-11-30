from sqlalchemy.orm import Session, Query
from typing import Optional

from app.core.base.repository import BaseRepository
from app.api.models.test import Test


class TestRepository(BaseRepository[Test]):
    """
    Test repository class for CRUD operations on Test model.
    This class inherits from BaseRepository and provides specific methods for Test model.
    Attributes:
        model (Type[Test]): The SQLAlchemy Test model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(Test, db)

    
    def publish_test(self, test_id: str) -> Test:
        """Publish a test by setting its is_published attribute to True.

        Args:
            test_id (str): The ID of the test to be published.

        Returns:
            Test: The updated test object.
        """
        test = self.get(test_id)
        if test:
            test.is_published = True
            self.db.commit()
            self.db.refresh(test)
        return test
    
    def unpublish_test(self, test_id: str) -> Test:
        """Unpublish a test by setting its is_published attribute to False.

        Args:
            test_id (str): The ID of the test to be unpublished.

        Returns:
            Test: The updated test object.
        """
        test = self.get(test_id)
        if test:
            test.is_published = False
            self.db.commit()
            self.db.refresh(test)
        return test
    
    # Additional filter methods can be added here as needed
    def filter_by_publication_status(
        self, query: Query[Test], is_published: Optional[bool]
    ) -> Query[Test]:
        """Filter tests by publication status.

        Args:
            is_published (bool): Publication status to filter by.

        Returns:
            Session: A SQLAlchemy query object with the applied filter.
        """

        if is_published is not None:
            return query.filter(self.model.is_published == is_published)
        return query
    
    def search_by_course_title(
        self, query: Query[Test], course_title: Optional[str]
    ) -> Query[Test]:
        """Search tests by course title (case-insensitive).

        Args:
            course_title (str): The course title or partial title to search for.

        Returns:
            Query[Test]: A SQLAlchemy query object with the applied filter.
        """
        if course_title:
            return query.filter(self.model.course_title.ilike(f"%{course_title}%"))
        return query

    def search_by_course_code(
        self, query: Query[Test], course_code: Optional[str]
    ) -> Query[Test]:
        """Search tests by course code (case-insensitive).

        Args:
            course_code (str): The course code or partial code to search for.

        Returns:
            Query[Test]: A SQLAlchemy query object with the applied filter.
        """
        if course_code:
            return query.filter(self.model.course_code.ilike(f"%{course_code}%"))
        return query
    