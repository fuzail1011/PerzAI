from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.db.session import get_db
from app.services.user_service import create_user, authenticate_user
from app.core.security import create_access_token, get_current_user, verify_password
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut)
async def signup(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    new_user = await create_user(
        db,
        user,
    )
    return new_user


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    auth_user = await authenticate_user(
        db,
        user.email,
        user.password,
    )
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(str(auth_user.id))
    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/get_all_users", response_model=list[UserOut])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),  # JWT required
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.delete("/delete_user")
async def delete_user(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    # Step 1: Find user by email
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Step 2: Verify password
    if not verify_password(
        payload.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # Step 3: Delete user
    await db.delete(user)
    await db.commit()

    return {
        "status": "success",
        "message": f"User {user.email} deleted successfully",
    }
