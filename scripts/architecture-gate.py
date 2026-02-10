#!/usr/bin/env python3

"""
Architecture Gate
=================

Unified architectural validation script.

Enforces:
- ADR-0004 (Boundary Contracts)
- ADR-0005 (Repository Structure Lock)

Exit codes:
- 0 → OK
- 1 → Violations detected
"""

import sys
import re
from pathlib import Path
from typing import List


# ============================================================
# ADR-0004: Boundary Contracts (Import Rules)
# ============================================================

BOUNDARY_RULES = [
    {
        "path": "domain/",
        "layer": "Domain",
        "forbidden": [
            r"sqlalchemy",
            r"fastapi",
            r"pydantic",
            r"infrastructure",
            r"application",
        ],
    },
    {
        "path": "application/",
        "layer": "Application",
        "forbidden": [
            r"fastapi",
            r"pydantic",
            r"sqlalchemy",
            r"JSONResponse",
        ],
    },
    {
        "path": "infrastructure/",
        "layer": "Infrastructure",
        "forbidden": [
            r"fastapi",
            r"pydantic",
            r"APIRouter",
            r"HTTPException",
        ],
    },
    {
        "path": "interface/",
        "layer": "Interface",
        "forbidden": [
            r"sqlalchemy",
            r"event_store",
            r"outbox",
            r"snapshot",
        ],
    },
]

IMPORT_RE = re.compile(r"^\s*(from|import)\s+([a-zA-Z0-9_.]+)", re.MULTILINE)


def check_imports() -> List[str]:
    """
    Validates architectural layer boundaries (ADR-0004).
    """
    violations = []
    root = Path(".")

    for file_path in root.rglob("*.py"):
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        for rule in BOUNDARY_RULES:
            if rule["path"] in str(file_path):
                for match in IMPORT_RE.findall(text):
                    imported_module = match[1]
                    for forbidden in rule["forbidden"]:
                        if re.search(forbidden, imported_module):
                            violations.append(
                                f"[{rule['layer']}] {file_path}: "
                                f"forbidden import '{imported_module}'"
                            )

    return violations


# ============================================================
# ADR-0005: Repository Structure Lock
# ============================================================

ALLOWED_ROOT_DIRS = {
    "domain",
    "application",
    "infrastructure",
    "interface",
    "contracts",
    "docs",
    ".github",
    "scripts",
}

ALLOWED_ROOT_FILES = {
    "pyproject.toml",
    "README.md",
    ".gitignore",
    ".pre-commit-config.yaml",
}


def check_structure() -> List[str]:
    """
    Validates repository root structure (ADR-0005).
    """
    violations = []
    root = Path(".")

    # Служебные директории, которые игнорируем
    IGNORED_DIRS = {
        ".git",
        ".idea",
        "__pycache__",
        ".venv",
        "venv",
    }

    for item in root.iterdir():

        # Игнорируем скрытые директории и служебные
        if item.name in IGNORED_DIRS:
            continue

        if item.name.startswith(".") and item.name != ".github":
            continue

        if item.is_dir():
            if item.name not in ALLOWED_ROOT_DIRS:
                violations.append(f"Forbidden root directory: {item.name}")

        elif item.is_file():
            if item.name not in ALLOWED_ROOT_FILES:
                if not item.name.startswith("."):
                    violations.append(f"Unexpected root file: {item.name}")

    return violations


# ============================================================
# Main
# ============================================================

def main():
    import_violations = check_imports()
    structure_violations = check_structure()

    has_errors = False

    if import_violations:
        has_errors = True
        print("\n[ERROR] Architecture boundary violations detected (ADR-0004):\n")
        for v in import_violations:
            print(f"  {v}")
        print(
            "\nCore Frozen v1 violated.\n"
            "See docs/boundary_contracts.md and "
            "docs/architecture_validation_checklist.md\n"
        )

    if structure_violations:
        has_errors = True
        print("\n[ERROR] Repository structure violations detected (ADR-0005):\n")
        for v in structure_violations:
            print(f"  {v}")
        print(
            "\nRepository Structure Lock violated.\n"
            "Adding new root directories requires a new ADR.\n"
        )

    if has_errors:
        sys.exit(1)

    print("[OK] Architecture Gate passed. Core Frozen v1 intact.")
    sys.exit(0)


if __name__ == "__main__":
    main()