# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import *
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from zope.interface import implements

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
    implements(IDeactivable)
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
