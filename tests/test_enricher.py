from config import VeanConfig
from enricher import clean_content, enrich_entry, extract_dependencies


def test_clean_content_removes_hygiene_names():
    dirty = "inst._@.Mathlib.Foo.12345678._hygCtx._hyg.3"
    clean = clean_content(dirty)
    assert "inst" in clean
    assert "_hygCtx" not in clean
    assert "12345678" not in clean


def test_clean_content_preserves_normal_names():
    dirty = "NonUnitalSubalgebra.ext"
    clean = clean_content(dirty)
    assert clean == dirty


def test_clean_content_removes_long_hashes():
    dirty = "Foo.1234567890.Bar"
    clean = clean_content(dirty)
    assert "1234567890" not in clean


def test_extract_dependencies():
    proof = "NonUnitalSubalgebra.ext S T h"
    deps = extract_dependencies(proof, "MyThm", ["Init.", "Core."])
    assert "NonUnitalSubalgebra.ext" in deps
    assert "MyThm" not in deps


def test_extract_dependencies_filters_noise():
    proof = "Init.Foo.Core.Bar NonUnitalSubalgebra.ext"
    deps = extract_dependencies(proof, "MyThm", ["Init.", "Core."])
    assert "NonUnitalSubalgebra.ext" in deps
    assert "Init.Foo" not in deps
    assert "Core.Bar" not in deps


def test_enrich_entry_truncates_large_content():
    config = VeanConfig()
    config.content.max_content_size = 200
    config.content.max_field_size = 100
    raw = {
        "name": "Test.thm",
        "module": "Test",
        "docstring": "",
        "proposition": "A" * 300,
        "proof": "B" * 300,
    }
    entry = enrich_entry(raw, config)
    assert entry["content"].endswith("... [truncated]")
    assert entry["metadata"]["proposition"].endswith("... [truncated]")
    assert entry["metadata"]["proof"].endswith("... [truncated]")


def test_enrich_entry_basic():
    config = VeanConfig()
    raw = {
        "name": "Test.thm",
        "module": "Test.Module",
        "docstring": "A theorem",
        "proposition": "forall x, x = x",
        "proof": "rfl",
    }
    entry = enrich_entry(raw, config)
    assert entry["id"] == "Test.thm"
    assert "Doc: A theorem" in entry["content"]
    assert entry["metadata"]["module"] == "Test.Module"
    assert entry["metadata"]["type"] == "theorem"


def test_enrich_entry_clean_content():
    config = VeanConfig()
    raw = {
        "name": "Test.thm",
        "module": "Test",
        "docstring": "",
        "proposition": "inst._@.Foo.12345678._hygCtx._hyg.3",
        "proof": "",
    }
    entry = enrich_entry(raw, config)
    assert "_hygCtx" not in entry["content"]
