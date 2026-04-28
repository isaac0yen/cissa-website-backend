from sqlalchemy.orm import Session, Query
from sqlalchemy import func
from typing import Optional

from app.core.base.repository import BaseRepository
from app.api.models.material import Material, Department

class DepartmentRepository(BaseRepository[Department]):
    """
    Department repository class for CRUD operations on Department model.
    This class inherits from BaseRepository and provides specific methods for Department model.
    Attributes:
        model (Type[Department]): The SQLAlchemy Department model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(Department, db)

    def get_by_name(self, name: str) -> Optional[Department]:
        """Get a department by its name (case-insensitive).

        Args:
            name (str): The name of the department.

        Returns:
            Optional[Department]: The Department object if found, else None.
        """
        return self.db.query(self.model).filter(func.lower(self.model.name) == func.lower(name)).first()

class MaterialRepository(BaseRepository[Material]):
    """
    Material repository class for CRUD operations on Material model.
    This class inherits from BaseRepository and provides specific methods for Material model.
    Attributes:
        model (Type[Material]): The SQLAlchemy Material model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(Material, db)

    # filter and search methods

    def search_by_title(self, query: Query[Material], title: Optional[str]) -> Query[Material]:
        """Search materials by title (case-insensitive).

        Args:
            title (str): The title or partial title to search for.

        Returns:
            Query[Material]: A SQLAlchemy query object with the applied filter.
        """
        if title:
            return query.filter(self.model.title.ilike(f"%{title}%"))
        return query
    
    def filter_by_department(self, query: Query[Material], department_name: Optional[str]) -> Query[Material]:
        """Filter materials by department name (case-insensitive).

        Args:
            department_name (str): The name of the department to filter by.

        Returns:
            Query[Material]: A SQLAlchemy query object with the applied filter.
        """
        if department_name:
            return query.join(self.model.departments).filter(func.lower(Department.name) == func.lower(department_name))
        return query
    
    def filter_by_course_code(self, query: Query[Material], course_code: Optional[str]) -> Query[Material]:
        """Filter materials by course code (case-insensitive).

        Args:
            course_code (str): The course code to filter by.

        Returns:
            Query[Material]: A SQLAlchemy query object with the applied filter.
        """
        if course_code:
            return query.filter(func.lower(self.model.course_code) == func.lower(course_code))
        return query
    
    def filter_by_level(self, query: Query[Material], level: Optional[str]) -> Query[Material]:
        """Filter materials by level (case-insensitive).

        Args:
            level (str): The level to filter by.

        Returns:
            Query[Material]: A SQLAlchemy query object with the applied filter.
        """
        if level:
            return query.filter(func.lower(self.model.level) == func.lower(level))
        return query
    
    def filter_by_semester(self, query: Query[Material], semester: Optional[str]) -> Query[Material]:
        """Filter materials by semester (case-insensitive).

        Args:
            semester (str): The semester to filter by.

        Returns:
            Query[Material]: A SQLAlchemy query object with the applied filter.
        """
        if semester:
            return query.filter(func.lower(self.model.semester) == func.lower(semester))
        return query
    
    def filter_by_material_type(self, query: Query[Material], material_type: Optional[str]) -> Query[Material]:
        """Filter materials by material type (case-insensitive).

        Args:
            material_type (str): The material type to filter by.

        Returns:
            Query[Material]: A SQLAlchemy query object with the applied filter.
        """
        if material_type:
            return query.filter(func.lower(self.model.material_type) == func.lower(material_type))
        return query
    
    def filter_by_session(self, query: Query[Material], session: Optional[str]) -> Query[Material]:
        """Filter materials by session (case-insensitive).

        Args:
            session (str): The session to filter by.

        Returns:
            Query[Material]: A SQLAlchemy query object with the applied filter.
        """
        if session:
            return query.filter(func.lower(self.model.session) == func.lower(session))
        return query