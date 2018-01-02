# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import re
from operator import itemgetter
import json

from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from plone.indexer import indexer
from bika.lims.utils import to_utf8
from bika.lims import bikaMessageFactory as _, safe_unicode
from bika.lims.browser import BrowserView
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.fields import ExtRecordsField
from bika.lims.interfaces import IHaveIdentifiers
from zope.component import adapts
import plone
from zope.interface import implements

from ZODB.POSException import ConflictError

@indexer(IHaveIdentifiers)
def IdentifiersIndexer(instance):
    """Return a list of unique Identifier strings
    This populates the Identifiers Keyword index, but with some
    replacements to prevent the word-splitter etc from taking effect.
    """
    identifiers = instance.Schema()['Identifiers'].get(instance)
    return [safe_unicode(i['Identifier']) for i in identifiers]

Identifiers = ExtRecordsField(
    'Identifiers',
    required=False,
    type='identifiers',
    searchable=True,
    subfields=('IdentifierType', 'Identifier', 'Description'),
    required_subfields=('IdentifierType', 'Identifier'),
    subfield_labels={'IdentifierType': _('Identifier Type'),
                     'Identifier': _('Identifier'),
                     'Description': _('Description')},
    subfield_validators={'IdentifierType': 'identifiervalidator',
                         'Identifier': 'identifiervalidator'},
    subfield_sizes={'IdentifierType': 10,
                    'Identifier': 15,
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

def SearchableText(self):
    """This overrides the default method from Archetypes.BaseObject,
    and allows Identifiers field to be included in SearchableText despite
    the field being an incompatible type.
    """
    data = []
    for field in self.Schema().fields():
        if not field.searchable:
            continue
        #### The following is the addition made to the default AT method:
        fieldname = field.getName()
        if IHaveIdentifiers.providedBy(self) and fieldname == 'Identifiers':
            identifiers = self.Schema()['Identifiers'].get(self)
            idents = [to_utf8(i['Identifier']) for i in identifiers]
            if idents:
                data.extend(idents)
            continue
        ### The code from this point on is lifted directly from BaseObject
        method = field.getIndexAccessor(self)
        try:
            datum = method(mimetype="text/plain")
        except TypeError:
            # Retry in case typeerror was raised because accessor doesn't
            # handle the mimetype argument
            try:
                datum = method()
            except (ConflictError, KeyboardInterrupt):
                raise
            except:
                continue
        if datum:
            vocab = field.Vocabulary(self)
            if isinstance(datum, (list, tuple)):
                #  Unmangle vocabulary: we index key AND value
                vocab_values = map(
                    lambda value, vocab=vocab: vocab.getValue(value, ''),
                    datum)
                datum = list(datum)
                datum.extend(vocab_values)
                datum = ' '.join(datum)
            elif isinstance(datum, basestring):
                if isinstance(datum, unicode):
                    datum = to_utf8(datum)
                value = vocab.getValue(datum, '')
                if isinstance(value, unicode):
                    value = to_utf8(value)
                datum = "%s %s" % (datum, value,)

            if isinstance(datum, unicode):
                datum = to_utf8(datum)
            data.append(str(datum))
    data = ' '.join(data)
    return data


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

