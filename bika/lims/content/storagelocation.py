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
            label=_("Site Title"),
            description=_("Title of the site"),
        ),
    ),
    StringField('SiteCode',
        widget=StringWidget(
            label=_("Site Code"),
            description=_("Code for the site"),
        ),
    ),
    StringField('SiteDescription',
        widget=StringWidget(
            label=_("Site Description"),
            description=_("Description of the site"),
        ),
    ),
    StringField('LocationTitle',
        widget=StringWidget(
            label=_("Location Title"),
            description=_("Title of location"),
        ),
    ),
    StringField('LocationCode',
        widget=StringWidget(
            label=_("Location Code"),
            description=_("Code for the location"),
        ),
    ),
    StringField('LocationDescription',
        widget=StringWidget(
            label=_("Location Description"),
            description=_("Description of the location"),
        ),
    ),
    StringField('LocationType',
        widget=StringWidget(
            label=_("Location Type"),
            description=_("Type of location"),
        ),
    ),
    StringField('ShelfTitle',
        widget=StringWidget(
            label=_("Shelf Title"),
            description=_("Title of the shelf"),
        ),
    ),
    StringField('ShelfCode',
        widget=StringWidget(
            label=_("Shelf Code"),
            description=_("Code the the shelf"),
        ),
    ),
    StringField('ShelfDescription',
        widget=StringWidget(
            label=_("Shelf Description"),
            description=_("Description of the shelf"),
        ),
    ),
))
schema['title'].widget.label=_('Address')
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
