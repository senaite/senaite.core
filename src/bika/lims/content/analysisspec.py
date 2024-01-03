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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import ResultsRangesField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import AnalysisSpecificationWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.clientawaremixin import ClientAwareMixin
from bika.lims.content.sampletype import SampleTypeAwareMixin
from bika.lims.interfaces import IAnalysisSpec
from bika.lims.interfaces import IDeactivable
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import Schema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFPlone.utils import safe_unicode
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.catalog import SETUP_CATALOG
from zope.i18n import translate
from zope.interface import implements

schema = Schema((

    UIDReferenceField(
        "SampleType",
        allowed_types=("SampleType",),
        required=1,
        widget=ReferenceWidget(
            label=_(
                "label_analysisspec_sampletype",
                default="Sample Type"),
            description=_(
                "description_analysisspec_sampletype",
                default="Select the sample type for this specification"),
            catalog=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
        )
    ),

    UIDReferenceField(
        "DynamicAnalysisSpec",
        allowed_types=("DynamicAnalysisSpec",),
        required=0,
        widget=ReferenceWidget(
            label=_(
                "label_analysisspec_dynamicspec",
                default="Dynamic Analysis Specification"),
            description=_(
                "description_analysisspec_dynamicspec",
                default="Link dynamic analysis specification"),
            catalog=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
        )
    ),

)) + BikaSchema.copy() + Schema((

    ResultsRangesField(
        'ResultsRange',
        required=1,
        widget=AnalysisSpecificationWidget(
            label=_("Specifications"),
            description=_(
                u"description_analysisspec_resultsrange",
                default=u"'Min' and 'Max' values indicate a valid results "
                        u"range. Any result outside this results range will "
                        u"raise an alert.<br/>"
                        u"'Min warn' and 'Max warn' values indicate a "
                        u"shoulder range. Any result outside the results "
                        u"range but within the shoulder range will raise a "
                        u"less severe alert.<br/>"
                        u"If the result is out of range, the value set for "
                        u"'&lt; Min' or '&gt; Max' will be displayed in lists "
                        u"and results reports instead of the real result. In "
                        u"such case, the value set for 'Out of range comment' "
                        u"will be displayed in results report as well"
            )
        ),
    ),
))

schema['description'].widget.visible = True
schema['title'].required = True


class AnalysisSpec(BaseFolder, HistoryAwareMixin, ClientAwareMixin,
                   SampleTypeAwareMixin):
    """Analysis Specification
    """
    implements(IAnalysisSpec, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the title if possible, else return the Sample type.
        Fall back on the instance's ID if there's no sample type or title.
        """
        if self.title:
            title = self.title
        else:
            title = self.getSampleTypeTitle() or ""
        return safe_unicode(title).encode('utf-8')

    def contextual_title(self):
        parent = self.aq_parent
        if parent == self.bika_setup.bika_analysisspecs:
            return self.title + " (" + translate(_("Lab")) + ")"
        else:
            return self.title + " (" + translate(_("Client")) + ")"


atapi.registerType(AnalysisSpec, PROJECTNAME)


class ResultsRangeDict(dict):

    def __init__(self, *arg, **kw):
        super(ResultsRangeDict, self).__init__(*arg, **kw)
        self["uid"] = self.uid
        self["min"] = self.min
        self["max"] = self.max
        self["error"] = self.error
        self["warn_min"] = self.warn_min
        self["warn_max"] = self.warn_max
        self["min_operator"] = self.min_operator
        self["max_operator"] = self.max_operator

    @property
    def uid(self):
        """The uid of the service this ResultsRange refers to
        """
        return self.get("uid", '')

    @property
    def min(self):
        return self.get("min", '')

    @property
    def max(self):
        return self.get("max", '')

    @property
    def error(self):
        return self.get("error", '')

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

    def __eq__(self, other):
        if isinstance(other, dict):
            other = ResultsRangeDict(other)

        if isinstance(other, ResultsRangeDict):
            # Balance both dicts with same keys, but without corrupting them
            current = dict(filter(lambda o: o[0] in other, self.items()))
            other = dict(filter(lambda o: o[0] in current, other.items()))

            # Ensure that all values are str (sometimes ranges are stored as
            # numeric values and sometimes are stored as str)
            current = dict(map(lambda o: (o[0], str(o[1])), current.items()))
            other = dict(map(lambda o: (o[0], str(o[1])), other.items()))

            # Check if both are equal
            return current == other

        return super(ResultsRangeDict, self).__eq__(other)
