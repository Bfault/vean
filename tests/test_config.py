from config import ContentConfig, ExtractionConfig, VeanConfig


def test_config_defaults():
    config = VeanConfig()
    assert config.extraction.batch_size == 50
    assert "Testing" in config.extraction.blacklist
    assert "Init." in config.extraction.noise_prefixes
    assert config.extraction.max_workers == 1
    assert config.content.max_content_size == 100000
    assert config.output.dataset_file == "vean_dataset.jsonl"


def test_config_custom_values():
    config = VeanConfig(
        extraction=ExtractionConfig(batch_size=10, max_workers=4)
    )
    assert config.extraction.batch_size == 10
    assert config.extraction.max_workers == 4
    assert config.extraction.timeout_seconds == 300  # default


def test_output_config_defaults():
    config = VeanConfig()
    assert config.output.progress_file == ".vean_progress.json"


def test_nested_config():
    config = VeanConfig(
        extraction=ExtractionConfig(blacklist=["Foo"]),
        content=ContentConfig(max_field_size=1000),
    )
    assert config.extraction.blacklist == ["Foo"]
    assert config.content.max_field_size == 1000
