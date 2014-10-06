from bika.lims.permissions import *
from bika.lims.utils import to_utf8 as _c
from bika.lims.utils import to_unicode as _u
from bika.lims.interfaces import IReferenceWidgetVocabulary
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
import json


class DefaultReferenceWidgetVocabulary(object):
    implements(IReferenceWidgetVocabulary)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, result=None, specification=None, **kwargs):
        searchTerm = _c(self.request.get('searchTerm', '')).lower()
        force_all = self.request.get('force_all', 'true')
        searchFields = 'search_fields' in self.request \
            and json.loads(_u(self.request.get('search_fields', '[]'))) \
            or ('Title',)
        # lookup objects from ZODB
        catalog_name = _c(self.request.get('catalog_name', 'portal_catalog'))
        catalog = getToolByName(self.context, catalog_name)
        base_query = json.loads(_c(self.request['base_query']))
        search_query = json.loads(_c(self.request.get('search_query', "{}")))
        # first with all queries
        contentFilter = dict((k, v) for k, v in base_query.items())
        contentFilter.update(search_query)
        try:
            brains = catalog(contentFilter)
        except:
            from bika.lims import logger
            logger.info(contentFilter)
            raise
        if brains and searchTerm:
            _brains = []
            if len(searchFields) == 0 \
                    or (len(searchFields) == 1 and searchFields[0] == 'Title'):
                _brains = [p for p in brains
                           if p.Title.lower().find(searchTerm) > -1]
            else:
                for p in brains:
                    for fieldname in searchFields:
                        value = getattr(p, fieldname, None)
                        if not value:
                            instance = p.getObject()
                            schema = instance.Schema()
                            if fieldname in schema:
                                value = schema[fieldname].get(instance)
                        if value and value.lower().find(searchTerm) > -1:
                            _brains.append(p)
                            break

            brains = _brains
        # Then just base_query alone ("show all if no match")
        if not brains and force_all.lower() == 'true':
            if search_query:
                brains = catalog(base_query)
                if brains and searchTerm:
                    _brains = [p for p in brains
                               if p.Title.lower().find(searchTerm) > -1]
                    if _brains:
                        brains = _brains
        return brains
