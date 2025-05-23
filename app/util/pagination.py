from typing import Tuple, Type, TypeVar

from sqlalchemy import Select, not_
from sqlalchemy.orm import Session

from app.core.config import configs
from app.model.base_model import BaseModel
from app.schema.base_schema import FindResult, PaginationQuery, SearchOptions

T = TypeVar("T", bound=BaseModel)

U = TypeVar("U", bound=PaginationQuery)


def paginate(
    query: Select[Tuple[T]], schema: U, session: Session, model: Type[T], soft_delete_visibility: bool = False, paginate: bool = True
) -> FindResult[T]:
    schema_as_dict = schema.model_dump(exclude_none=True)
    ordering = schema_as_dict.get("ordering", configs.ORDERING)
    order_by = schema_as_dict.get("order_by", configs.ORDER_BY)
    order_query = getattr(model, order_by).desc() if ordering == "desc" else getattr(model, order_by).asc()
    paginated_query = query
    if not soft_delete_visibility:
        paginated_query = query.filter(not_(model.is_deleted))
    paginated_query = paginated_query.order_by(order_query)
    total = session.execute(paginated_query).unique().scalars().all().__len__()
    if paginate:
        paginated_query = paginated_query.offset(schema.offset).limit(schema.limit)
        if schema.page_size * (schema.page - 1) > total:
            raise ValueError("Page out of range")

    return FindResult(
        founds=list(session.execute(paginated_query).unique().scalars().all()),
        search_options=SearchOptions(total_count=total, page=schema.page, page_size=schema.page_size, ordering=ordering, order_by=order_by),
    )
