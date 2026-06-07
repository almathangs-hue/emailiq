from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.routers import auth, applications, sync

app = FastAPI(title="EmailIQ API", version="0.1.0")

# Sessions required by Authlib for OAuth state verification (CSRF protection)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# CORS — only allow requests from the frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(sync.router)


@app.get("/health")
def health():
    return {"status": "ok"}
