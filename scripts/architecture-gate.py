import sys
from pathlib import Path
from typing import List


# ============================================================
# ADR-0005: Repository Structure Lock
# ============================================================

ALLOWED_ROOT_DIRS = {
    "domain",
    "application",
    "infrastructure",
    "interface",
    "projection",   # ← ДОБАВИТЬ ЭТУ СТРОКУ
    "contracts",
    "docs",
    "scripts",
    ".github",
    "tests",
    "migrations",
}

ALLOWED_ROOT_FILES = {
    "README.md",
    "pyproject.toml",
    "ARCHITECTURE.md",
    "ARCHITECTURE_CONTEXT.md",
    "PROJECT_STATE.md",
    "docker-compose.yml",
    "alembic.ini",
    "requirements.txt",
    "requirements-dev.txt",
    ".gitignore",
    ".pre-commit-config.yaml",
    ".env",              # допустимо для dev
}


# ============================================================
# Structure Validation
# ============================================================

def check_structure() -> List[str]:
    violations = []
    root = Path(".")

    IGNORED_DIRS = {
        ".git",
        ".idea",
        "__pycache__",
        ".venv",
        "venv",
    }

    IGNORED_FILES_PREFIX = {
        ".coverage",
    }

    for item in root.iterdir():

        if item.name in IGNORED_DIRS:
            continue

        if any(item.name.startswith(p) for p in IGNORED_FILES_PREFIX):
            continue

        if item.name.startswith(".") and item.name not in {
            ".github",
            ".gitignore",
            ".pre-commit-config.yaml",
            ".env",
        }:
            continue

        if item.is_dir():
            if item.name not in ALLOWED_ROOT_DIRS:
                violations.append(f"Forbidden root directory: {item.name}")

        elif item.is_file():
            if item.name not in ALLOWED_ROOT_FILES:
                violations.append(f"Unexpected root file: {item.name}")

    return violations


# ============================================================
# ADR-0004: Boundary Contracts
# ============================================================

FORBIDDEN_IMPORTS = {
    "domain": ["sqlalchemy", "fastapi"],
    "application": ["fastapi", "sqlalchemy"],
    "infrastructure": ["fastapi"],  # infra не должен знать HTTP
}


def check_boundaries() -> List[str]:
    violations = []

    for layer, forbidden in FORBIDDEN_IMPORTS.items():
        layer_path = Path(layer)
        if not layer_path.exists():
            continue

        for file in layer_path.rglob("*.py"):
            content = file.read_text(encoding="utf-8")

            for forbidden_import in forbidden:
                if (
                    f"import {forbidden_import}" in content
                    or f"from {forbidden_import}" in content
                ):
                    violations.append(
                        f"[{layer.capitalize()}] {file}: "
                        f"forbidden import '{forbidden_import}'"
                    )

    return violations


# ============================================================
# Entry Point
# ============================================================

def main() -> None:
    structure_violations = check_structure()
    boundary_violations = check_boundaries()

    if boundary_violations:
        print("\nArchitecture boundary violations detected (ADR-0004):\n")
        for v in boundary_violations:
            print(f"  {v}")
        sys.exit(1)

    if structure_violations:
        print("\nRepository structure violations detected (ADR-0005):\n")
        for v in structure_violations:
            print(f"  {v}")
        sys.exit(1)

    print("Architecture Gate (Core Frozen v1) ... Passed")


if __name__ == "__main__":
    main()