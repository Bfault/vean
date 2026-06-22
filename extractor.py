import json
import os
import subprocess
import threading
from collections.abc import Generator

import orjson

from config import VeanConfig


def get_dynamic_modules(config: VeanConfig) -> list[str]:
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


class TimeoutError(Exception):
    pass


def run_extraction_batch(modules: list[str], config: VeanConfig) -> Generator[dict, None, None]:
    cmd = ['lake', 'exe', 'extractor'] + modules
    process = subprocess.Popen(
        cmd,
        cwd=config.extraction.extractor_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    timer = threading.Timer(config.extraction.timeout_seconds, process.kill)
    timer.start()

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
        timer.cancel()
        process.wait()
        if process.returncode == -9:
            raise TimeoutError(f"Batch timed out after {config.extraction.timeout_seconds}s")
        if process.returncode != 0:
            stderr_output = process.stderr.read() if process.stderr else ""
            import sys as _sys
            print(f"Warning: lake exe extractor exited with code {process.returncode}", file=_sys.stderr)
            if stderr_output:
                print(f"stderr: {stderr_output[:500]}", file=_sys.stderr)


def load_progress(progress_file: str) -> set:
    try:
        with open(progress_file) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_progress(progress_file: str, modules: set):
    with open(progress_file, 'w') as f:
        json.dump(sorted(modules), f)
