# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.


from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import registerType
from Products.CMFPlone.utils import safe_unicode
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import ISamplePartition
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    ReferenceField('Container',
        allowed_types=('Container',),
        relationship='SamplePartitionContainer',
        required=1,
        multiValued=0,
    ),
    ReferenceField('Preservation',
        allowed_types=('Preservation',),
        relationship='SamplePartitionPreservation',
        required=0,
        multiValued=0,
    ),
    BooleanField('Separate',
        default=False
    ),
    UIDReferenceField('Analyses',
        allowed_types=('Analysis',),
        required=0,
        multiValued=1,
    ),
    DateTimeField('DatePreserved',
    ),
    StringField('Preserver',
        searchable=True
    ),
    DurationField('RetentionPeriod',
    ),
)
)

schema['title'].required = False


class SamplePartition(BaseContent, HistoryAwareMixin):
    implements(ISamplePartition)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Sample ID as title """
        return safe_unicode(self.getId()).encode('utf-8')


registerType(SamplePartition, PROJECTNAME)
