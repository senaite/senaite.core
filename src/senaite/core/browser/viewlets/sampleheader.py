# -*- coding: utf-8 -*-

from itertools import islice

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.api.security import check_permission
from bika.lims.interfaces import IHeaderTableFieldRenderer
from plone.app.layout.viewlets import ViewletBase
from plone.protect import PostOnly
from Products.Archetypes.event import ObjectEditedEvent
from Products.Archetypes.interfaces import IField as IATField
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from senaite.core.api import dtime
from senaite.core.browser.widgets.datetimewidget import DateTimeWidget
from senaite.core.interfaces import IDataManager
from zope import event
from zope.component import queryAdapter
from zope.schema.interfaces import IField as IDXField


class SampleHeaderViewlet(ViewletBase):
    """Header table with editable sample fields
    """
    template = ViewPageTemplateFile("templates/sampleheader.pt")

    def render(self):
        """Renders the viewlet and handles form submission
        """
        submitted = self.request.form.get("sampleheader_form_submitted", False)
        if submitted:
            self.handle_form_submit(request=self.request)
            self.request.response.redirect(self.context.absolute_url())
        return self.template()

    def handle_form_submit(self, request=None):
        """Handle form submission
        """
        PostOnly(request)

        errors = {}
        field_values = {}
        form = request.form

        for name, field in self.fields.items():
            value = self.get_field_value(field, form)
            if value is None:
                continue

            # Keep track of field-values
            field_values.update({name: value})

            # Validate the field values
            error = field.validate(value, self.context)
            if error:
                errors.update({name: error})

        if errors:
            request["errors"] = errors
            message = _("Please correct the indicated errors")
            self.add_status_message(message, level="error")
        else:
            # we want to set the fields with the data manager
            dm = IDataManager(self.context)

            # Store the field values
            for name, value in field_values.items():
                dm.set(name, value)

            message = _("Changes saved.")
            # reindex the object after save to update all catalog metadata
            self.context.reindexObject()
            # notify object edited event
            event.notify(ObjectEditedEvent(self.context))
            self.add_status_message(message, level="info")

    @property
    def fields(self):
        """Returns an ordered dict of all schema fields
        """
        return api.get_fields(self.context)

    def get_field_value(self, field, form):
        """Returns the submitted value for the given field
        """
        fieldname = field.getName()
        if fieldname not in form:
            return None

        # Handle (multiValued) reference fields
        # https://github.com/bikalims/bika.lims/issues/2270
        uid_fieldname = "{}_uid".format(fieldname)
        if uid_fieldname in form:
            value = form[uid_fieldname]
            if field.multiValued:
                value = filter(None, value.split(","))
            return value

        # other fields
        return form[fieldname]

    def grouper(self, iterable, n=3):
        """Splits an iterable into chunks of `n` items
        """
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
            html = self.render_field_html(field, mode=mode)
            label = self.render_field_label(field, mode=mode)
            required = self.is_field_required(field, mode=mode)
            header_fields[vis].append({
                "name": name,
                "mode": mode,
                "html": html,
                "field": field,
                "label": label,
                "required": required,
            })

        return header_fields

    def render_field_html(self, field, mode="view"):
        """Render field HTML
        """
        if mode == "view":
            # Lookup custom view adapter
            adapter = queryAdapter(self.context,
                                   interface=IHeaderTableFieldRenderer,
                                   name=field.getName())
            # return immediately if we have an adapter
            if adapter is not None:
                return adapter(field)

            # TODO: Refactor to adapter
            # Returns the localized date
            if self.is_datetime_field(field):
                value = field.get(self.context)
                if not value:
                    return None
                return dtime.ulocalized_time(value,
                                             long_format=True,
                                             context=self.context,
                                             request=self.request)

        return None

    def render_field_label(self, field, mode="view"):
        """Renders the field label

        In edit mode, render the required dot as well
        """
        widget = self.get_widget(field)
        return widget.label

    def render_widget(self, field, mode="view"):
        """Render the field widget
        """
        return self.context.widget(field.getName(), mode=mode)

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
        if self.is_at_field(field):
            return field.widget
        elif self.is_dx_field(field):
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

    def is_field_required(self, field, mode="edit"):
        """Check if the field is required
        """
        if mode == "view":
            return False
        return field.required

    def is_datetime_field(self, field):
        """Check if the field is a date field
        """
        if self.is_at_field(field):
            widget = self.get_widget(field)
            return isinstance(widget, DateTimeWidget)
        return False

    def is_at_field(self, field):
        """Check if the field is an AT field
        """
        return IATField.providedBy(field)

    def is_dx_field(self, field):
        """Check if the field is an DX field
        """
        return IDXField.providedBy(field)
