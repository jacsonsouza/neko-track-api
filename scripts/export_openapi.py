"""Export the OpenAPI contract to ``docs/openapi.json``.

Run it whenever a route, schema or enum changes:

    .venv/bin/python scripts/export_openapi.py

``tests/integration/test_openapi_contract.py`` fails when the file is stale.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402

OUTPUT = ROOT / "docs" / "openapi.json"


def export() -> pathlib.Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    contract = json.dumps(app.openapi(), indent=2, ensure_ascii=False, sort_keys=True)
    OUTPUT.write_text(contract + "\n", encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(f"written to {export()}")
