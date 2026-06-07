from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from app.core.config import settings
from app.core.auth import create_access_token, encrypt_token, get_current_user_id
from app.database import get_db
from app.models import User, ConnectedAccount

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly",
        "access_type": "offline",  # required to get a refresh token
        "prompt": "consent",       # forces refresh token on every login
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

    google_email = userinfo["email"]
    name = userinfo.get("name", google_email)
    picture = userinfo.get("picture")

    # Upsert user
    user = db.query(User).filter(User.email == google_email).first()
    if not user:
        user = User(email=google_email, name=name, picture=picture)
        db.add(user)
        db.flush()

    # Upsert connected account — encrypt tokens before storing
    account = db.query(ConnectedAccount).filter(
        ConnectedAccount.user_id == user.id,
        ConnectedAccount.email == google_email,
    ).first()

    access_token = token.get("access_token", "")
    refresh_token = token.get("refresh_token", "")

    if not account:
        account = ConnectedAccount(
            user_id=user.id,
            email=google_email,
            access_token=encrypt_token(access_token),
            refresh_token=encrypt_token(refresh_token) if refresh_token else "",
        )
        db.add(account)
    else:
        account.access_token = encrypt_token(access_token)
        if refresh_token:
            account.refresh_token = encrypt_token(refresh_token)

    db.commit()

    jwt_token = create_access_token(user.id)
    return RedirectResponse(f"{settings.frontend_url}/dashboard?token={jwt_token}")


@router.get("/me")
def me(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "name": user.name, "picture": user.picture}


@router.post("/logout")
def logout():
    # JWT is stateless — logout is handled client-side by discarding the token
    return {"message": "Logged out"}
