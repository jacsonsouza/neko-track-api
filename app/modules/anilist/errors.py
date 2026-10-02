"""Errors raised while talking to AniList.

They are the only vocabulary the gateway uses; the translation to the public
error contract lives in :mod:`app.core.exception_handlers`:

===============================  ======  =================================
Error                            Status  ``ErrorResponse.code``
===============================  ======  =================================
:class:`AnilistRateLimitError`   429     ``RATE_LIMITED`` (+ ``Retry-After``)
:class:`AnilistTimeoutError`     504     ``UPSTREAM_ERROR``
:class:`AnilistResponseError`    502     ``UPSTREAM_ERROR``
:class:`AnilistHttpError`        502     ``UPSTREAM_ERROR``
===============================  ======  =================================
"""


class AnilistError(RuntimeError):
    """Base class for every failure originated by the AniList provider."""


class AnilistHttpError(AnilistError):
    """AniList answered with a non-200 status, or the connection failed."""


class AnilistTimeoutError(AnilistError):
    """The call to AniList did not finish within the configured timeout."""


class AnilistResponseError(AnilistError):
    """AniList answered 200 with a payload the API cannot use.

    GraphQL ``errors[]``, a missing ``data`` field, or a body that is not JSON.
    """


class AnilistRateLimitError(AnilistError):
    """AniList answered 429; ``retry_after`` mirrors the ``Retry-After`` header."""

    def __init__(self, retry_after: int = 0) -> None:
        super().__init__(f"AniList rate limit exceeded, retry after {retry_after}s")
        self.retry_after = retry_after
