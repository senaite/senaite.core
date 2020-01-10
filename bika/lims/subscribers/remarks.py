# -*- coding: utf-8 -*-

from bika.lims import logger


def RemarksAddedEventHandler(event):
    """New Remarks Added
    """
    context = event.context
    history = event.history
    logger.info("New Remarks added for {}: {}"
                .format(repr(context), history[0]))
