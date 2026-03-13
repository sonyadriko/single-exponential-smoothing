from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

import models
from database import get_db
from schemas.auth import Token, UserResponse, TokenData
from services.auth_service import verify_password, create_access_token, decode_token
from config import get_settings
from repositories.user_repository import UserRepository

router = APIRouter()
settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """Get the currently authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_token(token)
    if token_data is None or token_data.get("username") is None:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = user_repo.get_by_username(token_data["username"])
    if user is None:
        raise credentials_exception
    return user


async def get_admin_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Dependency that ensures the current user is an admin."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login endpoint."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Get information about the currently authenticated user."""
    return {"username": current_user.username, "role": current_user.role}
