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
from bika.lims.content.schema.samplepoint import schema


class SamplePoint(BaseContent, HistoryAwareMixin):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')

    def SampleTypesVocabulary(self):
        from bika.lims.content.sampletype import SampleTypes
        return SampleTypes(self, allow_blank=False)

    def setSampleTypes(self, value, **kw):
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
        if not type(value) in (list, tuple):
            value = [value, ]
        # Find all SampleTypes that were removed
        existing = self.Schema()['SampleTypes'].get(self)
        removed = existing and [s for s in existing if s not in value] or []
        added = value and [s for s in value if s not in existing] or []
        ret = self.Schema()['SampleTypes'].set(self, value, **kw)

        # finally be sure that we aren't trying to set None values here.
        removed = [x for x in removed if x]
        added = [x for x in added if x]

        for st in removed:
            samplepoints = st.getSamplePoints()
            if self in samplepoints:
                samplepoints.remove(self)
                st.setSamplePoints(samplepoints)

        for st in added:
            st.setSamplePoints(list(st.getSamplePoints()) + [self, ])

        return ret

    def getSampleTypes(self, **kw):
        return self.Schema()['SampleTypes'].get(self, **kw)

    def getClientUID(self):
        return self.aq_parent.UID()


registerType(SamplePoint, PROJECTNAME)


def SamplePoints(self, instance=None, allow_blank=True, lab_only=True):
    instance = instance or self
    bsc = getToolByName(instance, 'bika_setup_catalog')
    items = []
    contentFilter = {
        'portal_type': 'SamplePoint',
        'inactive_state': 'active',
        'sort_on': 'sortable_title'}
    if lab_only:
        lab_path = instance.bika_setup.bika_samplepoints.getPhysicalPath()
        contentFilter['path'] = {"query": "/".join(lab_path), "level": 0}
    for sp in bsc(contentFilter):
        sp = sp.getObject()
        if sp.aq_parent.portal_type == 'Client':
            sp_title = "{}: {}".format(sp.aq_parent.Title(), sp.Title())
        else:
            sp_title = sp.Title()
        items.append((sp.UID(), sp_title))
    items = allow_blank and [['', '']] + list(items) or list(items)
    return DisplayList(items)
