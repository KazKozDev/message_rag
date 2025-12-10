"""Logging configuration utilities."""

import logging
import logging.config
from pathlib import Path

import yaml


def setup_logging(config_path: str | None = None) -> None:
    """Configure logging from YAML file.

    Args:
        config_path: Path to logging configuration YAML file.
                    Defaults to config/logging_config.yaml.
    """
    if config_path is None:
        config_path = "config/logging_config.yaml"

    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file) as f:
            config = yaml.safe_load(f)
            # Ensure log directory exists
            log_dir = Path("data/outputs")
            log_dir.mkdir(parents=True, exist_ok=True)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.warning(f"Logging config not found at {config_path}, using defaults")


def get_logger(name: str) -> logging.Logger:
    """Get logger instance.

    Args:
        name: Logger name (typically __name__ of the module).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
