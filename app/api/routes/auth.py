from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == data.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already exists")

    result = await session.execute(select(User).where(User.email == data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == data.username))
    user = result.scalars().first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)