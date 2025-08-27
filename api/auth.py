from app.schemas.user import UserCreate, UserLogin, UserOut
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.user_service import create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = await create_user(db, user)
    return new_user


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    auth_user = await authenticate_user(db, user.email, user.password)
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(auth_user.id)})
    return {"access_token": token, "token_type": "bearer"}
