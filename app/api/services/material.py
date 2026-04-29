from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session

from app.api.models.material import Material
from app.api.repositories.material import MaterialRepository, DepartmentRepository
from app.api.v1.material import schemas
from app.core.base.schema import PaginatedResponse
from app.utils.logger import logger


class MaterialService:
    """
    Service class for handling material-related operations.
    This class interacts with the MaterialRepository to perform CRUD operations on materials.
    """

    def __init__(self, db: Session):
        self.repository = MaterialRepository(db)
        self.department_repository = DepartmentRepository(db)

    def create(self, schema: schemas.MaterialRequest) -> Material:
        """
        Creates a new material

        Args:
            schema (schemas.MaterialRequest): The material data to create.
        Returns:
            Material: The created material object.
        """

        # fetch departments
        departments = []
        for dept_name in schema.departments:
            dept = self.department_repository.get(dept_name)
            if not dept:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Department '{dept_name}' not found.",
                )
            departments.append(dept)

        material_data = schema.model_dump(exclude={"departments"})
        material = Material(**material_data)
        material.departments = departments

        try:
            logger.info(
                f"Creating material: {material.id} - {material.title} - {material.course_code}"
            )
            return self.repository.create(material)
        except Exception as e:
            logger.error(f"Error creating material: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the material.",
            )

    def update(
        self, material_id: str, schema: schemas.MaterialUpdateRequest
    ) -> Material:
        """
        Updates an existing material

        Args:
            material_id (str): The ID of the material to update.
            schema (schemas.MaterialUpdateRequest): The updated material data.
        Returns:
            Material: The updated material object.
        """

        material = self.repository.get(material_id)
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Material not found."
            )

        # fetch departments if provided
        if schema.departments is not None:
            departments = []
            for dept_name in schema.departments:
                dept = self.department_repository.get(dept_name)
                if not dept:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Department '{dept_name}' not found.",
                    )
                departments.append(dept)
            material.departments = departments

        update_data = schema.model_dump(exclude={"departments"}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(material, key, value)

        try:
            logger.info(
                f"Updating material: {material.id} - {material.title} - {material.course_code}"
            )
            return self.repository.update(material)
        except Exception as e:
            logger.error(f"Error updating material: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the material.",
            )

    def delete(self, material_id: str) -> None:
        """
        Deletes a material by its ID.

        Args:
            material_id (str): The ID of the material to delete.
        Returns:
            None
        """
        material = self.repository.get(material_id)
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Material not found."
            )

        try:
            logger.info(
                f"Deleting material: {material.id} - {material.title} - {material.course_code}"
            )
            self.repository.delete(material)
        except Exception as e:
            logger.error(f"Error deleting material: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the material.",
            )

    def get(self, material_id: str) -> Material:
        """
        Retrieves a material by its ID.

        Args:
            material_id (str): The ID of the material to retrieve.
        Returns:
            Material: The retrieved material object.
        """
        material = self.repository.get(material_id)
        if not material:
            logger.error(f"Material with ID '{material_id}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Material not found."
            )
        logger.info(
            f"Material retrieved: {material.id} - {material.title} - {material.course_code}"
        )
        return material

    def list(
        self,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None,
        department: Optional[schemas.DepartmentType] = None,
        course_code: Optional[str] = None,
        level: Optional[schemas.LevelType] = None,
        semester: Optional[schemas.SemesterType] = None,
        material_type: Optional[str] = None,
        session: Optional[str] = None,
    ) -> PaginatedResponse:
        """
        Retrieves a paginated list of materials with optional filtering.

        Args:
            page (int): The page number to retrieve.
            page_size (int): The number of items per page.
            title (Optional[str]): Filter by material title (case-insensitive).
            department (Optional[schemas.DepartmentType]): Filter by department name (case-insensitive).
            course_code (Optional[str]): Filter by course code (case-insensitive).
            level (Optional[schemas.LevelType]): Filter by level (case-insensitive).
            semester (Optional[schemas.SemesterType]): Filter by semester (case-insensitive).
            material_type (Optional[str]): Filter by material type (case-insensitive).
            session (Optional[str]): Filter by session (case-insensitive).
        Returns:
            PaginatedResponse: A paginated response containing the list of materials.
        """

        query = self.repository.base_query()

        # apply filters
        query = self.repository.search_by_title(query, title)
        query = self.repository.filter_by_department(query, department)
        query = self.repository.filter_by_course_code(query, course_code)
        query = self.repository.filter_by_level(query, level)
        query = self.repository.filter_by_semester(query, semester)
        query = self.repository.filter_by_material_type(query, material_type)
        query = self.repository.filter_by_session(query, session)

        return self.repository.paginate(query, page, page_size)
