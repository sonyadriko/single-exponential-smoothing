from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request
from passlib.context import CryptContext
from jose import JWTError, jwt
from config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        return {"username": username, "role": role}
    except JWTError:
        return None


# Session-based authentication functions
def create_session(request: Request, username: str, role: str):
    """Create a session for the authenticated user."""
    request.session["user"] = {"username": username, "role": role}


def get_session_user(request: Request) -> Optional[dict]:
    """Get the current user from session."""
    return request.session.get("user")


def clear_session(request: Request):
    """Clear the session."""
    request.session.clear()


def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated via session."""
    return "user" in request.session


def is_admin(request: Request) -> bool:
    """Check if current session user is admin."""
    user = get_session_user(request)
    return user is not None and user.get("role") == "admin"
