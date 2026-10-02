"""Shared error contract for the public API.

Every non-2xx response is serialised as :class:`ErrorResponse` so clients can
branch on the machine-readable ``code`` instead of parsing human text. The
``detail`` field is kept because it is what the mobile client already reads.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UPSTREAM_ERROR = "UPSTREAM_ERROR"


ERROR_CODE_BY_STATUS: dict[int, ErrorCode] = {
    400: ErrorCode.BAD_REQUEST,
    401: ErrorCode.UNAUTHORIZED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    409: ErrorCode.BAD_REQUEST,
    422: ErrorCode.VALIDATION_ERROR,
    429: ErrorCode.RATE_LIMITED,
    500: ErrorCode.INTERNAL_ERROR,
    502: ErrorCode.UPSTREAM_ERROR,
    503: ErrorCode.UPSTREAM_ERROR,
    504: ErrorCode.UPSTREAM_ERROR,
}


def error_code_for(status_code: int) -> ErrorCode:
    """Map an HTTP status to the error code exposed by the API."""
    if status_code in ERROR_CODE_BY_STATUS:
        return ERROR_CODE_BY_STATUS[status_code]

    return ErrorCode.BAD_REQUEST if status_code < 500 else ErrorCode.INTERNAL_ERROR


class ErrorDetail(BaseModel):
    """Field-level issue attached to :class:`ErrorResponse` (422 responses)."""

    loc: str
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Body of every error response produced by the API."""

    detail: str
    code: ErrorCode
    errors: list[ErrorDetail] = Field(default_factory=list)


# Additional responses documented on every authenticated router.
ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse, "description": "Missing or invalid app JWT"},
    403: {"model": ErrorResponse, "description": "AniList account not connected"},
    422: {"model": ErrorResponse, "description": "Request validation error"},
    429: {
        "model": ErrorResponse,
        "description": "AniList rate limit exceeded (Retry-After header)",
    },
    502: {"model": ErrorResponse, "description": "Invalid AniList response"},
    504: {"model": ErrorResponse, "description": "AniList request timed out"},
}
