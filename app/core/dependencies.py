from typing import Any

from dependency_injector.wiring import inject
from fastapi import Depends
from pydantic import ValidationError

from app.core.exceptions import AuthError
from app.core.security import JWTBearer, decode_jwt
import logging

logger = logging.getLogger(__name__)


@inject
def validate_token(
    token: str = Depends(JWTBearer()),
) -> dict[str, Any]:

    try:
        payload = decode_jwt(token)
        logger.debug("Decoded payload: %s", payload)  # Debugging line

        if not payload:  # decode_jwt returns {} or None if invalid
            raise AuthError(detail="Could not validate credentials")

        if payload.get("token_type") != "access":
            raise AuthError(detail="Invalid token type")
        return payload
    except (ValidationError,):
        raise AuthError(detail="Could not validate credentials")
