from datetime import datetime, timedelta
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

bearer_scheme = HTTPBearer()

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    return decode_access_token(credentials.credentials)


# --- Token encryption for DB storage ---
# Fernet key must be 32 url-safe base64-encoded bytes.
# Derived from SECRET_KEY â€” in production use a dedicated ENCRYPTION_KEY env var.
def _get_fernet() -> Fernet:
    import base64
    key = base64.urlsafe_b64encode(settings.secret_key.encode()[:32].ljust(32, b"0"))
    return Fernet(key)


def encrypt_token(token: str) -> str:
    return _get_fernet().encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()

