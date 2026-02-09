#!/usr/bin/env python3
import sys
from pathlib import Path

# Разрешённые root директории (ADR-0005)
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

# Разрешённые root файлы
ALLOWED_ROOT_FILES = {
    "pyproject.toml",
    "README.md",
    ".gitignore",
    ".pre-commit-config.yaml",
}

def main():
    root = Path(".")

    violations = []

    for item in root.iterdir():
        if item.is_dir():
            if item.name not in ALLOWED_ROOT_DIRS:
                violations.append(f"Forbidden root directory: {item.name}")
        elif item.is_file():
            if item.name not in ALLOWED_ROOT_FILES:
                # игнорируем скрытые служебные файлы
                if not item.name.startswith("."):
                    violations.append(f"Unexpected root file: {item.name}")

    if violations:
        print("\n🚫 Repository structure violations detected:\n")
        for v in violations:
            print(v)

        print(
            "\nRepository Structure Lock (ADR-0005) violated.\n"
            "Adding new root directories requires a new ADR."
        )
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()