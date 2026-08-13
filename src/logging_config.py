"""Central logging configuration for the Trading Intelligence Platform."""
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure project-wide logging with consistent formatting.

    Args:
        level: The logging level (default: INFO).
    """
    log_format = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Suppress noisy third-party loggers
    logging.getLogger("yfinance").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
