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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.


import json
import sys
from operator import itemgetter

import plone.protect
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from magnitude import mg
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    ReferenceField('ContainerType',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('ContainerType',),
        vocabulary = 'getContainerTypes',
        relationship = 'ContainerContainerType',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Container Type"),
        ),
    ),
    StringField('Capacity',
        required = 1,
        default = "0 ml",
        widget = StringWidget(
            label=_("Capacity"),
            description=_("Maximum possible size or volume of samples."),
        ),
    ),
    BooleanField('PrePreserved',
        validators = ('container_prepreservation_validator'),
        default = False,
        widget = BooleanWidget(
            label=_("Pre-preserved"),
            description = _(
                "Check this box if this container is already preserved."
                "Setting this will short-circuit the preservation workflow "
                "for sample partitions stored in this container."),
        ),
    ),
    ReferenceField('Preservation',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Preservation',),
        vocabulary = 'getPreservations',
        relationship = 'ContainerPreservation',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Preservation"),
            description = _(
                "If this container is pre-preserved, then the preservation "
                "method could be selected here."),
        ),
    ),
    BooleanField('SecuritySealIntact',
        default = True,
        widget = BooleanWidget(
            label=_("Security Seal Intact Y/N"),
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class Container(BaseContent):
    implements(IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getJSCapacity(self, **kw):
        """Try convert the Capacity to 'ml' or 'g' so that JS has an
        easier time working with it.  If conversion fails, return raw value.
        """
        default = self.Schema()['Capacity'].get(self)
        try:
            mgdefault = default.split(' ', 1)
            mgdefault = mg(float(mgdefault[0]), mgdefault[1])
        except:
            mgdefault = mg(0, 'ml')
        try:
            return str(mgdefault.ounit('ml'))
        except:
            pass
        try:
            return str(mgdefault.ounit('g'))
        except:
            pass
        return str(default)

    def getContainerTypes(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in
                               bsc(portal_type='ContainerType')]
        o = self.getContainerType()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getPreservations(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in
                               bsc(portal_type='Preservation',
                                   apiis_active = True)]
        o = self.getPreservation()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

registerType(Container, PROJECTNAME)


class ajaxGetContainers:

    catalog_name='bika_setup_catalog'
    contentFilter = {'portal_type': 'Container',
                     'is_active': True}

    def __init__(self, context, request):
        self.context = context
        self.request = request

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
        catalog = getToolByName(self.context, self.catalog_name)
        brains = catalog(self.contentFilter)
        brains = searchTerm and \
            [p for p in brains if p.Title.lower().find(searchTerm) > -1] \
            or brains

        rows = [{'UID': p.UID,
                 'container_uid': p.UID,
                 'Container': p.Title,
                 'Description': p.Description}
                for p in brains]

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(
        ), y.lower()), key=itemgetter(sidx and sidx or 'Container'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}
        return json.dumps(ret)
