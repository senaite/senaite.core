# -*- coding:utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from types import DictType
from Products.Archetypes.utils import shasattr
from bika.lims.interfaces import IAcquireFieldDefaults
from zope.interface import implements
from Acquisition import aq_base, aq_inner, aq_parent

_marker = []


class AcquireFieldDefaults(object):
    """Default behaviour for IAcquireFieldDefaults.

    Simply works the way up the acquisition, looking for the specified (or
    identically named) field, and returns the found value.

    If no value is found, the original AT default is used.  In this case we return
    None, which is ignored by our handler in monkey/Field.py

    """
    implements(IAcquireFieldDefaults)

    def __init__(self, context):
        self.context = context
        self.sort = 1000

    def __call__(self, field):

        fieldname = field.getName()

        acquire = getattr(field, 'acquire', True)
        if type(acquire) == DictType:
            new_fieldname = acquire.get('fieldname', None)
            if new_fieldname:
                fieldname = new_fieldname

        current = self.context
        while hasattr(current, 'aq_parent'):
            current = current.aq_parent
            if IPloneSiteRoot.providedBy(current):
                break
            if fieldname in current.schema._names:
                value = current.schema[fieldname].get(current)
                if value is not None:
                    return value
