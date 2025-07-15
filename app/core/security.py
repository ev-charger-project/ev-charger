from datetime import datetime, timedelta

import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import configs
from app.core.exceptions import AuthError

ALGORITHM = "HS256"


def create_access_token(subject: dict, expires_delta: timedelta = None) -> (str, str):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    payload = {"exp": expire, "token_type": "access", **subject}

    encoded_jwt = jwt.encode(payload, configs.SECRET_KEY, algorithm=ALGORITHM)
    expiration_datetime = expire.strftime(configs.DATETIME_FORMAT)
    return encoded_jwt, expiration_datetime


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, configs.SECRET_KEY, algorithms=[ALGORITHM])
        return (
            decoded_token
            if decoded_token["exp"] >= int(round(datetime.utcnow().timestamp()))
            else None
        )
    except jwt.InvalidSignatureError as e:
        print(f"JWT Invalid Signature error: {e}")
        return {}
    except jwt.ExpiredSignatureError as e:
        print(f"JWT Expired Signature error: {e}")
        return {}
    except jwt.InvalidTokenError as e:
        print(f"JWT Invalid Token error: {e}")
        return {}
    except Exception as e:
        print(f"JWT decode error: {e}")  # Added debugging to see the actual error
        return {}


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise AuthError(detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise AuthError(detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise AuthError(detail="Invalid authorization code.")

    def verify_jwt(self, jwt_token: str) -> bool:
        is_token_valid: bool = False
        try:
            payload = decode_jwt(jwt_token)
        except Exception:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid
