"""Exception handlers that render :class:`ErrorResponse` on every failure."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.errors import ErrorDetail, ErrorResponse, error_code_for


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


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(ValidationError, anilist_payload_handler)
