# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import json
from operator import itemgetter

from AccessControl import ClassSecurityInfo
from Products.Archetypes import DisplayList
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseContent import BaseContent
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.container import schema
from plone.protect import CheckAuthenticator


class Container(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getContainerTypes(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(o.UID, o.Title) for o in
                              bsc(portal_type='ContainerType')]
        o = self.getContainerType()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getPreservations(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(o.UID, o.Title) for o in
                              bsc(portal_type='Preservation',
                                  inactive_state='active')]
        o = self.getPreservation()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))


registerType(Container, PROJECTNAME)


class ajaxGetContainers:
    catalog_name = 'bika_setup_catalog'
    contentFilter = {'portal_type': 'Container',
                     'inactive_state': 'active'}

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):

        CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request[
            'searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']

        # lookup objects from ZODB
        catalog = getToolByName(self.context, self.catalog_name)
        brains = catalog(self.contentFilter)
        brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1] \
            if searchTerm else brains

        rows = [{'UID': p.UID,
                 'container_uid': p.UID,
                 'Container': p.Title,
                 'Description': p.Description}
                for p in brains]

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()),
                      key=itemgetter(sidx and sidx or 'Container'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        start = (int(page) - 1) * int(nr_rows)
        end = int(page) * int(nr_rows)
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[start:end]}
        return json.dumps(ret)
