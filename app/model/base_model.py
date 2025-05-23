import uuid
from datetime import datetime

from sqlalchemy import func
from sqlmodel import Field, SQLModel


class EntityVersionTracking:
    version: int = Field(default=1, nullable=False)


class OperationTimeTracking:
    created_at: datetime = Field(nullable=False, sa_column_kwargs={"default": func.now()})
    updated_at: datetime | None = Field(nullable=True, sa_column_kwargs={"default": func.now(), "onupdate": func.now()})
    deleted_at: datetime | None = Field(default=None, nullable=True)


class OperationByTracking:
    created_by: uuid.UUID | None = Field(default=None, nullable=True)
    updated_by: uuid.UUID | None = Field(default=None, nullable=True)
    deleted_by: uuid.UUID | None = Field(default=None, nullable=True)


class BaseModel(SQLModel, OperationTimeTracking, OperationByTracking, EntityVersionTracking):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4, nullable=False, index=True)
    is_deleted: bool = Field(default=False, nullable=False)
