from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class EmailIQException(Exception):
    """Base exception for all domain errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(EmailIQException):
    pass


class UnauthorizedError(EmailIQException):
    pass


class ConflictError(EmailIQException):
    pass


class ExternalServiceError(EmailIQException):
    """Raised when Gmail API or other external calls fail."""
    pass


class ValidationError(EmailIQException):
    pass


# --- FastAPI exception handlers ---

async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": exc.message})


async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})


async def external_service_handler(request: Request, exc: ExternalServiceError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": exc.message})


async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.message})


EXCEPTION_HANDLERS = {
    NotFoundError: not_found_handler,
    UnauthorizedError: unauthorized_handler,
    ConflictError: conflict_handler,
    ExternalServiceError: external_service_handler,
    ValidationError: validation_handler,
}
