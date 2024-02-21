# -*- coding: utf-8 -*-

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
