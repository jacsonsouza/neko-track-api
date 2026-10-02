"""Exception handlers that render :class:`ErrorResponse` on every failure.

This is also the single place where provider failures raised by the AniList
gateway (see :mod:`app.modules.anilist.errors`) become HTTP responses, so the
whole error contract can be read in one file.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.errors import ErrorDetail, ErrorResponse, error_code_for
from app.modules.anilist.errors import (
    AnilistError,
    AnilistRateLimitError,
    AnilistResponseError,
    AnilistTimeoutError,
)


def _error_response(
    status_code: int, detail: str, errors: list[ErrorDetail] | None = None
) -> JSONResponse:
    body = ErrorResponse(
        detail=detail,
        code=error_code_for(status_code),
        errors=errors or [],
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    response = _error_response(exc.status_code, detail)

    if exc.headers:
        response.headers.update(exc.headers)

    return response


def request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        ErrorDetail(
            loc=".".join(str(part) for part in error.get("loc", ())),
            msg=str(error.get("msg", "")),
            type=str(error.get("type", "")),
        )
        for error in exc.errors()
    ]
    return _error_response(422, "Request validation error", errors)


def anilist_payload_handler(request: Request, exc: ValidationError) -> JSONResponse:
    # A pydantic ValidationError escaping the service layer means the payload
    # came from AniList in an unexpected shape, not from the API client.
    return _error_response(502, "Invalid AniList response")


def anilist_response_handler(
    request: Request, exc: AnilistResponseError
) -> JSONResponse:
    # AniList answered 200 with something we cannot use: GraphQL errors[],
    # missing data or a non-JSON body.
    return _error_response(502, "Invalid AniList response")


def anilist_error_handler(request: Request, exc: AnilistError) -> JSONResponse:
    # Transport-level failure (non-200 status, connection error).
    return _error_response(502, "AniList request failed")


def anilist_timeout_handler(
    request: Request, exc: AnilistTimeoutError
) -> JSONResponse:
    return _error_response(504, "AniList request timed out")


def anilist_rate_limit_handler(
    request: Request, exc: AnilistRateLimitError
) -> JSONResponse:
    response = _error_response(429, "AniList rate limit exceeded")

    if exc.retry_after:
        response.headers["Retry-After"] = str(exc.retry_after)

    return response


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(ValidationError, anilist_payload_handler)

    # Most specific first for readability; Starlette walks the MRO anyway.
    app.add_exception_handler(AnilistRateLimitError, anilist_rate_limit_handler)
    app.add_exception_handler(AnilistTimeoutError, anilist_timeout_handler)
    app.add_exception_handler(AnilistResponseError, anilist_response_handler)
    app.add_exception_handler(AnilistError, anilist_error_handler)
