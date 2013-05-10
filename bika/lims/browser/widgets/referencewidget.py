from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.permissions import *
from bika.lims.utils import to_unicode as _u
from operator import itemgetter
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import StringWidget
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
import json
import plone


class ReferenceWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/referencewidget",
        'helper_js': ("bika_widgets/referencewidget.js",),
        'helper_css': ("bika_widgets/referencewidget.css",),

        'url': 'referencewidget_search',
        'catalog_name': 'portal_catalog',

        # base_query can be a dict or a callable returning a dict
        'base_query': {},

        # columnName must contain valid index names
        'colModel': [
            {'columnName': 'Title', 'width': '30', 'label': _('Title'), 'align': 'left'},
            {'columnName': 'Description', 'width': '70', 'label': _('Description'), 'align': 'left'},
            # UID is required in colModel
            {'columnName': 'UID', 'hidden': True},
        ],

        # Default field to put back into input elements
        'ui_item': 'Title',
        'search_fields': ('Title',),
        'popup_width': '550px',
        'showOn': 'false',
        'sord': 'asc',
        'sidx': 'Title',
        'portal_types': {}
    })
    security = ClassSecurityInfo()

    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """Return a UID so that ReferenceField understands.
        """
        fieldName = field.getName()
        if fieldName+"_uid" in form:
            uid = form.get(fieldName+"_uid", '')
        elif fieldName in form:
            uid = form.get(fieldName, '')
        else:
            uid = None
        return uid, {}

    def get_combogrid_options(self, context, fieldName):
        colModel = self.colModel
        if 'UID' not in [x['columnName'] for x in colModel]:
            colModel.append({'columnName': 'UID', 'hidden': True})
        options = {
            'url': self.url,
            'colModel': colModel,
            'showOn': self.showOn,
            'width': self.popup_width,
            'sord': self.sord,
            'sidx': self.sidx,
            'search_fields': self.search_fields,
        }
        return json.dumps(options)

    def get_base_query(self, context, fieldName):
        base_query = self.base_query
        if callable(base_query):
            base_query = base_query()
        if base_query and isinstance(base_query, basestring):
            base_query = json.loads(base_query)

        # portal_type: use field allowed types
        field = context.Schema().getField(fieldName)
        allowed_types = getattr(field, 'allowed_types', None)
        allowed_types_method = getattr(field, 'allowed_types_method', None)
        if allowed_types_method:
            meth = getattr(content_instance, allowed_types_method)
            allowed_types = meth(field)
        # If field has no allowed_types defined, use widget's portal_type prop
        base_query['portal_type'] = allowed_types and allowed_types or self.portal_types

        return json.dumps(self.base_query)

registerWidget(ReferenceWidget, title='Reference Widget')


class ajaxReferenceWidgetSearch(BrowserView):
    """ Source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request[
            'searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        colModel = json.loads(_u(self.request.get('colModel', '[]')))
        searchFields = 'search_fields' in self.request \
            and json.loads(_u(self.request.get('search_fields', '[]'))) \
            or ('Title',)
        rows = []

        # lookup objects from ZODB
        catalog = getToolByName(self.context, self.request['catalog_name'])
        base_query = json.loads(_u(self.request['base_query']))
        search_query = json.loads(_u(self.request.get('search_query', "{}")))

        # first with all queries
        contentFilter = dict((k,v) for k,v in base_query.items())
        contentFilter.update(search_query)
        brains = catalog(contentFilter)
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
                            break;

            brains = _brains

        # Then just base_query alone ("show all if no match")
        if not brains:
            if search_query:
                brains = catalog(base_query)
                if brains and searchTerm:
                    _brains = [p for p in brains
                               if p.Title.lower().find(searchTerm) > -1]
                    if _brains:
                        brains = _brains

        for p in brains:
            row = {'UID': getattr(p, 'UID'),
                   'Title': getattr(p, 'Title')}
            other_fields = [x for x in colModel
                            if x['columnName'] not in row.keys()]
            for field in other_fields:
                fieldname = field['columnName']
                value = getattr(p, fieldname, None)
                if not value:
                    instance = p.getObject()
                    schema = instance.Schema()
                    if fieldname in schema:
                        value = schema[fieldname].get(instance)
                # '&nbsp;' instead of '' because empty div fields don't render 
                # correctly in combo results table
                row[fieldname] = value and value or '&nbsp;'
            rows.append(row)

        rows = sorted(rows, cmp=lambda x, y: cmp(
            x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
