from pydantic import BaseModel


class MeResponse(BaseModel):
    """Authenticated user, in a single shape for both cases below.

    ``exists`` is ``False`` when the app has a valid JWT but no matching row in
    ``users`` (the token was issued before the account row was removed).
    """

    id: int
    anilist_id: int
    name: str | None = None
    exists: bool
