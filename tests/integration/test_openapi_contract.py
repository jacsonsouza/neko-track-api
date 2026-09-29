"""Guards the committed OpenAPI contract against drifting from the code."""

import json
import pathlib

from app.main import app

CONTRACT = pathlib.Path("docs/openapi.json")


def test_committed_openapi_contract_is_up_to_date():
    assert CONTRACT.exists(), "docs/openapi.json is missing - run scripts/export_openapi.py"

    documented = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert app.openapi() == documented, (
        "docs/openapi.json is stale - run scripts/export_openapi.py and commit it"
    )


def test_contract_exposes_every_public_route():
    documented = json.loads(CONTRACT.read_text(encoding="utf-8"))

    paths = documented["paths"]
    assert "/api/v1/me/anime-list" in paths
    assert "/api/v1/activities/{activity_id}/replies" in paths
    assert "/api/v1/animes/{anime_id}" in paths
    assert "/auth/anilist/me" in paths

    # Every non-redirect operation documents a success response schema.
    for path, operations in paths.items():
        for method, operation in operations.items():
            if method == "parameters":
                continue
            if path.startswith("/auth/anilist/start") or path.endswith("/callback"):
                continue
            assert "200" in operation["responses"], f"{method.upper()} {path}"
