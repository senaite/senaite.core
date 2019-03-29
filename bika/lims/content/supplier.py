# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields.remarksfield import RemarksField
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.organisation import Organisation
from bika.lims.interfaces import ISupplier, IDeactivable
from zope.interface import implements
from Products.Archetypes.public import registerType
from Products.Archetypes.public import StringField
from Products.Archetypes.public import ManagedSchema
from Products.Archetypes.public import StringWidget


schema = Organisation.schema.copy() + ManagedSchema((

    RemarksField(
        "Remarks",
        searchable=True,
        widget=RemarksWidget(
            label=_("Remarks"),
        ),
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
