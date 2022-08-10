# -*- coding: utf-8 -*-

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
        if submitted and save:
            self.handle_form_submit(request=self.request)
            self.request.response.redirect(self.page_url)
        elif submitted and reset:
            self.reset_configuration()
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

    def handle_form_submit(self, request=None):
        """Handle form submission
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
            self.set_config(key, new_value)
        message = _("Changes saved.")
        self.add_status_message(message)

    @property
    def fields(self):
        """Returns an ordered dict of all schema fields
        """
        return api.get_fields(self.context)

    def get_header_fields(self):
        """Return the (re-arranged) fields
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

    def set_config(self, name, value):
        """Lookup name in the config, otherwise return default
        """
        registry_name = "{}_{}".format(REGISTRY_KEY_PREFIX, name)
        set_registry_record(registry_name, value)

    def get_config(self, name, default=None):
        """Lookup registry record value

        NOTE: This method returns
        """
        registry_name = "{}_{}".format(REGISTRY_KEY_PREFIX, name)
        record = get_registry_record(registry_name, default=_marker)
        if record is _marker:
            return default
        return record

    def get_configuration(self):
        """Return the header fields configuration
        """
        show_standard_fields = self.get_config("show_standard_fields")
        prominent_columns = self.get_config("prominent_columns")
        standard_columns = self.get_config("standard_columns")
        prominent_fields = self.get_config("prominent_fields")
        standard_fields = self.get_config("standard_fields")
        field_visibility = self.get_config("field_visibility")

        # Handle flushed or not set registry keys
        if show_standard_fields is None:
            show_standard_fields = True
        if prominent_columns is None:
            prominent_columns = 1
        if standard_columns is None:
            standard_columns = 3

        if not all([prominent_fields, standard_fields, field_visibility]):
            fields = self.get_header_fields()

            if prominent_fields is None:
                prominent_fields = fields["prominent"]

            if standard_fields is None:
                standard_fields = fields["visible"]

            if field_visibility is None:
                field_visibility = dict.fromkeys(self.fields.keys(), True)

        config = {
            "show_standard_fields": show_standard_fields,
            "prominent_columns": prominent_columns,
            "standard_columns": standard_columns,
            "prominent_fields": prominent_fields,
            "standard_fields": standard_fields,
            "field_visibility": field_visibility,
        }

        return config

    def reset_configuration(self):
        """Reset configuration to default values
        """
        identifier = ISampleHeaderRegistry.__identifier__
        registry = get_registry()
        for key in registry.records:
            if key.startswith(identifier):
                logger.info("Flushing registry key %s" % key)
                registry.records[key].value = None
        message = _("Configuration restored to default values.")
        self.add_status_message(message)

    def get_field_visibility(self, field, default="hidden"):
        """Returns the field visibility in the header

        Possible values are:

          - prominent: Rendered as a promient field
          - visible: Rendered as a odestandard field
          - hidden: Not displayed
        """
        widget = self.get_widget(field)
        visibility = widget.isVisible(
            self.context, mode="header_table", field=field)
        if visibility not in ["prominent", "visible"]:
            return default
        return visibility

    def get_field_label(self, field):
        """Get the field label
        """
        widget = self.get_widget(field)
        return getattr(widget, "label", "")

    def get_field_description(self, field):
        """Get the field description
        """
        widget = self.get_widget(field)
        return getattr(widget, "description", "")

    def get_widget(self, field):
        """Returns the widget of the field
        """
        if self.is_at_field(field):
            return field.widget
        elif self.is_dx_field(field):
            raise NotImplementedError("DX widgets not yet needed")
        raise TypeError("Field %r is neither a DX nor an AT field")

    def is_field_visible(self, field):
        """Checks if the field is visible in view mode
        """
        widget = self.get_widget(field)
        visibility = widget.isVisible(self.context, mode="view", field=field)
        return visibility == "visible"


    def is_field_required(self, field):
        """Check if the field is required
        """
        return getattr(field, "required", False)

    def is_at_field(self, field):
        """Check if the field is an AT field
        """
        return IATField.providedBy(field)

    def is_dx_field(self, field):
        """Check if the field is an DX field
        """
        return IDXField.providedBy(field)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
