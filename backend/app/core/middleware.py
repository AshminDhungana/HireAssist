from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.services.resumeparser import FileParseError
import logging
import time
import uuid
from collections import defaultdict
from app.core.config import settings

logger = logging.getLogger(__name__)

async def global_error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except FileParseError as e:
        # Handle known parsing errors
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(e), "error_type": "parse_error"}
        )
    except Exception as e:
        # Log unexpected errors
        logger.exception("Unexpected error occurred: %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred",
                "error_type": "internal_error"
            }
        )


# Request ID and basic structured access log
async def request_context_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "access log",
        extra={
            "event": "access",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else None,
        },
    )
    return response


# Simple in-memory rate limiter per client IP
_ip_hits = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    try:
        limit = int(getattr(settings, "RATE_LIMIT_PER_MINUTE", 120))
    except Exception:
        limit = 120
    now = time.time()
    window_start = now - 60
    ip = request.client.host if request.client else "unknown"
    hits = _ip_hits[ip]
    # prune old hits
    while hits and hits[0] < window_start:
        hits.pop(0)
    if len(hits) >= limit:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    hits.append(now)
    return await call_next(request)


# Security headers
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self' 'unsafe-inline' data:")
    return response