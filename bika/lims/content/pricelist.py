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
from bika.lims.config import PRICELIST_TYPES
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IPricelist
from DateTime import DateTime
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import DecimalWidget
from Products.Archetypes.public import FixedPointField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import registerType
from zope.interface import implements


schema = BikaSchema.copy() + Schema((

    StringField(
        "Type",
        required=1,
        vocabulary=PRICELIST_TYPES,
        widget=SelectionWidget(
            format="select",
            label=_("Pricelist for"),
        ),
    ),

    BooleanField(
        "BulkDiscount",
        default=False,
        widget=SelectionWidget(
            label=_("Bulk discount applies"),
        ),
    ),

    FixedPointField(
        "BulkPrice",
        widget=DecimalWidget(
            label=_("Discount %"),
            description=_("Enter discount percentage value"),
        ),
    ),

    BooleanField(
        "Descriptions",
        default=False,
        widget=BooleanWidget(
            label=_("Include descriptions"),
            description=_("Select if the descriptions should be included"),
        ),
    ),

    RemarksField(
        "Remarks",
        searchable=True,
        widget=RemarksWidget(
            label=_("Remarks"),
        ),
    )),
)

Field = schema["title"]
Field.required = 1
Field.widget.visible = True

Field = schema["effectiveDate"]
Field.schemata = "default"
# If no date is selected the item will be publishedimmediately.
Field.required = 0
Field.widget.visible = True

Field = schema["expirationDate"]
Field.schemata = "default"
# If no date is chosen, it will never expire.
Field.required = 0
Field.widget.visible = True


class Pricelist(BaseFolder):
    """Pricelist content
    """
    implements(IPricelist, IDeactivable)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    @security.public
    def current_date(self):
        """ return current date """
        return DateTime()


registerType(Pricelist, PROJECTNAME)
