# -*- coding: utf-8 -*-

from bika.lims.api.security import check_permission

from .permissions import TransitionPublishResults
from .permissions import TransitionReceiveSample


def can_publish(context):
    """Checks if publication is allowed
    """
    return check_permission(TransitionPublishResults, context)


def can_receive(context):
    """Checks if a sample can be received
    """
    return check_permission(TransitionReceiveSample, context)
