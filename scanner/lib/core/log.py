#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import logging
import sys
import traceback

from lib.core.data import paths

FORMATTER = logging.Formatter("\r[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

LOGGER = logging.getLogger("TopLog")

FILE_HANDLER = logging.FileHandler(paths.FIlELOG)
FILE_HANDLER.setFormatter(FORMATTER)

STDOUT_HANDLER = logging.StreamHandler(sys.stdout)
STDOUT_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STDOUT_HANDLER)
LOGGER.setLevel(logging.DEBUG)

def _error(msg):
    if any(sys.exc_info()):
        LOGGER.error("\n".join((msg,traceback.format_exc())))
        sys.exc_clear()
    else:
        LOGGER.error(msg+",But no exception detected,please check")


ERROR = _error
DEBUG = LOGGER.debug
INFO = LOGGER.info
WARN = LOGGER.warn






