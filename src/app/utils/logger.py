import logging

from ecs_logging import ECSFormatter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def get_logger(name: str):
    """
    Creates and configures a logger with the specified name.

    This function sets the logging level to INFO and adds a stream handler
    with an ECSFormatter to the logger.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(ECSFormatter())

    logger.addHandler(handler)
    return logger
