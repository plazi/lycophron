import logging
from .app import LycophronApp

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    app = LycophronApp()
    try:
        app.initialize()
    except Exception:
        logger.warning("An error has been thrown. Please check error log.")