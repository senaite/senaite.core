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

from Products.ATExtensions.field import RecordsField
from Products.Archetypes.Registry import registerField

from bika.lims import api
from bika.lims.browser.fields.resultrangefield import SUB_FIELDS
from bika.lims.browser.widgets import AnalysisSpecificationWidget
from bika.lims.catalog import SETUP_CATALOG


class ResultsRangesField(RecordsField):
    """A field that stores a list of results ranges
    """
    _properties = RecordsField._properties.copy()
    _properties.update({
        "type": "specifications",
        "subfields": map(itemgetter(0), SUB_FIELDS),
        "subfield_labels": dict(SUB_FIELDS),
        "subfield_validators": {
            "min": "analysisspecs_validator",
            "max": "analysisspecs_validator",
        },
        "required_subfields": ("keyword", ),
        "widget": AnalysisSpecificationWidget,
    })

    def get(self, instance, **kwargs):
        values = super(ResultsRangesField, self).get(instance, **kwargs)

        # If a keyword or an uid has been specified, return the result range
        # for that uid or keyword only
        if "search_by" in kwargs:
            uid_or_keyword = kwargs.get("search_by")
            if uid_or_keyword:
                return self.getResultRange(values, uid_or_keyword) or {}
            return {}

        # Convert the dict items to ResultRangeDict for easy handling
        from bika.lims.content.analysisspec import ResultsRangeDict
        return map(lambda val: ResultsRangeDict(dict(val.items())), values)

    def getResultRange(self, values, uid_keyword_service):
        if not uid_keyword_service:
            return None

        if api.is_object(uid_keyword_service):
            uid_keyword_service = api.get_uid(uid_keyword_service)

        key = "keyword"
        if api.is_uid(uid_keyword_service) and uid_keyword_service != "0":
            # We always assume a uid of "0" refers to portal
            key = "uid"

        # Find out the item for the given uid/keyword
        from bika.lims.content.analysisspec import ResultsRangeDict
        value = filter(lambda v: v.get(key) == uid_keyword_service, values)
        return value and ResultsRangeDict(dict(value[0].items())) or None

    def _to_dict(self, value):
        """Convert the records to persistent dictionaries
        """
        # Resolve items to guarantee all them have the key uid
        value = super(ResultsRangesField, self)._to_dict(value)
        return map(self.resolve_uid, value)

    def resolve_uid(self, raw_dict):
        """Returns a copy of the raw dictionary passed in, but with additional
        key "uid". It's value is inferred from "keyword" if present
        """
        value = raw_dict.copy()
        uid = value.get("uid")
        if api.is_uid(uid) and uid != "0":
            return value

        # uid key does not exist or is not valid, try to infere from keyword
        keyword = value.get("keyword")
        if keyword:
            query = dict(portal_type="AnalysisService", getKeyword=keyword)
            brains = api.search(query, SETUP_CATALOG)
            if len(brains) == 1:
                uid = api.get_uid(brains[0])
        value["uid"] = uid
        return value


registerField(ResultsRangesField, title="ResultsRanges",
              description="Used for storing a results ranges",)
