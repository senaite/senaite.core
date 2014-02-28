import sys
import time
import transaction
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import ManageBika, PROJECTNAME, ARIMPORT_OPTIONS
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IARPriority
from bika.lims.jsonapi import resolve_request_lookup
from bika.lims.workflow import doActionFor
from bika.lims.utils import tmpID
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope import event
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    IntegerField('sortKey',
        widget = IntegerWidget(
            label = _("Sort Key"),
            description = _("Numeric value indicating the sort order of objects that are prioritised"),
        ),
    ),
    IntegerField('pricePremium',
        widget = IntegerWidget(
            label = _("Price Premium Percentage"),
            description = _("The percentage used to calculate the price for analyses done at this priority"),
        ),
    ),
    ImageField('smallIcon',
        widget = ImageWidget(
            label = _("Small Icon"),
            description = _("16x16 pixel icon used for the this priority in listings.")
        ),
    ),
    ImageField('bigIcon',
        widget = ImageWidget(
            label = _("Big Icon"),
            description = _("32x32 pixel icon used for the this priority in object views.")
        ),
    ),
    BooleanField('isDefault',
        widget = BooleanWidget(
            label = _("Default Priority?"),
            description = _("Check this box if this is the default priority")
        ),
    ),
))

schema['description'].widget.visible = True

class ARPriority(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements (IARPriority)
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)



atapi.registerType(ARPriority, PROJECTNAME)
