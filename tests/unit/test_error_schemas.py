"""Unit tests for the shared error contract."""

import pytest

from app.core.errors import ErrorCode, ErrorResponse, error_code_for


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (400, ErrorCode.BAD_REQUEST),
        (401, ErrorCode.UNAUTHORIZED),
        (403, ErrorCode.FORBIDDEN),
        (404, ErrorCode.NOT_FOUND),
        (422, ErrorCode.VALIDATION_ERROR),
        (500, ErrorCode.INTERNAL_ERROR),
        (502, ErrorCode.UPSTREAM_ERROR),
        (418, ErrorCode.BAD_REQUEST),
        (507, ErrorCode.INTERNAL_ERROR),
    ],
)
def test_error_code_for_maps_status_codes(status_code, expected):
    assert error_code_for(status_code) is expected


def test_error_response_defaults_to_an_empty_error_list():
    body = ErrorResponse(detail="Invalid token.", code=ErrorCode.UNAUTHORIZED)

    assert body.model_dump() == {
        "detail": "Invalid token.",
        "code": "UNAUTHORIZED",
        "errors": [],
    }
