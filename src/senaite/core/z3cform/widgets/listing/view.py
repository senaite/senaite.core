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

from plone.autoform.interfaces import WIDGETS_KEY
from senaite.app.listing.view import ListingView
from z3c.form.interfaces import IContextAware
from z3c.form.interfaces import IFieldWidget
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


class DefaultListingWidget(ListingView):
    """Default listing widget
    """
    def __init__(self, field, request):
        self.field = field
        self.context = field.context
        self.request = request
        super(DefaultListingWidget, self).__init__(self.context, request)

        # default configuration that is usable for widget purposes
        self.allow_edit = True
        self.context_actions = {}
        self.fetch_transitions_on_select = False
        self.omit_form = True
        self.show_column_toggles = False
        self.show_select_column = True

    @property
    def widget(self):
        return self.get_widget(self.field)

    def get_widget(self, field):
        """Lookup the widget of the field
        """
        widget_tags = field.interface.getTaggedValue(WIDGETS_KEY)
        factory = widget_tags.get(field.getName())
        if factory:
            widget = factory(field, self.request)
        else:
            widget = getMultiAdapter((field, self.request), IFieldWidget)
        widget.context = self.context
        alsoProvides(widget, IContextAware)
        return widget

    def get_value(self):
        """Return the current value of the field
        """
        try:
            # we might be in ++add++ view
            return self.field.get(self.context)
        except AttributeError:
            return self.field.default

    def extract(self):
        """Extract the selected valued from the request
        """
        raise NotImplementedError("Must be provided by subclass")
