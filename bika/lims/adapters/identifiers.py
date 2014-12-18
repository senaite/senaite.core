from operator import itemgetter
import json

from archetypes.schemaextender.interfaces import IOrderableSchemaExtender, \
    ISchemaModifier
from bika.lims import bikaMessageFactory as _, to_utf8
from bika.lims.browser import BrowserView
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.fields import ExtRecordsField
from bika.lims.interfaces import IHaveIdentifiers, IBikaCatalog, \
    IBikaSetupCatalog
from plone.indexer import indexer
from zope.component import adapts
import plone
from zope.interface import implements


@indexer(IHaveIdentifiers, IBikaCatalog)
def IBikaCatalogIdentifiersIndexer(instance):
    try:
        Identifiers = instance.Schema()['Identifiers'].get(instance)
    except:
        return None
    if Identifiers:
        return [to_utf8(i['Identifier']) for i in Identifiers] + \
               [to_utf8(i['Title']) for i in Identifiers]


@indexer(IHaveIdentifiers, IBikaSetupCatalog)
def IBikaSetupCatalogIdentifiersIndexer(instance):
    try:
        Identifiers = instance.Schema()['Identifiers'].get(instance)
    except:
        return None
    if Identifiers:
        return [to_utf8(i['Identifier']) for i in Identifiers] + \
               [to_utf8(i['Title']) for i in Identifiers]


Identifiers = ExtRecordsField(
    'Identifiers',
    required=False,
    type='identifiers',
    subfields=('IdentifierType', 'Identifier', 'Title', 'Description'),
    required_subfields=('IdentifierType', 'Identifier', 'Title'),
    subfield_labels={'IdentifierType': _('Identifier Type'),
                     'Identifier': _('Identifier'),
                     'Title': _('Title'),
                     'Desription': _('Description')},
    subfield_validators={'IdentifierType': 'identifiervalidator',
                         'Identifier': 'identifiervalidator',
                         'Title': 'identifiervalidator'},
    subfield_sizes={'IdentifierType': 10,
                    'Identifier': 15,
                    'Title': 25,
                    'Description': 32},
    widget=RecordsWidget(
        label=_('Identifiers for this object'),
        description=_(
            "Select identifiers by which this object can be referenced."),
        visible={'view': 'visible',
                 'edit': 'visible'},
        combogrid_options={
            'IdentifierType': {
                'colModel': [
                    {'columnName': 'identifiertype_uid', 'hidden': True},
                    {'columnName': 'IdentifierType', 'width': '30',
                     'label': _('Identifier Type')},
                    {'columnName': 'Description', 'width': '70',
                     'label': _('Description')}
                ],
                'url': 'getidentifiertypes',
                'showOn': True,
                'width': '500px',
            }
        }
    )
)


class IHaveIdentifiersSchemaExtender(object):
    adapts(IHaveIdentifiers)
    implements(IOrderableSchemaExtender)

    fields = [
        Identifiers,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        """Return modified order of field schemats.
        """
        schemata = self.context.schema['description'].schemata
        fields = schematas[schemata]
        fields.insert(fields.index('description') + 1,
                      'Identifiers')
        return schematas

    def getFields(self):
        return self.fields


class IHaveIdentifiersSchemaModifier(object):
    adapts(IHaveIdentifiers)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        schemata = schema['description'].schemata
        schema['Identifiers'].schemata = schemata
        schema.moveField('Identifiers', after='description')
        return schema


class ajaxGetIdentifierTypes(BrowserView):
    """ Identifier types vocabulary source for jquery combo dropdown box
    """

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request[
            'searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type='IdentifierType',
                                         inactive_state='active')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower(
            ).find(searchTerm) > -1]

        for p in brains:
            rows.append({'IdentifierType': p.Title,
                         'Description': p.Description})

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(
        ), y.lower()), key=itemgetter(sidx and sidx or 'IdentifierType'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(
                   nr_rows)]}
        return json.dumps(ret)
