from typing import Any

from dependency_injector.wiring import inject
from fastapi import Depends
from jose import jwt
from pydantic import ValidationError

from app.core.config import configs
from app.core.exceptions import AuthError
from app.core.security import ALGORITHM, JWTBearer


@inject
def validate_token(
    token: str = Depends(JWTBearer()),
) -> dict[str, Any]:

    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=ALGORITHM)
        if payload["token_type"] != "access":
            raise AuthError(detail="Invalid token type")
        return payload
    except (jwt.JWTError, ValidationError):
        raise AuthError(detail="Could not validate credentials")
