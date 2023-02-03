# under the terms of the MIT License; see LICENSE file for more details.import logging
"""Main file entry point."""
import logging
import sys
from .cli import lycophron


def init_logging():
    """Initialises logging in two steps:
    1 - adds a "user-friendly" logger that prints errors to stdout.
    2 - adds a "dev-only" logger tha prints errors to a file.
    """
    logger = logging.getLogger("lycophron")
    dev_logger = logging.getLogger("lycophron_dev")

    formatter = logging.Formatter("%(asctime)s : %(message)s")
    dev_formatter = logging.Formatter("%(asctime)s : %(message)s\n")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)

    dev_file_handler = logging.FileHandler("dev_logs.log")
    dev_file_handler.setLevel(logging.ERROR)
    dev_file_handler.setFormatter(dev_formatter)

    logger.addHandler(stdout_handler)
    dev_logger.addHandler(dev_file_handler)


if __name__ == "__main__":
    init_logging()
    lycophron()
