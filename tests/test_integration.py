import subprocess
import orjson
import os

EXTRACTOR_DIR = "Extractor"


def _mathlib_available():
    return os.path.exists(os.path.join(EXTRACTOR_DIR, ".lake", "packages", "mathlib"))


def test_extract_small_module():
    """Vérifie que l'extraction d'un petit module fonctionne et produit du JSONL valide."""
    if not _mathlib_available():
        import pytest
        pytest.skip("Mathlib not installed")

    cmd = ["lake", "exe", "extractor", "Mathlib.Algebra.Group.Defs"]
    result = subprocess.run(
        cmd,
        cwd=EXTRACTOR_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"stderr: {result.stderr[:500]}"

    lines = [l.strip() for l in result.stdout.split("\n") if l.strip()]
    assert len(lines) >= 2  # preflight + au moins 1 théorème

    # Première ligne = préflight
    preflight = orjson.loads(lines[0])
    assert "total_theorems" in preflight
    assert preflight["total_theorems"] > 0

    # Lignes suivantes = théorèmes
    for line in lines[1:]:
        entry = orjson.loads(line)
        assert "name" in entry
        assert "module" in entry
        assert "proposition" in entry
        assert not entry["name"].startswith("_")
        assert "._proof_" not in entry["name"]


def test_extract_no_name_starts_with_underscore():
    """Vérifie qu'aucun nom extrait ne commence par _ (filtrage Lean)."""
    if not _mathlib_available():
        import pytest
        pytest.skip("Mathlib not installed")

    cmd = ["lake", "exe", "extractor", "Mathlib.Algebra.Group.Defs"]
    result = subprocess.run(
        cmd,
        cwd=EXTRACTOR_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    lines = [l.strip() for l in result.stdout.split("\n") if l.strip()]
    for line in lines[1:]:
        entry = orjson.loads(line)
        assert not entry["name"].startswith("_"), f"Bad name: {entry['name']}"
