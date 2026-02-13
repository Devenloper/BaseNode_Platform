# tests/architecture/test_boundaries.py

import ast
import pathlib


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]


def get_imports(path: pathlib.Path):
    tree = ast.parse(path.read_text())
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)

    return imports


# ----------------------------------------------------------
# Application must not import fastapi
# ----------------------------------------------------------

def test_application_does_not_import_fastapi():
    for path in PROJECT_ROOT.glob("application/**/*.py"):
        imports = get_imports(path)
        for module in imports:
            assert not module.startswith("fastapi"), (
                f"{path} imports fastapi ({module})"
            )


# ----------------------------------------------------------
# Domain must not import fastapi or sqlalchemy
# ----------------------------------------------------------

def test_domain_is_framework_free():
    for path in PROJECT_ROOT.glob("domain/**/*.py"):
        imports = get_imports(path)
        for module in imports:
            assert not module.startswith("fastapi"), (
                f"{path} imports fastapi ({module})"
            )
            assert not module.startswith("sqlalchemy"), (
                f"{path} imports sqlalchemy ({module})"
            )


# ----------------------------------------------------------
# Infrastructure must not import interface
# ----------------------------------------------------------

def test_infrastructure_does_not_import_interface():
    for path in PROJECT_ROOT.glob("infrastructure/**/*.py"):
        imports = get_imports(path)
        for module in imports:
            assert not module.startswith("interface"), (
                f"{path} imports interface ({module})"
            )