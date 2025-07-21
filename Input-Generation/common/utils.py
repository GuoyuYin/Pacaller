# common/utils.py
import json
from pathlib import Path
from typing import Dict, Any, Optional
from common.logger import setup_logger

logger = setup_logger()

def ensure_dir(path: Path):
    """Ensures a directory exists, creating it if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise

def load_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """Loads a JSON file from the given path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load or parse JSON file {file_path}: {e}")
        return None

def write_file(path: Path, content: str):
    """Writes content to a file."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.debug(f"Successfully wrote to {path}")
    except IOError as e:
        logger.error(f"Failed to write to file {path}: {e}")
        raise