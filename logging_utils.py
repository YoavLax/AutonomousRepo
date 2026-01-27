import logging
from typing import Optional

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    fmt: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
) -> logging.Logger:
    """
    Sets up and returns a logger with the specified name, log file, and level.

    Args:
        name (str): Name of the logger.
        log_file (Optional[str]): If provided, logs will be written to this file.
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
        fmt (str): Log message format.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(fmt)

    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler if log_file is specified
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

    return logger

# Example usage:
if __name__ == "__main__":
    log = setup_logger("test_logger", "test.log", logging.DEBUG)
    log.info("Logger initialized.")
    log.debug("This is a debug message.")
    log.error("This is an error message.")