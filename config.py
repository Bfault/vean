import sys
from dataclasses import dataclass, field
from typing import List

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class ExtractionConfig:
    batch_size: int = 50
    mathlib_path: str = "Extractor/.lake/packages/mathlib/Mathlib"
    blacklist: List[str] = field(
        default_factory=lambda: ["Testing", "Deprecated", "Tactic", "Util", "Lean"]
    )
    noise_prefixes: List[str] = field(
        default_factory=lambda: [
            "Init.", "Core.", "Eq.", "Iff.", "And.", "Or.",
            "Not.", "True.", "False.", "Exists.",
        ]
    )
    timeout_seconds: int = 300
    extractor_dir: str = "Extractor"


@dataclass
class ContentConfig:
    max_content_size: int = 100000
    max_field_size: int = 50000


@dataclass
class OutputConfig:
    dataset_file: str = "vean_dataset.jsonl"
    progress_file: str = ".vean_progress.json"


@dataclass
class VeanConfig:
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    content: ContentConfig = field(default_factory=ContentConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


def load_config(path: str = "vean_config.toml") -> VeanConfig:
    if tomllib is not None:
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            extraction = ExtractionConfig(**data.get("extraction", {}))
            content = ContentConfig(**data.get("content", {}))
            output = OutputConfig(**data.get("output", {}))
            return VeanConfig(extraction=extraction, content=content, output=output)
        except FileNotFoundError:
            pass
    return VeanConfig()
