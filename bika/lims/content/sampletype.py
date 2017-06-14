# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes import DisplayList
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseContent import BaseContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.sampletype import schema
from bika.lims.interfaces import ISampleType
from zope.interface import implements


class SampleType(BaseContent, HistoryAwareMixin):
    implements(ISampleType)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')

    def getDefaultLifetime(self):
        """ get the default retention period """
        settings = getToolByName(self, 'bika_setup')
        return settings.getDefaultSampleLifetime()

    def SamplePointsVocabulary(self):
        from bika.lims.content.samplepoint import SamplePoints
        return SamplePoints(self, allow_blank=False, lab_only=False)

    def setSamplePoints(self, value, **kw):
        """ For the moment, we're manually trimming the sampletype<>samplepoint
            relation to be equal on both sides, here.
            It's done strangely, because it may be required to behave strangely.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        # convert value to objects
        if value and type(value) == str:
            value = [bsc(UID=value)[0].getObject(), ]
        elif value and type(value) in (list, tuple) and type(value[0]) == str:
            value = [bsc(UID=uid)[0].getObject() for uid in value if uid]
        # Find all SamplePoints that were removed
        existing = self.Schema()['SamplePoints'].get(self)
        removed = existing and [s for s in existing if s not in value] or []
        added = value and [s for s in value if s not in existing] or []
        ret = self.Schema()['SamplePoints'].set(self, value, **kw)

        # finally be sure that we aren't trying to set None values here.
        removed = [x for x in removed if x]
        added = [x for x in added if x]

        for sp in removed:
            sampletypes = sp.getSampleTypes()
            if self in sampletypes:
                sampletypes.remove(self)
                sp.setSampleTypes(sampletypes)

        for sp in added:
            sp.setSampleTypes(list(sp.getSampleTypes()) + [self, ])

        return ret

    def getSamplePoints(self, **kw):
        return self.Schema()['SamplePoints'].get(self, **kw)

    def SampleMatricesVocabulary(self):
        from bika.lims.content.samplematrix import SampleMatrices
        return SampleMatrices(self, allow_blank=True)

    def ContainerTypesVocabulary(self):
        from bika.lims.content.containertype import ContainerTypes
        return ContainerTypes(self, allow_blank=True)


registerType(SampleType, PROJECTNAME)


def SampleTypes(self, instance=None, allow_blank=False):
    instance = instance or self
    bsc = getToolByName(instance, 'bika_setup_catalog')
    items = []
    for st in bsc(portal_type='SampleType',
                  inactive_state='active',
                  sort_on='sortable_title'):
        items.append((st.UID, st.Title))
    items = allow_blank and [['', '']] + list(items) or list(items)
    return DisplayList(items)
