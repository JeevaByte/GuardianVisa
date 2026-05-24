from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class GuardianVisaError(Exception):
    def __init__(self, message: str, code: str = "platform_error", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(GuardianVisaError)
    async def gv_handler(_: Request, exc: GuardianVisaError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def fallback_handler(_: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": str(exc)}},
        )

