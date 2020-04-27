# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger("senaite.core")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing SENAITE.CORE ***")
