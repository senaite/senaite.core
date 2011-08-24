""" Force a new version to be created if the object is in TYPES_TO_VERSION """

from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims.config import TYPES_TO_VERSION
#from zope.lifecycleevent.interfaces import IObjectModifiedEvent

def ObjectModifiedEventHandler(event):

    if hasattr(event.object, 'portal_type') and\
       event.object.portal_type in TYPES_TO_VERSION:
        event.object.update_version_on_edit()
