from logging import Logger, INFO, WARNING

# TODO load some configs from a higher level file
DEFAULT_LEVEL = INFO

class LycophronLogger(Logger):
    """Represents a lycophron specific logger.
    Adds configuration to the built-in logger."""

    level = DEFAULT_LEVEL
    name = 'lycophron'

    def __init__(self, name, level) -> None:
        super().__init__(name, level)