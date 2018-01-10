# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IHaveIdentifiers

from AccessControl import ClassSecurityInfo
from Products.Archetypes import listTypes
from Products.Archetypes.Field import LinesField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import PicklistWidget
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from Products.CMFCore.utils import getToolByName

from ZODB.POSException import ConflictError

# class IdentifierTypeAttributesField(RecordsField):
#     """Keeps a list of possible attributes for an identifier of this type
#     """
#     _properties = RecordsField._properties.copy()
#     _properties.update({
#         'fixedSize': False,
#         'minimalSize': 1,
#         'maximalSize': 9999,
#         'type': 'identifiertypeattributes',
#         'subfields': ('title', 'description'),
#         'required_subfields': ('title',),
#         'subfield_labels': {'title': _('Attribute Title'),
#                             'description': _('Description')},
#         'subfield_sizes': {'title': 20,
#                            'description': 35},
#         'subfield_validators': {'title': 'identifiertypeattributesvalidator'},
#     })
#     security = ClassSecurityInfo()


PortalTypes = LinesField(
    'PortalTypes',
    vocabulary='getPortalTypes',
    widget=PicklistWidget(
        label=_("Portal Types"),
        description=_("Select the types that this ID is used to identify."),
    ),
)

# Attributes = IdentifierTypeAttributesField(
#     'Attributes',
#     widget=BikaRecordsWidget(
#         label=_("Identifier attributes"),
#         description=_("Each item identified with this IdentifierType can "
#                       "contain additional information.  The allowed
# attributes "
#                       "can be specified here."),
#     ),
# )

schema = BikaSchema.copy() + Schema((
    PortalTypes,
    # Attributes,
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class IdentifierType(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation

        renameAfterCreation(self)

    def getPortalTypes(self):
        # cargoed from ArchetypeTool.listPortalTypesWithInterfaces because
        # portal_factory is given a FauxArchetypeTool without this method
        pt = getToolByName(self, 'portal_types')
        value = []
        for data in listTypes():
            klass = data['klass']
            for iface in [IHaveIdentifiers]:
                if iface.implementedBy(klass):
                    ti = pt.getTypeInfo(data['portal_type'])
                    if ti is not None:
                        value.append(ti)
        return [v.Title() for v in value]


registerType(IdentifierType, PROJECTNAME)
