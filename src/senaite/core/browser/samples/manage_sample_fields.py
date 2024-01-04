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

import traceback

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from plone.memoize import view as viewcache
from plone.protect import PostOnly
from Products.Archetypes.interfaces import IField as IATField
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from senaite.core.registry import get_registry
from senaite.core.registry import get_registry_record
from senaite.core.registry import set_registry_record
from senaite.core.registry.schema import ISampleHeaderRegistry
from zope.component import getMultiAdapter
from zope.schema.interfaces import IField as IDXField
from ZPublisher.HTTPRequest import record as RequestRecord

_marker = object

REGISTRY_KEY_PREFIX = "sampleheader"


class ManageSampleFieldsView(BrowserView):
    """Manage Sample Fields
    """
    template = ViewPageTemplateFile("templates/manage_sample_fields.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        submitted = self.request.form.get("submitted", False)
        save = self.request.form.get("save", False)
        reset = self.request.form.get("reset", False)
        # Handle form save action
        if submitted and save:
            self.handle_form_save(request=self.request)
            self.request.response.redirect(self.page_url)
        # Handle form reset action
        elif submitted and reset:
            self.handle_form_reset(request=self.request)
            self.request.response.redirect(self.page_url)
        return self.template()

    @property
    @viewcache.memoize
    def context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_context_state")

    @property
    def page_url(self):
        return self.context_state.current_page_url()

    @property
    def fields(self):
        """Returns an ordered dict of all schema fields
        """
        return api.get_fields(self.context)

    def handle_form_save(self, request=None):
        """Handle form submission -> save

        Update all known registry records with the values from the request
        """
        PostOnly(request)
        config = self.get_configuration()
        for key, old_value in config.items():
            new_value = request.form.get(key, _marker)
            if new_value is _marker:
                continue
            # convert request records to plain dictionaries
            if isinstance(new_value, RequestRecord):
                new_value = dict(new_value)
            success = self.set_config(key, new_value)
            # return immediately if a record could not be set
            if not success:
                message = _("Failed to update registry records. "
                            "Please check the server log for details.")
                return self.add_status_message(message, level="warning")
        message = _("Changes saved.")
        return self.add_status_message(message)

    def handle_form_reset(self, request=None):
        """Handle form submission -> reset

        Set all known registry record values to `None`
        """
        PostOnly(request)
        identifier = ISampleHeaderRegistry.__identifier__
        registry = get_registry()
        for key in registry.records:
            if key.startswith(identifier):
                logger.info("Flushing registry key %s" % key)
                registry.records[key].value = None
        message = _("Configuration restored to default values.")
        self.add_status_message(message)

    def set_config(self, name, value, prefix=REGISTRY_KEY_PREFIX):
        """Set registry record by name

        :param name: Name of the registry record to update
        :param value: Value to set
        :returns: True if the record was updated successfully, otherwise False
        """
        if prefix:
            name = "{}_{}".format(REGISTRY_KEY_PREFIX, name)
        logger.info("Set registry record '{}' to value '{}'"
                    .format(name, value))
        try:
            set_registry_record(name, value)
        except (NameError, TypeError):
            exc = traceback.format_exc()
            logger.error("Failed to set registry record '{}' -> '{}'"
                         "\nTraceback: {}\nForgot to run the migration steps?"
                         .format(name, value, exc))
            return False
        return True

    def get_config(self, name, prefix=REGISTRY_KEY_PREFIX, default=None):
        """Get registry record value by name

        :param name: Name of the registry record to fetch
        :returns: Value of the registry record, otherwise the default
        """
        if prefix:
            name = "{}_{}".format(REGISTRY_KEY_PREFIX, name)
        # only return the default when the registry record is not set
        record = get_registry_record(name, default=_marker)
        if record is _marker:
            return default
        return record

    def get_header_fields(self):
        """Return the (re-arranged) fields

        :returns: Dictionary with ordered lists of field names
        """
        header_fields = {
            "prominent": [],
            "visible": [],
            "hidden": [],
        }

        for name, field in self.fields.items():
            if not self.is_field_visible(field):
                continue
            vis = self.get_field_visibility(field)
            header_fields[vis].append(name)

        return header_fields

    def get_field_info(self, name):
        """Return field information required for the template

        :param name: Name of the field
        :returns: Dictionary with template specific data
        """
        field = self.fields.get(name)
        label = self.get_field_label(field)
        description = self.get_field_description(field)
        required = self.is_field_required(field)
        return {
            "name": name,
            "field": field,
            "label": label,
            "description": description,
            "required": required,
        }

    def get_configuration(self):
        """Return the header fields configuration

        NOTE: This method is used in the sample header viewlet to render the
              fields according to their order and visibility.

        :returns: Field configuration dictionary for the sample header viewlet
        """
        show_standard_fields = self.get_config("show_standard_fields")
        prominent_columns = self.get_config("prominent_columns")
        standard_columns = self.get_config("standard_columns")
        prominent_fields = self.get_config("prominent_fields")
        standard_fields = self.get_config("standard_fields")
        field_visibility = self.get_config("field_visibility")

        # all available fields looked up from schema
        fields = self.get_header_fields()

        # Handle flushed or not set registry keys
        if show_standard_fields is None:
            show_standard_fields = True
        if prominent_columns is None:
            prominent_columns = 1
        if standard_columns is None:
            standard_columns = 3
        if prominent_fields is None:
            prominent_fields = fields["prominent"]
        if standard_fields is None:
            standard_fields = fields["visible"]
        if field_visibility is None:
            field_visibility = dict.fromkeys(self.fields.keys(), True)

        # Always update added or removed fields, e.g. when the sampling
        # workflow was activated or deactivated in the setup
        default_fields = fields["prominent"] + fields["visible"]
        configured_fields = prominent_fields + standard_fields

        added = set(default_fields).difference(configured_fields)
        removed = set(configured_fields).difference(default_fields)

        # add new appeard fields always to the standard fields
        standard_fields += added

        # remove fields from prominent and standard fields
        prominent_fields = filter(lambda f: f not in removed, prominent_fields)
        standard_fields = filter(lambda f: f not in removed, standard_fields)

        # make new fields visible
        field_visibility.update(dict.fromkeys(added, True))

        config = {
            "show_standard_fields": show_standard_fields,
            "prominent_columns": prominent_columns,
            "standard_columns": standard_columns,
            "prominent_fields": prominent_fields,
            "standard_fields": standard_fields,
            "field_visibility": field_visibility,
        }

        return config

    def get_field_visibility(self, field, default="hidden"):
        """Returns the field visibility in the header

        Possible return values are:

          - prominent: Rendered as a promient field
          - visible: Rendered as a odestandard field
          - hidden: Not displayed

        :param field: Field object
        :returns: Visibility string
        """
        widget = self.get_widget(field)
        visibility = widget.isVisible(
            self.context, mode="header_table", field=field)
        if visibility not in ["prominent", "visible"]:
            return default
        return visibility

    def get_field_label(self, field):
        """Get the field label

        :param field: Field object
        :returns: Label of the fields' widget
        """
        widget = self.get_widget(field)
        return getattr(widget, "label", "")

    def get_field_description(self, field):
        """Get the field description

        :param field: Field object
        :returns: Description of the fields' widget
        """
        widget = self.get_widget(field)
        return getattr(widget, "description", "")

    def get_widget(self, field):
        """Returns the widget of the field

        :param field: Field object
        :returns: Widget object
        """
        if self.is_at_field(field):
            return field.widget
        elif self.is_dx_field(field):
            raise NotImplementedError("DX widgets not yet needed")
        raise TypeError("Field %r is neither a DX nor an AT field")

    def is_field_visible(self, field):
        """Checks if the field is visible in view mode

        :param field: Field object
        :returns: True if field is visible, otherwise False
        """
        widget = self.get_widget(field)
        visibility = widget.isVisible(self.context, mode="view", field=field)
        return visibility == "visible"

    def is_field_required(self, field):
        """Check if the field is required

        :param field: Field object
        :returns: True if field is set to required, otherwise False
        """
        return getattr(field, "required", False)

    def is_at_field(self, field):
        """Check if the field is an AT field

        :param field: Field object
        :returns: True if field is an AT based field
        """
        return IATField.providedBy(field)

    def is_dx_field(self, field):
        """Check if the field is an DX field

        :param field: Field object
        :returns: True if field is an DX based field
        """
        return IDXField.providedBy(field)

    def add_status_message(self, message, level="info"):
        """Set a portal status message

        :param message: The status message to render
        :returns: None
        """
        self.context.plone_utils.addPortalMessage(message, level)
