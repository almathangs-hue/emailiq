from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request

from app.core.config import settings
from app.core.auth import create_access_token, encrypt_token, get_current_user_id
from app.db.session import get_db
from app.repositories.user import UserRepository
from app.repositories.account import AccountRepository
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly",
        "access_type": "offline",
        "prompt": "consent",
    },
)


@router.get("/login")
async def login(request: Request):
    return await oauth.google.authorize_redirect(request, settings.google_redirect_uri)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        raise HTTPException(status_code=400, detail="OAuth authentication failed")

    userinfo = token.get("userinfo")
    if not userinfo:
        raise HTTPException(status_code=400, detail="Could not retrieve user info from Google")

    user_repo = UserRepository(db)
    account_repo = AccountRepository(db)

    user = user_repo.upsert(
        email=userinfo["email"],
        name=userinfo.get("name", userinfo["email"]),
        picture=userinfo.get("picture"),
    )

    account_repo.upsert(
        user_id=user.id,
        email=userinfo["email"],
        access_token=encrypt_token(token.get("access_token", "")),
        refresh_token=encrypt_token(token.get("refresh_token", "")) if token.get("refresh_token") else "",
    )

    db.commit()

    jwt_token = create_access_token(user.id)
    return RedirectResponse(f"{settings.frontend_url}/auth/callback?token={jwt_token}")


@router.get("/me", response_model=UserResponse)
def me(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/logout", status_code=200)
def logout():
    return {"message": "Logged out"}


