"""Self-consistency coverage for pyproject.toml (added 2026-07-18).

This is not a build test - actually invoking `python -m build` and
`pip install` in every CI run is slow and adds a build-tool dependency
just to run the unit suite, so that's a manual/release-time check, not
something this file re-proves on every commit (see the isolated-venv
wheel-install run done by hand when pyproject.toml was first added,
which did prove the schema JSON files travel correctly as real package
data and the plg-evidence console script resolves from outside the
repo - not repeated here).

What *this* file guards against is quieter: pyproject.toml's declared
dependency pins silently drifting away from requirements.txt (the file
CI's own `pip install -r requirements.txt` step actually reads - see
.github/workflows/tests.yml), and the `plg-evidence` console-script
target silently drifting away from evidence/cli.py's real callable, in
either case without anything failing loudly until someone tries a
fresh install.
"""

import pathlib
import sys
import tomllib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"


def _load_pyproject() -> dict:
    return tomllib.loads(PYPROJECT_PATH.read_text())


def _requirements_pins() -> dict[str, str]:
    """Parse requirements.txt's `pkg==version` lines into a dict.

    Deliberately simple (exact `==` pins only, one per line) rather
    than a general requirements-file parser - that's what this repo's
    requirements.txt actually contains, and a general parser would
    hide the day someone adds a marker or range this check can't
    compare against pyproject.toml.
    """
    pins = {}
    for line in REQUIREMENTS_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        assert "==" in line, (
            f"requirements.txt line {line!r} is not an exact `pkg==version` "
            f"pin - test_packaging.py's comparison against pyproject.toml "
            f"dependencies assumes exact pins throughout this file."
        )
        name, version = line.split("==", 1)
        pins[name.strip().lower()] = version.strip()
    return pins


def test_pyproject_is_valid_toml_with_expected_shape():
    data = _load_pyproject()
    assert data["project"]["name"] == "payloadguard-evidence"
    assert "dependencies" in data["project"]


def test_runtime_dependencies_match_requirements_txt_pins():
    """Every runtime dep in pyproject.toml must match requirements.txt's
    pin exactly - not "compatible", not "close enough". Runtime deps
    only: pytest is deliberately excluded from pyproject.toml's
    dependencies (it's declared under [project.optional-dependencies]
    "test" instead, since an installed CLI tool doesn't need pytest to
    run) even though it IS pinned in requirements.txt for CI's own use,
    so this loop does not expect pytest to appear on both sides.
    """
    pyproject_deps = _load_pyproject()["project"]["dependencies"]
    requirements_pins = _requirements_pins()

    assert pyproject_deps, "pyproject.toml declares no runtime dependencies"

    for dep in pyproject_deps:
        assert "==" in dep, (
            f"pyproject.toml dependency {dep!r} is not an exact pin - "
            f"this repo pins everything exactly in requirements.txt, "
            f"pyproject.toml should match that convention."
        )
        name, version = dep.split("==", 1)
        name = name.strip().lower()
        version = version.strip()
        assert name in requirements_pins, (
            f"pyproject.toml declares a runtime dependency on {name!r} "
            f"that does not appear in requirements.txt at all."
        )
        assert requirements_pins[name] == version, (
            f"pyproject.toml pins {name!r} to {version!r} but "
            f"requirements.txt pins it to {requirements_pins[name]!r} - "
            f"these must not silently drift apart."
        )


def test_console_script_points_at_a_real_callable_main():
    data = _load_pyproject()
    scripts = data["project"]["scripts"]
    assert "plg-evidence" in scripts
    target = scripts["plg-evidence"]
    module_path, _, attr = target.partition(":")
    assert module_path == "evidence.cli" and attr == "main", (
        f"plg-evidence entry point is {target!r}, expected "
        f"'evidence.cli:main' - if evidence/cli.py's real entry point "
        f"function was ever renamed, this would otherwise ship a wheel "
        f"whose console script fails at invocation time, not install "
        f"time."
    )

    from evidence.cli import main  # noqa: E402
    assert callable(main)


def test_schema_json_files_are_declared_as_package_data():
    data = _load_pyproject()
    package_data = data["tool"]["setuptools"]["package-data"]
    assert "evidence.schema" in package_data
    assert "*.json" in package_data["evidence.schema"], (
        "evidence/schema/*.json must be declared under "
        "[tool.setuptools.package-data] or a built wheel silently "
        "drops the schema files a fresh install needs at runtime - "
        "this was proven by hand with a real wheel build+install into "
        "an isolated venv when pyproject.toml was added; this test "
        "only guards the declaration from later regressing."
    )

    schema_files = sorted(p.name for p in (REPO_ROOT / "evidence" / "schema").glob("*.json"))
    assert schema_files, "evidence/schema/ has no *.json files to package - fixture drift?"
