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

import json

import plone
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import StringWidget
from bika.lims import api
from bika.lims import logger
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IReferenceWidgetVocabulary
from bika.lims.utils import to_unicode as _u
from senaite.core.supermodel.model import SuperModel
from zope.component import getAdapters
from plone import protect


class ReferenceWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/referencewidget",
        'helper_js': ("bika_widgets/referencewidget.js",),
        'helper_css': ("bika_widgets/referencewidget.css",),

        'url': 'referencewidget_search',
        'catalog_name': 'portal_catalog',

        # base_query can be a dict or a callable returning a dict
        'base_query': {},

        # This will be faster if the columnNames are catalog indexes
        'colModel': [
            {'columnName': 'Title', 'width': '30', 'label': _(
                'Title'), 'align': 'left'},
            {'columnName': 'Description', 'width': '70', 'label': _(
                'Description'), 'align': 'left'},
            # UID is required in colModel
            {'columnName': 'UID', 'hidden': True},
        ],

        # Default field to put back into input elements
        'ui_item': 'Title',
        'search_fields': ('Title',),
        'discard_empty': [],
        'popup_width': '550px',
        'showOn': False,
        'searchIcon': True,
        'minLength': '0',
        'delay': '500',
        'resetButton': False,
        'sord': 'asc',
        'sidx': 'Title',
        'force_all': False,
        'portal_types': {},
    })
    security = ClassSecurityInfo()

    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """Return a UID so that ReferenceField understands.
        """
        fieldName = field.getName()
        if fieldName + "_uid" in form:
            uid = form.get(fieldName + "_uid", '')
            if field.multiValued and\
                    (isinstance(uid, str) or isinstance(uid, unicode)):
                uid = uid.split(",")
        elif fieldName in form:
            uid = form.get(fieldName, '')
            if field.multiValued and\
                    (isinstance(uid, str) or isinstance(uid, unicode)):
                uid = uid.split(",")
        else:
            uid = None
        return uid, {}

    def get_combogrid_options(self, context, fieldName):
        colModel = self.colModel
        if 'UID' not in [x['columnName'] for x in colModel]:
            colModel.append({'columnName': 'UID', 'hidden': True})
        options = {
            'url': self.url,
            'colModel': colModel,
            'showOn': self.showOn,
            'width': self.popup_width,
            'sord': self.sord,
            'sidx': self.sidx,
            'force_all': self.force_all,
            'search_fields': self.search_fields,
            'discard_empty': self.discard_empty,
            'minLength': self.minLength,
            'resetButton': self.resetButton,
            'searchIcon': self.searchIcon,
            'delay': self.delay,
        }
        return json.dumps(options)

    def get_base_query(self, context, fieldName):
        base_query = self.base_query
        if callable(base_query):
            base_query = base_query()
        if base_query and isinstance(base_query, basestring):
            base_query = json.loads(base_query)

        # portal_type: use field allowed types
        field = context.Schema().getField(fieldName)
        allowed_types = getattr(field, 'allowed_types', None)
        allowed_types_method = getattr(field, 'allowed_types_method', None)
        if allowed_types_method:
            meth = getattr(context, allowed_types_method)
            allowed_types = meth(field)
        # If field has no allowed_types defined, use widget's portal_type prop
        base_query['portal_type'] = allowed_types \
            if allowed_types \
            else self.portal_types

        return json.dumps(self.base_query)

    def initial_uid_field_value(self, value):
        if type(value) in (list, tuple):
            ret = ",".join([v.UID() for v in value])
        elif type(value) in [str, ]:
            ret = value
        else:
            ret = value.UID() if value else value
        return ret


registerWidget(ReferenceWidget, title='Reference Widget')

class ajaxReferenceWidgetSearch(BrowserView):
    """ Source for jquery combo dropdown box
    """

    @property
    def num_page(self):
        """Returns the number of page to render
        """
        return api.to_int(self.request.get("page", None), default=1)

    @property
    def num_rows_page(self):
        """Returns the number of rows per page to render
        """
        return api.to_int(self.request.get("rows", None), default=10)

    def get_field_names(self):
        """Return the field names to get values for
        """
        col_model = self.request.get("colModel", None)
        if not col_model:
            return ["UID",]

        names = []
        col_model = json.loads(_u(col_model))
        if isinstance(col_model, (list, tuple)):
            names = map(lambda c: c.get("columnName", "").strip(), col_model)

        # UID is used by reference widget to know the object that the user
        # selected from the popup list
        if "UID" not in names:
            names.append("UID")

        return filter(None, names)

    def get_data_record(self, brain, field_names):
        """Returns a dict with the column values for the given brain
        """
        record = {}
        model = None

        for field_name in field_names:
            # First try to get the value directly from the brain
            value = getattr(brain, field_name, None)

            # No metadata for this column name
            if value is None:
                logger.warn("Not a metadata field: {}".format(field_name))
                model = model or SuperModel(brain)
                value = model.get(field_name, None)
                if callable(value):
                    value = value()

            # '&nbsp;' instead of '' because empty div fields don't render
            # correctly in combo results table
            record[field_name] = value or "&nbsp;"

        return record

    def search(self):
        """Returns the list of brains that match with the request criteria
        """
        brains = []
        # TODO Legacy
        for name, adapter in getAdapters((self.context, self.request),
                                         IReferenceWidgetVocabulary):
            brains.extend(adapter())
        return brains

    def to_data_rows(self, brains):
        """Returns a list of dictionaries representing the values of each brain
        """
        fields = self.get_field_names()
        return map(lambda brain: self.get_data_record(brain, fields), brains)

    def to_json_payload(self, data_rows):
        """Returns the json payload
        """
        num_rows = len(data_rows)
        num_page = self.num_page
        num_rows_page = self.num_rows_page

        pages = num_rows / num_rows_page
        pages += divmod(num_rows, num_rows_page)[1] and 1 or 0
        start = (num_page - 1) * num_rows_page
        end = num_page * num_rows_page
        payload = {"page": num_page,
                   "total": pages,
                   "records": num_rows,
                   "rows": data_rows[start:end]}
        return json.dumps(payload)

    def __call__(self):
        protect.CheckAuthenticator(self.request)

        # Do the search
        brains = self.search()

        # Generate the data rows to display
        data_rows = self.to_data_rows(brains)

        # Return the payload
        return self.to_json_payload(data_rows)
