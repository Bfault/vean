import subprocess
import orjson
import os
from typing import Generator, Dict, List
from config import VeanConfig


def get_dynamic_modules(config: VeanConfig) -> List[str]:
    mathlib_path = config.extraction.mathlib_path
    if not os.path.exists(mathlib_path):
        raise FileNotFoundError(f"No Mathlib found at {mathlib_path}")
    blacklist = set(config.extraction.blacklist)
    modules = []
    for root, _, files in os.walk(mathlib_path):
        if any(b in root for b in blacklist):
            continue
        for file in files:
            if file.endswith('.lean'):
                rel_path = os.path.relpath(os.path.join(root, file), mathlib_path)
                mod_path = rel_path[:-5].replace(os.sep, '.')
                modules.append(f"Mathlib.{mod_path}")
    return sorted(modules)


def run_extraction_batch(modules: List[str], config: VeanConfig) -> Generator[Dict, None, None]:
    cmd = ['lake', 'exe', 'extractor'] + modules
    process = subprocess.Popen(
        cmd,
        cwd=config.extraction.extractor_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                yield orjson.loads(line)
            except orjson.JSONDecodeError:
                continue
    finally:
        process.wait()
