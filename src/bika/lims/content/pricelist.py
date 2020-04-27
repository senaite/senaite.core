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
from DateTime import DateTime
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import DecimalWidget
from Products.Archetypes.public import FixedPointField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import TextField
from Products.Archetypes.public import registerType
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.config import PRICELIST_TYPES
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IPricelist

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

    TextField(
        "Remarks",
        allowable_content_types=("text/plain",),
        widget=TextAreaWidget(
            label=_("Remarks"),
        )
    ),
))

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
