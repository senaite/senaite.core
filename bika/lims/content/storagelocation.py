from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.browser import BrowserView
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.browser.fields import CoordinateField
from bika.lims.browser.widgets import CoordinateWidget
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims import PMF, bikaMessageFactory as _
from zope.interface import implements
import json
import plone
import sys

schema = BikaSchema.copy() + Schema((
    StringField('SiteTitle',
        widget=StringWidget(
            label = "Site Title",
            description = "Title of the site",
        ),
    ),
    StringField('SiteCode',
        widget=StringWidget(
            label = "Site Code",
            description = "Code for the site",
        ),
    ),
    StringField('SiteDescription',
        widget=StringWidget(
            label = "Site Description",
            description = "Description of the site",
        ),
    ),
    StringField('LocationTitle',
        widget=StringWidget(
            label = "Location Title",
            description = "Title of location",
        ),
    ),
    StringField('LocationCode',
        widget=StringWidget(
            label = "Location Code",
            description = "Code for the location",
        ),
    ),
    StringField('LocationDescription',
        widget=StringWidget(
            label = "Location Description",
            description = "Description of the location",
        ),
    ),
    StringField('LocationType',
        widget=StringWidget(
            label = "Location Type",
            description = "Type of location",
        ),
    ),
    StringField('ShelfTitle',
        widget=StringWidget(
            label = "Shelf Title",
            description = "Title of the shelf",
        ),
    ),
    StringField('ShelfCode',
        widget=StringWidget(
            label = "Shelf Code",
            description = "Code the the shelf",
        ),
    ),
    StringField('ShelfDescription',
        widget=StringWidget(
            label = "Shelf Description",
            description = "Description of the shelf",
        ),
    ),
))
schema['title'].widget.label = 'Address'
schema['description'].widget.visible = True

class StorageLocation(BaseContent, HistoryAwareMixin):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')


registerType(StorageLocation, PROJECTNAME)

#def StorageLocations(self, instance=None, allow_blank=True, lab_only=True):
#    instance = instance or self
#    bsc = getToolByName(instance, 'bika_setup_catalog')
#    items = []
#    contentFilter = {
#        'portal_type'  : 'StorageLocation',
#        'inactive_state'  :'active',
#        'sort_on' : 'sortable_title'}
#    if lab_only:
#        lab_path = instance.bika_setup.bika_storagelocations.getPhysicalPath()
#        contentFilter['path'] = {"query": "/".join(lab_path), "level" : 0 }
#    for sp in bsc(contentFilter):
#        items.append((sp.UID, sp.Title))
#    items = allow_blank and [['','']] + list(items) or list(items)
#    return DisplayList(items)
