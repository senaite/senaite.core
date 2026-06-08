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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

import Missing
from Acquisition import aq_base
from Acquisition import aq_inner
from bika.lims import api
from bika.lims.interfaces import IClient
from Products.CMFPlone.utils import base_hasattr
from senaite.core import logger
from senaite.core.interfaces import IReferenceWidgetDataProvider
from zope.interface import implementer

_marker = object()
MISSING_VALUES = [_marker, Missing.Value]

CONTACT_FIELD_NAMES = ("PrimaryContact", "Contact", "CCContact", "CCContacts")


def get_base_field_name(field_name):
    """Return the base field name, stripping any arnum suffix.

    The sample add form renames fields as 'FieldName-N' where N is the
    sample column index. This strips the suffix to get the base name.

    :param field_name: Field name, possibly with arnum suffix
    :returns: Base field name string
    """
    if field_name and "-" in field_name:
        return field_name.rsplit("-", 1)[0]
    return field_name or ""


SCOPE_ICONS = {
    "LabContact": (
        '<i class="fas fa-flask" title="Lab Contact"></i>'
    ),
    "Contact": (
        '<i class="fas fa-user" title="Client Contact"></i>'
    ),
    "GlobalContact": (
        '<i class="fas fa-globe" title="Global Contact"></i>'
    ),
}


def get_scope_icon(reference):
    """Return HTML icon for a contact reference.

    Distinguishes between:
    - LabContact: lab staff contact
    - Contact under a Client: client-local contact
    - Contact NOT under a Client: global contact

    :param reference: Catalog brain, AT/DX object or UID
    :returns: HTML string with FontAwesome icon
    """
    portal_type = getattr(reference, "portal_type", None)
    if portal_type is None:
        obj = api.get_object(reference)
        portal_type = getattr(obj, "portal_type", "")
    if portal_type == "LabContact":
        return SCOPE_ICONS["LabContact"]
    if portal_type != "Contact":
        return ""
    parent = api.get_parent(reference)
    if IClient.providedBy(parent):
        return SCOPE_ICONS["Contact"]
    return SCOPE_ICONS["GlobalContact"]


@implementer(IReferenceWidgetDataProvider)
class ReferenceWidgetDataProvider(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def get_field_name(self):
        """Return the field name
        """
        return self.request.get("field_name", None)

    def get_columns(self):
        """Return the requested columns
        """
        columns = self.request.get("column_names", [])
        if api.is_string(columns):
            # seems to be converted to string only if only one column exists.
            return [columns]
        return columns

    def lookup(self, brain_or_object, name, default=None):
        """Lookup a named attribute on the brain/object
        """
        if base_hasattr(brain_or_object, name):
            value = getattr(aq_base(aq_inner(brain_or_object)), name, _marker)
        else:
            value = _marker

        # wake up the object
        if value is _marker:
            logger.info("No catalog metadata found for '{name}'"
                        "in catalog {catalog}. Waking up the object!".format(
                            name=name, catalog=brain_or_object.aq_parent.id))
            obj = api.get_object(brain_or_object)
            value = getattr(obj, name, default)

        # Fallback to the default value if we do not have a catalog metadata
        if value in MISSING_VALUES:
            value = default

        if callable(value):
            value = value()

        try:
            json.dumps(value)
            return value
        except TypeError:
            # not JSON serializable
            return default

    def get_base_info(self, brain_or_object):
        """Return the base information for the brain or object
        """
        id = self.lookup(brain_or_object, "getId", "")
        title = self.lookup(brain_or_object, "Title", "")
        description = self.lookup(brain_or_object, "Description", "")
        return {
            "id": id,
            "getId": id,
            "uid": api.get_uid(brain_or_object),
            "url": api.get_url(brain_or_object),
            "Title": title or id,
            "title": title or id,
            "Description": description,
            "description": description,
            "review_state": api.get_review_status(brain_or_object),
        }

    def to_dict(self, reference, data=None, **kw):
        """Return the required data for the given object or uid

        :param reference: Catalog Brain, AT/DX object or UID
        :param data: Dictionary of collected data
        """
        info = {}

        if isinstance(data, dict):
            info.update(data)

        # Fetch the object if an UID is passed
        if api.is_uid(reference):
            brain_or_object = api.get_object(reference)
        else:
            brain_or_object = reference

        # always include base information
        info.update(self.get_base_info(brain_or_object))

        columns = self.get_columns()

        # always include all brain metadata
        if api.is_brain(brain_or_object):
            columns.extend(brain_or_object.schema())

        for column in columns:
            if column not in info:
                info[column] = self.lookup(
                    brain_or_object, column, default="")

        # Add scope icon for contact fields regardless of context
        field_name = get_base_field_name(self.get_field_name())
        if field_name in CONTACT_FIELD_NAMES:
            info["scope"] = get_scope_icon(reference)

        return info


class ClientReferenceWidgetDataProvider(ReferenceWidgetDataProvider):
    """Data provider for reference widgets on Client context.
    """


class AnalysisRequestReferenceWidgetDataProvider(ReferenceWidgetDataProvider):
    """Data provider for reference widgets on AnalysisRequest context.
    """
