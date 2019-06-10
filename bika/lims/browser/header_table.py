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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import getSecurityManager
from AccessControl.Permissions import view
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IHeaderTableFieldRenderer
from bika.lims.utils import t
from Products.Archetypes.event import ObjectEditedEvent
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import event
from zope.component import getAdapter
from zope.component.interfaces import ComponentLookupError


class HeaderTableView(BrowserView):
    """Table rendered at the top in AR View
    """
    template = ViewPageTemplateFile("templates/header_table.pt")

    def __call__(self):
        self.errors = {}
        if "header_table_submitted" in self.request:
            schema = self.context.Schema()
            fields = schema.fields()
            form = self.request.form
            for field in fields:
                fieldname = field.getName()
                if fieldname in form:
                    # Handle (multiValued) reference fields
                    # https://github.com/bikalims/bika.lims/issues/2270
                    uid_fieldname = "{}_uid".format(fieldname)
                    if uid_fieldname in form:
                        value = form[uid_fieldname]
                        if field.multiValued:
                            value = value.split(",")
                        field.getMutator(self.context)(value)
                    else:
                        # other fields
                        field.getMutator(self.context)(form[fieldname])
            message = _("Changes saved.")
            # reindex the object after save to update all catalog metadata
            self.context.reindexObject()
            # notify object edited event
            event.notify(ObjectEditedEvent(self.context))
            self.context.plone_utils.addPortalMessage(message, "info")
        return self.template()

    def three_column_list(self, input_list):
        list_len = len(input_list)

        # Calculate the length of the sublists
        sublist_len = (list_len % 3 == 0 and list_len / 3 or list_len / 3 + 1)

        def _list_end(num):
            # Calculate the list end point given the list number
            return num == 2 and list_len or (num + 1) * sublist_len

        # Generate only filled columns
        final = []
        for i in range(3):
            column = input_list[i * sublist_len:_list_end(i)]
            if len(column) > 0:
                final.append(column)
        return final

    # TODO Revisit this
    def render_field_view(self, field):
        fieldname = field.getName()
        field = self.context.Schema()[fieldname]
        ret = {"fieldName": fieldname, "mode": "view"}
        try:
            adapter = getAdapter(self.context,
                                 interface=IHeaderTableFieldRenderer,
                                 name=fieldname)

        except ComponentLookupError:
            adapter = None
        if adapter:
            ret = {'fieldName': fieldname,
                   'mode': 'structure',
                   'html': adapter(field)}
        else:
            if field.getWidgetName() == "BooleanWidget":
                value = field.get(self.context)
                ret = {
                    "fieldName": fieldname,
                    "mode": "structure",
                    "html": t(_("Yes")) if value else t(_("No"))
                }
            elif field.getType().find("Reference") > -1:
                # Prioritize method retrieval over schema"s field
                targets = None
                if hasattr(self.context, "get%s" % fieldname):
                    fieldaccessor = getattr(self.context, "get%s" % fieldname)
                    if callable(fieldaccessor):
                        targets = fieldaccessor()
                if not targets:
                    targets = field.get(self.context)

                if targets:
                    if not type(targets) == list:
                        targets = [targets, ]
                    sm = getSecurityManager()
                    if all([sm.checkPermission(view, ta) for ta in targets]):
                        elements = [
                            "<div id='{id}' class='field reference'>"
                            "  <a class='link' uid='{uid}' href='{url}'>"
                            "    {title}"
                            "  </a>"
                            "</div>"
                            .format(id=target.getId(),
                                    uid=target.UID(),
                                    url=target.absolute_url(),
                                    title=target.Title())
                            for target in targets]

                        ret = {
                            "fieldName": fieldname,
                            "mode": "structure",
                            "html": "".join(elements),
                        }
                    else:
                        ret = {
                            "fieldName": fieldname,
                            "mode": "structure",
                            "html": ", ".join([ta.Title() for ta in targets]),
                        }
                else:
                    ret = {
                        "fieldName": fieldname,
                        "mode": "structure",
                        "html": "",
                    }
            elif field.getType().lower().find("datetime") > -1:
                value = field.get(self.context)
                ret = {
                    "fieldName": fieldname,
                    "mode": "structure",
                    "html": self.ulocalized_time(value, long_format=True)
                }
        return ret

    def get_field_visibility_mode(self, field):
        """Returns "view" or "edit" modes, together with the place within where
        this field has to be rendered, based on the permissions the current
        user has for the context and the field passed in
        """
        fallback_mode = ("hidden", "hidden")
        widget = field.widget

        # TODO This needs to be done differently
        # Check where the field has to be located
        layout = widget.isVisible(self.context, "header_table")
        if layout in ["invisible", "hidden"]:
            return fallback_mode

        # Check permissions. We want to display field (either in view or edit
        # modes) only if the current user has enough privileges.
        if field.checkPermission("edit", self.context):
            mode = "edit"
            sm = getSecurityManager()
            if not sm.checkPermission(ModifyPortalContent, self.context):
                logger.warn("Permission '{}' granted for the edition of '{}', "
                            "but 'Modify portal content' not granted"
                            .format(field.write_permission, field.getName()))
        elif field.checkPermission("view", self.context):
            mode = "view"
        else:
            return fallback_mode

        # Check if the field needs to be displayed or not, even if the user has
        # the permissions for edit or view. This may depend on criteria other
        # than permissions (e.g. visibility depending on a setup setting, etc.)
        if widget.isVisible(self.context, mode, field=field) != "visible":
            if mode == "view":
                return fallback_mode
            # The field cannot be rendered in edit mode, but maybe can be
            # rendered in view mode.
            mode = "view"
            if widget.isVisible(self.context, mode, field=field) != "visible":
                return fallback_mode
        return (mode, layout)

    def get_fields_grouped_by_location(self):
        standard = []
        prominent = []
        for field in self.context.Schema().fields():
            mode, layout = self.get_field_visibility_mode(field)
            if mode == "hidden":
                # Do not render this field
                continue
            field_mapping = {"fieldName": field.getName(), "mode": mode}
            if mode == "view":
                # Special formatting (e.g. links, etc.)
                field_mapping = self.render_field_view(field)
            if layout == "prominent":
                # Add the field at the top of the fields table
                prominent.append(field_mapping)
            else:
                # Add the field at standard location
                standard.append(field_mapping)
        return prominent, self.three_column_list(standard)
