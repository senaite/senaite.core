# -*- coding: utf-8 -*-

from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.z3cform.interfaces import IListingWidget
from senaite.core.z3cform.widgets.basewidget import BaseWidget
from z3c.form.browser import widget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import NO_VALUE
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IList


@adapter(IDict, IListingWidget)
class DictFieldDataConverter(BaseDataConverter):
    """Data Converter for Dict Fields
    """
    def toWidgetValue(self, value):
        if not value:
            return {}
        return value

    def toFieldValue(self, value):
        if not value:
            return {}
        return value


@adapter(IList, IListingWidget)
class ListFieldDataConverter(BaseDataConverter):
    """Data Converter for List Fields
    """
    def toWidgetValue(self, value):
        if not value:
            return []
        return value

    def toFieldValue(self, value):
        if not value:
            return []
        return value


@implementer_only(IListingWidget)
class ListingWidget(widget.HTMLInputWidget, BaseWidget):
    """Listing widget for list/dict fields
    """
    klass = u"listing-widget"

    def update(self):
        super(ListingWidget, self).update()
        widget.addFieldClass(self)

    def extract(self, default=NO_VALUE):
        """Extract the value from the request
        """
        # delegate to the extract method of the listing view
        view = self.get_listing_view()
        if view:
            return view.extract()
        return default

    def get_widget_view_name(self, default="default_listing_widget_view"):
        """Returns the configured listing view name
        """
        return getattr(self, "listing_view", default)

    def get_traversal_path(self):
        """Return the view traversal path including the field
        """
        viewname = self.get_widget_view_name()
        fieldname = self.field.getName()
        iface = self.field.interface.__identifier__
        return "++field++{}.{}/{}".format(iface, fieldname, viewname)

    def get_listing_view(self):
        """Lookup the listing view by name
        """
        context = self.context
        path = self.get_traversal_path()
        view = context.unrestrictedTraverse(path, default=None)
        if not view:
            return None
        # Inject the API URL for Ajax requests coming from senaite.app.listing
        view.get_api_url = self.get_api_url
        return view

    def get_api_url(self):
        """Ajax API URL for the listing view that traverses over the field
        """
        url = self.context.absolute_url()
        path = self.get_traversal_path()
        return "{}/{}".format(url, path)

    def contents_table(self, editable=True):
        view = self.get_listing_view()
        if not view:
            return "Listing view not found!"
        view.update()
        view.before_render()
        if editable:
            return view.ajax_contents_table()
        # ensure all rows are displayed in view mode
        view.pagesize = 999999
        return view.contents_table_view()


@adapter(IField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def ListingWidgetFactory(field, request):
    """Widget factory
    """
    return FieldWidget(field, ListingWidget(request))
