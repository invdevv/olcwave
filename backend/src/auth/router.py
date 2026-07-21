from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
import jwt

from config import settings
from auth.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    if body.username != settings.ADMIN_USERNAME or body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": body.username, "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return TokenResponse(access_token=token)
