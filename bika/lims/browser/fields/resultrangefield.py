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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from operator import itemgetter

from Products.ATExtensions.field import RecordField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.interfaces import IFieldDefaultProvider
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces.analysis import IRequestAnalysis


# A tuple of (subfield_id, subfield_label,)
SUB_FIELDS = (
    ("keyword", _("Analysis Service")),
    ("min_operator", _("Min operator")),
    ("min", _('Min')),
    ("max_operator", _("Max operator")),
    ("max", _('Max')),
    ("warn_min", _('Min warn')),
    ("warn_max", _('Max warn')),
    ("hidemin", _('< Min')),
    ("hidemax", _('> Max')),
    ("rangecomment", _('Range Comment')),
)


class ResultRangeField(RecordField):
    """A field that stores a results range
    """
    _properties = RecordField._properties.copy()
    _properties.update({
        "type": "results_range_field",
        "subfields": map(itemgetter(0), SUB_FIELDS),
        "subfield_labels": dict(SUB_FIELDS),
    })

    def set(self, instance, value, **kwargs):
        if isinstance(value, ResultsRangeDict):
            # Better store a built-in dict so it will always be available even
            # if ResultsRangeDict is removed or changed
            value = dict(value)

        super(ResultRangeField, self).set(instance, value, **kwargs)

    def get(self, instance, **kwargs):
        value = super(ResultRangeField, self).get(instance, **kwargs)
        if value:
            return ResultsRangeDict(dict(value.items()))
        return {}


registerField(ResultRangeField, title="ResultRange",
              description="Used for storing a result range",)


class DefaultResultsRangeProvider(object):
    """Default Results Range provider for analyses
    This is used for backwards-compatibility for when the analysis' ResultsRange
    was obtained directly from Sample's ResultsRanges field, before this:
    https://github.com/senaite/senaite.core/pull/1506
    """
    implements(IFieldDefaultProvider)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        """Get the default value.
        """
        if not IRequestAnalysis.providedBy(self.context):
            return {}

        # Get the AnalysisRequest to look at
        analysis = self.context
        sample = analysis.getRequest()
        if not sample:
            return {}

        # Search by keyword
        field = sample.getField("ResultsRange")
        keyword = analysis.getKeyword()
        rr = field.get(sample, search_by=keyword)
        if rr:
            return rr

        # Try with uid (this shouldn't be necessary)
        service_uid = analysis.getServiceUID()
        return field.get(sample, search_by=service_uid) or {}


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