import logging
import sys
import os

def configure_log(verbosity, log_file):
    if not os.access("logs", os.R_OK | os.W_OK | os.X_OK):
        os.mkdir("logs")
    logging.basicConfig(
        format='%(asctime)s: %(name)s: %(levelname)s: %(message)s',
        level=verbosity,
        handlers=[logging.FileHandler(f"{log_file}"),logging.StreamHandler(sys.stdout)])
    logger = logging.getLogger(__name__)
    logger.debug('Logger configured')
