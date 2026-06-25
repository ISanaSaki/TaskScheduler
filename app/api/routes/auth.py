from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.database import get_session
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_refresh_token
)
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse, RefreshRequest
from app.core.logger import get_logger
from app.core.limiter import limiter

logger = get_logger("auth")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == data.username))
    if result.scalars().first():
        logger.warning(f"Register failed - username '{data.username}' already exists")
        raise HTTPException(status_code=400, detail="Username already exists")

    result = await session.execute(select(User).where(User.email == data.email))
    if result.scalars().first():
        logger.warning(f"Register failed - email '{data.email}' already exists")
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info(f"New user registered: '{data.username}'")

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed for username: '{form_data.username}'")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    logger.info(f"User '{form_data.username}' logged in successfully")

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh(request: Request, data: RefreshRequest, session: AsyncSession = Depends(get_session)):
    username = decode_refresh_token(data.refresh_token)

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        logger.warning(f"Refresh failed - user not found: '{username}'")
        raise HTTPException(status_code=401, detail="User not found")

    logger.info(f"Token refreshed for user: '{username}'")

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)