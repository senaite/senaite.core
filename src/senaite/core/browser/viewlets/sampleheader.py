# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from plone.app.layout.viewlets import ViewletBase
from bika.lims.api.security import check_permission
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Archetypes.interfaces import IField as IATField
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

    @property
    def fields(self):
        """Returns an ordered dict of all schema fields
        """
        return api.get_fields(self.context)

    def get_header_fields(self):
        """Return the (re-arranged) fields
        """
        prominent = []
        standard = []
        hidden = []

        for name, field in self.fields.items():
            layout = self.get_field_visibility(field)

        return {
            "prominent": prominent,
            "standard": standard
            "hidden": hidden
        }

    def get_field_visibility(self, field):
        """Returns "view" or "edit" modes, together with the place within where
        this field has to be rendered, based on the permissions the current
        user has for the context and the field passed in
        """
        widget = self.get_widget(field)
        widget.isVisible(self.context, "header_table")

    def get_widget(self, field):
        """Returns the widget of the field
        """
        elif IATField.providedBy(field):
            return field.widget
        if IDXField.providedBy(field):
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

    def render_field(self, field):
        return "FIELD EDIT/VIEW HTML"
