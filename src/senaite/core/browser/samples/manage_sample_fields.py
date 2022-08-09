# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from plone.protect import PostOnly
from Products.Archetypes.interfaces import IField as IATField
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from zope.schema.interfaces import IField as IDXField


class ManageSampleFieldsView(BrowserView):
    """Manage Sample Fields
    """
    template = ViewPageTemplateFile("templates/manage_sample_fields.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        submitted = self.request.form.get("submitted", False)
        if submitted:
            self.handle_form_submit(request=self.request)
            self.request.response.redirect(self.context.absolute_url())
        return self.template()

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
            vis = self.get_field_visibility(field)
            label = self.get_field_label(field)
            description = self.get_field_description(field)
            required = self.is_field_required(field)
            header_fields[vis].append({
                "name": name,
                "field": field,
                "label": label,
                "description": description,
                "required": required,
            })

        return header_fields

    def get_field_visibility(self, field, default="hidden"):
        """Returns the field visibility in the header

        Possible values are:

          - prominent: Rendered as a promient field
          - visible: Rendered as a odestandard field
          - hidden: Not displayed
        """
        widget = self.get_widget(field)
        visibility = widget.isVisible(self.context, mode="header_table", field=field)
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

    def handle_form_submit(self, request=None):
        """Handle form submission
        """
        PostOnly(request)
        message = _("Changes saved.")
        self.add_status_message(message)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
