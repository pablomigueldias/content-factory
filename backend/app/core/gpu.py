import logging
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

_gpu_lock = threading.Lock()


@contextmanager
def gpu_lock(label: str = ""):
    logger.debug("Aguardando GPU lock (%s)", label)
    with _gpu_lock:
        logger.debug("GPU lock adquirido (%s)", label)
        try:
            yield
        finally:
            logger.debug("GPU lock liberado (%s)", label)