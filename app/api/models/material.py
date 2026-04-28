""" Material models for the application. """

from sqlalchemy import Column, String, Table, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base.model import BaseTableModel


material_departments = Table(
    'material_departments',
    BaseTableModel.metadata,
    Column('material_id', String, ForeignKey('materials.id'), primary_key=True),
    Column('department_id', String, ForeignKey('departments.id'), primary_key=True)
)

class Department(BaseTableModel):
    __tablename__ = "departments"

    name = Column(String, nullable=False)

    materials = relationship(
        "Material",
        secondary=material_departments,
        back_populates="departments",
    )


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

    def __str__(self):
        return "Department: {}".format(self.name)

class Material(BaseTableModel):
    __tablename__ = "materials"

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    course_code = Column(String, nullable=False)
    course_title = Column(String, nullable=False)
    level = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    material_type = Column(String, nullable=False)
    drive_url = Column(String, nullable=False)
    session = Column(String, nullable=True)

    departments = relationship(
        "Department",
        secondary=material_departments,
        back_populates="materials",
    )


    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "course_code": self.course_code,
            "course_title": self.course_title,
            "level": self.level,
            "semester": self.semester,
            "material_type": self.material_type,
            "drive_url": self.drive_url,
            "session": self.session,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "departments": [dept.name for dept in self.departments]
        }

    def __str__(self):
        return "Material: {}".format(self.title)