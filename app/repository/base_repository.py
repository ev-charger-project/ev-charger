from contextlib import AbstractContextManager
from datetime import datetime
from typing import Any, Callable, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import and_, not_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.config import configs
from app.core.exceptions import DuplicatedError, NotFoundError
from app.model.base_model import BaseModel
from app.schema.base_schema import PaginationQuery
from app.util.query_builder import dict_to_sqlalchemy_filter_options

T = TypeVar("T", bound=BaseModel)

U = TypeVar("U", bound=PaginationQuery)

V = TypeVar("V", bound=PydanticBaseModel)


class BaseRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
        model: Type[T],
    ) -> None:
        self.session_factory = session_factory
        self.model = model

    def read_by_options(self, schema: U, eager=False):
        with self.session_factory() as session:
            schema_as_dict = schema.model_dump(exclude_none=True)
            ordering = schema_as_dict.get("ordering", configs.ORDERING)
            order_by = schema_as_dict.get("order_by", configs.ORDER_BY)
            order_query = (
                getattr(self.model, order_by).desc()
                if ordering == "desc"
                else getattr(self.model, order_by).asc()
            )
            page = schema_as_dict.get("page", configs.PAGE)
            page_size = schema_as_dict.get("page_size", configs.PAGE_SIZE)
            filter_options = dict_to_sqlalchemy_filter_options(
                self.model, schema.model_dump(exclude_none=True)
            )
            query = session.query(self.model)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            filtered_query = query.filter(filter_options).filter(
                not_(self.model.is_deleted)
            )
            query = filtered_query.order_by(order_query)
            if page_size == "all":
                query = query.all()
            else:
                query = query.limit(page_size).offset((page - 1) * page_size).all()
            total_count = filtered_query.count()
            return {
                "founds": query,
                "search_options": {
                    "page": page,
                    "page_size": page_size,
                    "ordering": ordering,
                    "total_count": total_count,
                    "order_by": order_by,
                },
            }

    def read_by_id(self, id: str, eager=False):
        with self.session_factory() as session:
            query = session.query(self.model)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            query = query.filter(
                and_(self.model.id == id, (self.model.is_deleted.__eq__(False)))
            ).first()
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            return query

    def read_by_id_without_deleted(self, id: str, eager=False):
        with self.session_factory() as session:
            query = session.query(self.model)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            query = query.filter(self.model.id == id).first()
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            return query

    def create(self, schema: V):
        with self.session_factory() as session:
            query = self.model(**schema.model_dump(exclude_none=True))
            try:
                session.add(query)
                session.commit()
                session.refresh(query)
            except IntegrityError as e:
                raise DuplicatedError(detail=str(e.orig))
            return query

    def update(self, id: str, schema: V):
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == id).update(
                {
                    **schema.model_dump(exclude_none=True),
                    "version": self.model.version + 1,
                }
            )
            session.commit()
            return self.read_by_id(id)

    def update_attr(self, id: str, column: str, value: Any):
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == id).update(
                {column: value, "version": self.model.version + 1}
            )
            session.commit()
            return self.read_by_id(id)

    def whole_update(self, id: str, schema: V):
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == id).update(
                {**schema.model_dump(), "version": self.model.version + 1}
            )
            session.commit()
            return self.read_by_id(id)

    def delete_by_id(self, id: str):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(and_(self.model.id == id, not_(self.model.is_deleted)))
                .first()
            )
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            session.delete(query)
            session.commit()

    def soft_delete_by_id(self, id: str):
        with self.session_factory() as session:
            delete_query = (
                update(self.model)
                .returning(self.model)
                .filter(and_(self.model.id == id, not_(self.model.is_deleted)))
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow(),
                )
            )
            rs = session.execute(delete_query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            session.commit()

            return self.read_by_id_without_deleted(id)
