# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from itertools import islice
from bika.lims.api.security import check_permission
from plone.app.layout.viewlets import ViewletBase
from Products.Archetypes.interfaces import IField as IATField
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from zope.schema.interfaces import IField as IDXField


class SampleHeaderViewlet(ViewletBase):
    """Header table with editable sample fields
    """
    template = ViewPageTemplateFile("templates/sampleheader.pt")

    def render(self):
        submitted = self.request.form.get("sampleheader_form_submitted", False)
        if submitted:
            self.add_status_message(_("Changes saved"))
            self.request.response.redirect(self.context.absolute_url())
        return self.template()

    def render_widget(self, field):
        """Render the label for the fields' widget
        """
        mode = self.get_field_mode(field)
        return self.context.widget(field.getName(), mode=mode)

    def render_widget_label(self, field):
        """Render the label for the fields' widget
        """
        return field.widget.label

    @property
    def fields(self):
        """Returns an ordered dict of all schema fields
        """
        return api.get_fields(self.context)

    def grouper(self, iterable, n):
        for chunk in iter(lambda it=iter(iterable): list(islice(it, n)), []):
            yield chunk

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
            mode = self.get_field_mode(field)
            if mode not in ["view", "edit"]:
                continue
            header_fields[vis].append(field)

        return header_fields

    def get_field_visibility(self, field, default="hidden"):
        """Returns the field visibility in the header

        Possible values are:

          - prominent: Rendered as a promient field
          - visible: Rendered as a standard field
          - hidden: Not displayed
        """
        widget = self.get_widget(field)
        visibility = widget.isVisible(self.context, mode="header_table", field=field)
        if visibility not in ["prominent", "visible"]:
            return default
        return visibility

    def get_field_mode(self, field, default="hidden"):
        """Returns the field mode in the header

        Possible values are:

          - edit: field is rendered in edit mode
          - view: field is rendered in view mode
        """
        mode = "view"
        if field.checkPermission("edit", self.context):
            mode = "edit"
            if not self.is_edit_allowed():
                logger.warn("Permission '{}' granted for the edition of '{}', "
                            "but 'Modify portal content' not granted"
                            .format(field.write_permission, field.getName()))
        elif field.checkPermission("view", self.context):
            mode = "view"

        widget = self.get_widget(field)
        mode_vis = widget.isVisible(self.context, mode=mode, field=field)
        if mode_vis != "visible":
            if mode == "view":
                return default
            # The field cannot be rendered in edit mode, but maybe can be
            # rendered in view mode.
            mode = "view"
            view_vis = widget.isVisible(self.context, mode=mode, field=field)
            if view_vis != "visible":
                return default

        return mode

    def get_widget(self, field):
        """Returns the widget of the field
        """
        if IATField.providedBy(field):
            return field.widget
        elif IDXField.providedBy(field):
            raise NotImplementedError("DX widgets not yet needed")
        raise TypeError("Field %r is neither a DX nor an AT field")

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def is_edit_allowed(self):
        """Check permission 'ModifyPortalContent' on the context
        """
        return check_permission(ModifyPortalContent, self.context)
