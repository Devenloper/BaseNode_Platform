#!/usr/bin/env python3
import sys
import re
from pathlib import Path

# ---- Правила архитектурных границ ----

RULES = [
    # Domain
    {
        "path": "domain/",
        "forbidden": [
            r"sqlalchemy",
            r"fastapi",
            r"pydantic",
            r"infrastructure",
            r"application",
        ],
        "layer": "Domain",
    },
    # Application
    {
        "path": "application/",
        "forbidden": [
            r"fastapi",
            r"pydantic",
            r"sqlalchemy",
            r"JSONResponse",
        ],
        "layer": "Application",
    },
    # Infrastructure
    {
        "path": "infrastructure/",
        "forbidden": [
            r"fastapi",
            r"pydantic",
            r"APIRouter",
            r"HTTPException",
        ],
        "layer": "Infrastructure",
    },
    # Interface
    {
        "path": "interface/",
        "forbidden": [
            r"sqlalchemy",
            r"event_store",
            r"outbox",
            r"snapshot",
        ],
        "layer": "Interface",
    },
]

IMPORT_RE = re.compile(r"^\s*(from|import)\s+([a-zA-Z0-9_.]+)", re.MULTILINE)


def check_file(file_path: Path) -> list[str]:
    errors = []
    text = file_path.read_text(encoding="utf-8", errors="ignore")

    for rule in RULES:
        if rule["path"] in str(file_path):
            for match in IMPORT_RE.findall(text):
                imported = match[1]
                for forbidden in rule["forbidden"]:
                    if re.search(forbidden, imported):
                        errors.append(
                            f"[{rule['layer']}] {file_path}: forbidden import '{imported}'"
                        )
    return errors


def main(files):
    violations = []

    for file in files:
        path = Path(file)
        if not path.exists() or not path.suffix == ".py":
            continue
        violations.extend(check_file(path))

    if violations:
        print("\n🚫 Architecture boundary violations detected:\n")
        for v in violations:
            print(v)
        print(
            "\nCore Frozen v1 violated.\n"
            "See docs/boundary_contracts.md and docs/architecture_validation_checklist.md"
        )
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])