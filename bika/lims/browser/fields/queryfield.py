"""This version adds registry_prefix, used to select
additional fields from the registry and catalog_name,
for selecting a catalog tool.
"""

from AccessControl import ClassSecurityInfo
from archetypes.querywidget.interfaces import IQueryField
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Field import registerField
from zope.interface import implements
from zope.site.hooks import getSite

from archetypes.querywidget.field import QueryField as _QueryField
from bika.lims.querystring.querybuilder import QueryBuilder


class QueryField(_QueryField):
    """QueryField for storing query"""

    implements(IQueryField)
    _properties = ObjectField._properties.copy()
    _properties.update({
        'catalog_name': 'portal_catalog',
        'registry_prefix': '',
        'config': {},
    })

    security = ClassSecurityInfo()

    def get(self, instance, **kwargs):
        """Get the query dict from the request or from the object"""
        raw = kwargs.get('raw', None)
        value = self.getRaw(instance)
        if raw:
            # We actually wanted the raw value, should have called getRaw
            return value
        request = getSite().REQUEST
        request['catalog_name'] = self.catalog_name
        querybuilder = QueryBuilder(instance, request,
                                    catalog_name=self.catalog_name)

        sort_on = kwargs.get('sort_on', instance.getSort_on())
        sort_order = 'reverse' if instance.getSort_reversed() else 'ascending'
        limit = kwargs.get('limit', instance.getLimit())

        return querybuilder(query=value, batch=kwargs.get('batch', False),
                            b_start=kwargs.get('b_start', 0),
                            b_size=kwargs.get('b_size', 30),
                            sort_on=sort_on, sort_order=sort_order,
                            limit=limit, brains=kwargs.get('brains', False))

    def getRaw(self, instance, **kwargs):
        return ObjectField.get(self, instance, **kwargs) or ()


registerField(QueryField, title='QueryField',
              description=('query field for storing a query'))
