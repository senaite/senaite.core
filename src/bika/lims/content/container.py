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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
from operator import itemgetter

import plone.protect
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IContainer
from bika.lims.interfaces import IDeactivable
from magnitude import mg
from Products.Archetypes.atapi import registerType
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.Field import BooleanField
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget
from Products.Archetypes.Widget import StringWidget
from Products.CMFCore.utils import getToolByName
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.p3compat import cmp
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    UIDReferenceField(
        "ContainerType",
        required=0,
        allowed_types=("ContainerType",),
        widget=ReferenceWidget(
            label=_(
                "label_container_type",
                default="Container Type"),
            description=_(
                "description_container_type",
                default="Select the type of this container"),
            catalog=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
        ),
    ),

    StringField(
        "Capacity",
        required=1,
        default="0 ml",
        widget=StringWidget(
            label=_("Capacity"),
            description=_("Maximum possible size or volume of samples."),
        ),
    ),

    BooleanField(
        'PrePreserved',
        validators=('container_prepreservation_validator'),
        default=False,
        widget=BooleanWidget(
            label=_("Pre-preserved"),
            description=_(
                "Check this box if this container is already preserved."
                "Setting this will short-circuit the preservation workflow "
                "for sample partitions stored in this container."),
        ),
    ),

    UIDReferenceField(
        "Preservation",
        required=0,
        allowed_types=("SamplePreservation",),
        widget=ReferenceWidget(
            label=_(
                "label_container_preservation",
                default="Preservation"),
            description=_(
                "description_container_preservation",
                default="If this container is pre-preserved, then the "
                "preservation method could be selected here."),
            render_own_label=True,
            catalog_name=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
        )
    ),

    BooleanField(
        "SecuritySealIntact",
        default=True,
        widget=BooleanWidget(
            label=_("Security Seal Intact Y/N"),
        ),
    ),
))

schema["description"].widget.visible = True
schema["description"].schemata = "default"


class Container(BaseContent):
    implements(IContainer, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getJSCapacity(self, **kw):
        """Try convert the Capacity to 'ml' or 'g' so that JS has an
        easier time working with it.  If conversion fails, return raw value.
        """
        default = self.Schema()['Capacity'].get(self)
        try:
            mgdefault = default.split(' ', 1)
            mgdefault = mg(float(mgdefault[0]), mgdefault[1])
        except Exception:
            mgdefault = mg(0, 'ml')
        try:
            return str(mgdefault.ounit('ml'))
        except Exception:
            pass
        try:
            return str(mgdefault.ounit('g'))
        except Exception:
            pass
        return str(default)


registerType(Container, PROJECTNAME)


# TODO: Refactor!
#       This class is registered as `getcontainers` and used in artemplate to
#       populate the combogrid field
class ajaxGetContainers:

    catalog_name='senaite_catalog_setup'
    contentFilter = {'portal_type': 'SampleContainer',
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
