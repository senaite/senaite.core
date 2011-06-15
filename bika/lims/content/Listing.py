"""Listing support

$Id: Listing.py 319 2006-11-05 20:27:14Z anneline $
"""
from AccessControl import ClassSecurityInfo
from Acquisition import ImplicitAcquisitionWrapper
from Products.CMFCore import permissions
from Products.Archetypes.Renderer import renderer
from Products.Archetypes.ClassGen import Generator

_iaw = ImplicitAcquisitionWrapper
_marker = []

class ListingSupport:
    security = ClassSecurityInfo()

    security.declarePublic('getListingById')
    def getListingById(self, id, default=_marker):
        for listing in self.listings:
            if listing['id'] == id:
                l = listing['listing']
                return _iaw(l, self)
        raise ValueError, ('No listing "%s" for %s'
                           % (id, str(self)))

    def getListedTypes(self, id):
        for listing in self.listings:
            if listing['id'] == id and \
                listing.has_key('allowed_content_types'):
                return [self.portal_types[i] for i in listing['allowed_content_types']]
        return self.getAllowedTypes()
        

    security.declareProtected(permissions.View, 'widget')
    def widget_p(self, instance, field_name, mode="view", field=None,
                 schema=None, **kwargs):
        """Returns the rendered widget. Extends BaseObject.widget to
           look in a given 'schema'.
        """
        if schema is None:
            schema = instance.Schema()
        if field is None:
            field = schema[field_name]
        widget = field.widget
        accessor = field.getAccessor(instance)
        if accessor is None:
            generator = Generator()
            methodName = generator.computeMethodName(field, 'r')
            generator.makeMethod(instance.__class__, field,
                'r', methodName)
            accessor=getattr(instance, methodName)
        return renderer.render(field_name, mode, widget, instance,
            field=field, accessor=accessor, schema=schema, **kwargs)


