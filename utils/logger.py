import logging


def setup_logging(level: str = "INFO", log_file: str | None = None):
    """Logs to the console, and to log_file too if one is given."""
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )
    # urllib3 is way too talkative
    logging.getLogger("urllib3").setLevel(logging.WARNING)
