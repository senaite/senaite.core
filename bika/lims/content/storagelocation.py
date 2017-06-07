# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import *
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

SiteTitle = StringField(
    'SiteTitle',
    widget=StringWidget(
        label=_("Site Title"),
        description=_("Title of the site")
    )
)
SiteCode = StringField(
    'SiteCode',
    widget=StringWidget(
        label=_("Site Code"),
        description=_("Code for the site")
    )
)
SiteDescription = StringField(
    'SiteDescription',
    widget=StringWidget(
        label=_("Site Description"),
        description=_("Description of the site")
    )
)
LocationTitle = StringField(
    'LocationTitle',
    widget=StringWidget(
        label=_("Location Title"),
        description=_("Title of location")
    )
)
LocationCode = StringField(
    'LocationCode',
    widget=StringWidget(
        label=_("Location Code"),
        description=_("Code for the location")
    )
)
LocationDescription = StringField(
    'LocationDescription',
    widget=StringWidget(
        label=_("Location Description"),
        description=_("Description of the location")
    )
)
LocationType = StringField(
    'LocationType',
    widget=StringWidget(
        label=_("Location Type"),
        description=_("Type of location")
    )
)
ShelfTitle = StringField(
    'ShelfTitle',
    widget=StringWidget(
        label=_("Shelf Title"),
        description=_("Title of the shelf")
    )
)
ShelfCode = StringField(
    'ShelfCode',
    widget=StringWidget(
        label=_("Shelf Code"),
        description=_("Code the the shelf")
    )
)
ShelfDescription = StringField(
    'ShelfDescription',
    widget=StringWidget(
        label=_("Shelf Description"),
        description=_("Description of the shelf")
    )
)

schema = BikaSchema.copy() + Schema((
    SiteTitle,
    SiteCode,
    SiteDescription,
    LocationTitle,
    LocationCode,
    LocationDescription,
    LocationType,
    ShelfTitle,
    ShelfCode,
    ShelfDescription
))
schema['title'].widget.label = _('Address')
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
