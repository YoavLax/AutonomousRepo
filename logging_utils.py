import logging
from typing import Optional

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
) -> logging.Logger:
    """
    Sets up and returns a logger with the specified name, log file, and level.

    Args:
        name (str): Name of the logger.
        log_file (Optional[str]): If provided, logs will be written to this file.
        level (int): Logging level (e.g., logging.INFO).
        fmt (str): Log message format.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(fmt)

    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
