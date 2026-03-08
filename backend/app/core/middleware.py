"""中间件配置."""

import time
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings


def setup_cors(app: ASGIApp) -> None:
    """配置 CORS 中间件."""
    # Parse CORS_ORIGINS from string to list
    cors_origins = settings.CORS_ORIGINS
    if isinstance(cors_origins, str):
        cors_origins = [origin.strip() for origin in cors_origins.split(",")]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        return response


def setup_middleware(app: ASGIApp) -> None:
    """配置所有中间件."""
    setup_cors(app)
    app.add_middleware(RequestLoggingMiddleware)
