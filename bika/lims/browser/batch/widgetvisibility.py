# -*- coding:utf-8 -*-
from bika.lims.interfaces import IATWidgetVisibility
from zope.interface import implements

_marker = []


class BatchClientFieldWidgetVisibility(object):
    """If the Batch Client field has a value, then ARs created in that bach should
    have their Client field pre-selected and hidden.

    If there is no value in the Batch/Client field, then this field must be forced
    visible in the Add form.
    """
    implements(IATWidgetVisibility)

    def __init__(self, context):
        self.context = context
        self.sort = 5

    def __call__(self, context, mode, field, default):
        parent = context.aq_parent
        state = default if default else 'visible'
        fieldName = field.getName()
        if fieldName == 'Client' and parent.portal_type == 'Batch':
            client = parent.Schema()['Client'].get(parent)
            return 'hidden' if client else 'edit'
        return state
