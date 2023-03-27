# -*- coding: utf-8 -*-

from bika.lims.api.security import check_permission
from .permissions import TransitionPublishResults


def can_publish(context):
    """Checks if publication is allowed
    """
    return check_permission(TransitionPublishResults, context)
