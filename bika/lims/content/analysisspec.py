# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import AnalysisSpecificationWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisSpec, IDeactivable
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import ComputedField
from Products.Archetypes.public import ComputedWidget
from Products.Archetypes.public import ReferenceWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.field.records import RecordsField
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate
from zope.interface import implements


schema = Schema((

    UIDReferenceField(
        'SampleType',
        vocabulary="getSampleTypes",
        allowed_types=('SampleType',),
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Sample Type"),
        ),
    ),

    ComputedField(
        'SampleTypeTitle',
        expression="context.getSampleType().Title() if context.getSampleType() else ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),

    ComputedField(
        'SampleTypeUID',
        expression="context.getSampleType().UID() if context.getSampleType() else ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
)) + BikaSchema.copy() + Schema((

    RecordsField(
        'ResultsRange',
        # schemata = 'Specifications',
        required=1,
        type='resultsrange',
        subfields=(
            'keyword',
            'min_operator',
            'min',
            'max_operator',
            'max',
            'warn_min',
            'warn_max',
            'hidemin',
            'hidemax',
            'rangecomment'
        ),
        required_subfields=('keyword',),
        subfield_validators={
            'min': 'analysisspecs_validator',
            'max': 'analysisspecs_validator',
        },
        subfield_labels={
            'keyword': _('Analysis Service'),
            'min_operator': _('Min operator'),
            'min': _('Min'),
            'max_operator': _('Max operator'),
            'max': _('Max'),
            'warn_min': _('Min warn'),
            'warn_max': _('Max warn'),
            'hidemin': _('< Min'),
            'hidemax': _('> Max'),
            'rangecomment': _('Range Comment'),
        },
        widget=AnalysisSpecificationWidget(
            checkbox_bound=0,
            label=_("Specifications"),
            description=_(
                "'Min' and 'Max' values indicate a valid results range. Any "
                "result outside this results range will raise an alert. 'Min "
                "warn' and 'Max warn' values indicate a shoulder range. Any "
                "result outside the results range but within the shoulder "
                "range will raise a less severe alert. If the result is out of "
                "range, the value set for '< Min' or '< Max' will be displayed "
                "in lists and results reports instead of the real result.")
        ),
    ),

    ComputedField(
        'ClientUID',
        expression="context.aq_parent.UID()",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
))

schema['description'].widget.visible = True
schema['title'].required = True


class AnalysisSpec(BaseFolder, HistoryAwareMixin):
    """Analysis Specification
    """
    implements(IAnalysisSpec, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the title if possible, else return the Sample type.
        Fall back on the instance's ID if there's no sample type or title.
        """
        title = ''
        if self.title:
            title = self.title
        else:
            sampletype = self.getSampleType()
            if sampletype:
                title = sampletype.Title()
        return safe_unicode(title).encode('utf-8')

    def contextual_title(self):
        parent = self.aq_parent
        if parent == self.bika_setup.bika_analysisspecs:
            return self.title + " (" + translate(_("Lab")) + ")"
        else:
            return self.title + " (" + translate(_("Client")) + ")"

    security.declarePublic('getResultsRangeDict')

    def getResultsRangeDict(self):
        """Return a dictionary with the specification fields for each
           service. The keys of the dictionary are the keywords of each
           analysis service. Each service contains a dictionary in which
           each key is the name of the spec field:
           specs['keyword'] = {'min': value,
                               'max': value,
                               'warnmin': value,
                               ... }
        """
        specs = {}
        subfields = self.Schema()['ResultsRange'].subfields
        for spec in self.getResultsRange():
            keyword = spec['keyword']
            specs[keyword] = {}
            for key in subfields:
                if key not in ['uid', 'keyword']:
                    specs[keyword][key] = spec.get(key, '')
        return specs

    security.declarePublic('getRemainingSampleTypes')

    def getSampleTypes(self, active_only=True):
        """Return all sampletypes
        """
        catalog = api.get_tool("bika_setup_catalog")
        query = {
            "portal_type": "SampleType",
            # N.B. The `sortable_title` index sorts case sensitive. Since there
            #      is no sort key for sample types, it makes more sense to sort
            #      them alphabetically in the selection
            "sort_on": "title",
            "sort_order": "ascending"
        }
        results = catalog(query)
        if active_only:
            results = filter(api.is_active, results)
        sampletypes = map(
            lambda brain: (brain.UID, brain.Title), results)
        return DisplayList(sampletypes)

    def getClientUID(self):
        return self.aq_parent.UID()


atapi.registerType(AnalysisSpec, PROJECTNAME)


class ResultsRangeDict(dict):

    def __init__(self, *arg, **kw):
        super(ResultsRangeDict, self).__init__(*arg, **kw)
        self["min"] = self.min
        self["max"] = self.max
        self["warn_min"] = self.warn_min
        self["warn_max"] = self.warn_max
        self["min_operator"] = self.min_operator
        self["max_operator"] = self.max_operator

    @property
    def min(self):
        return self.get("min", '')

    @property
    def max(self):
        return self.get("max", '')

    @property
    def warn_min(self):
        return self.get("warn_min", self.min)

    @property
    def warn_max(self):
        return self.get('warn_max', self.max)

    @property
    def min_operator(self):
        return self.get('min_operator', 'geq')

    @property
    def max_operator(self):
        return self.get('max_operator', 'leq')

    @min.setter
    def min(self, value):
        self["min"] = value

    @max.setter
    def max(self, value):
        self["max"] = value

    @warn_min.setter
    def warn_min(self, value):
        self['warn_min'] = value

    @warn_max.setter
    def warn_max(self, value):
        self['warn_max'] = value

    @min_operator.setter
    def min_operator(self, value):
        self['min_operator'] = value

    @max_operator.setter
    def max_operator(self, value):
        self['max_operator'] = value
