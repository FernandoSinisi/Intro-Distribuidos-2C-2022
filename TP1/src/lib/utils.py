import lib.constants as cte
import logging


def get_window_size(rdt_protocol):
    logger = logging.getLogger(__name__)
    logger.info(f"RDT protocol {rdt_protocol}")
    if rdt_protocol == cte.Protocol.UDP_GBN.value:
        logger.debug(f"window size {cte.GBN_WINDOW_SIZE}")
        return cte.GBN_WINDOW_SIZE
    else:
        logger.debug(f"window size {cte.SAW_WINDOW_SIZE}")
        return cte.SAW_WINDOW_SIZE
