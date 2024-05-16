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

from bika.lims import api
from plone.z3cform.fieldsets.interfaces import IDescriptiveGroup
from z3c.form.interfaces import ISubForm
from z3c.form.widget import Widget


class BaseWidget(Widget):

    def get_form(self):
        """Return the current form of the widget
        """
        if not self.form:
            return None

        form = self.form
        # form is a fieldset group
        if IDescriptiveGroup.providedBy(form):
            form = form.parentForm
        # form is a subform (e.g. DataGridFieldObjectSubForm)
        if ISubForm.providedBy(form):
            form = form.parentForm
        return form

    def get_portal_type(self, default=None):
        """Extract the portal type from the form or the query
        """
        form = self.get_form()
        portal_type = getattr(form, "portal_type", None)
        if not portal_type:
            query = getattr(self, "query", {})
            portal_type = query.get("portal_type")
            if api.is_list(portal_type):
                portal_type = portal_type[0]
        return portal_type or default

    def get_context(self):
        """Get the current context

        NOTE: If we are in the ++add++ form, `self.context` is the container!
              Therefore, we create one here to have access to the methods.
        """
        # We are in the edit view. Return the context directly
        schema_iface = self.field.interface if self.field else None
        if schema_iface and schema_iface.providedBy(self.context):
            return self.context
        # We might be in a subform or in a datagrid widget.
        # Therefore, `self.context` is not set or set to `<NO_VALUE>`
        form = self.get_form()
        portal_type = self.get_portal_type()
        context = getattr(form, "context", None)
        # no context found, return
        # happens e.g. in the `datetimewidget.txt` doctest
        if context is None:
            return None
        # Hack alert!
        try:
            # we are in ++add++ form and have no context!
            # Create a temporary object to be able to access class methods
            view = api.get_view("temporary_context", context=context)
            return view.create_temporary_context(portal_type)
        except TypeError:
            # happens when we no portal_type was found, e.g. if we are in a
            # form and the portal object is our context
            return None
