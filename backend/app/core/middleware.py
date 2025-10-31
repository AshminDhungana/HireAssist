from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.services.resumeparser import FileParseError
import logging

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