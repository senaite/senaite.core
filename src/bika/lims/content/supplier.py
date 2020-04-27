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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import ManagedSchema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import TextField
from Products.Archetypes.public import registerType
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.organisation import Organisation
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import ISupplier

schema = Organisation.schema.copy() + ManagedSchema((

    TextField(
        "Remarks",
        allowable_content_types=("text/plain",),
        widget=TextAreaWidget(
            label=_("Remarks"),
        )
    ),

    StringField(
        "Website",
        searchable=1,
        required=0,
        widget=StringWidget(
            visible={"view": "visible", "edit": "visible"},
            label=_("Website."),
        ),
    ),

    StringField(
        "NIB",
        searchable=1,
        schemata="Bank details",
        required=0,
        widget=StringWidget(
            visible={"view": "visible", "edit": "visible"},
            label=_("NIB"),
        ),
        validators=("NIBvalidator"),
    ),

    StringField(
        "IBN",
        searchable=1,
        schemata="Bank details",
        required=0,
        widget=StringWidget(
            visible={"view": "visible", "edit": "visible"},
            label=_("IBN"),
        ),
        validators=("IBANvalidator"),
    ),

    StringField(
        "SWIFTcode",
        searchable=1,
        required=0,
        schemata="Bank details",
        widget=StringWidget(
            visible={"view": "visible", "edit": "visible"},
            label=_("SWIFT code."),
        ),
    ),
))


class Supplier(Organisation):
    """Supplier content
    """
    implements(ISupplier, IDeactivable)

    _at_rename_after_creation = True
    displayContentsTab = False
    isPrincipiaFolderish = 0
    schema = schema
    security = ClassSecurityInfo()

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(Supplier, PROJECTNAME)
