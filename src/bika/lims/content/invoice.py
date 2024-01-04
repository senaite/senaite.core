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

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IInvoice
from plone.app.blob.field import FileField as BlobFileField
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import FileWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import registerType
from Products.CMFPlone.utils import safe_unicode
from senaite.core.browser.fields.datetime import DateTimeField
from senaite.core.browser.widgets.datetimewidget import DateTimeWidget
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    BlobFileField(
        "InvoicePDF",
        widget=FileWidget(
            label=_("Invoice PDF"),
        )
    ),
    UIDReferenceField(
        "Client",
        required=1,
        allowed_types=("Client",),
    ),
    UIDReferenceField(
        "AnalysisRequest",
        required=1,
        allowed_types=("AnalysisRequest",),
        relationship="AnalysisRequestInvoice",
    ),
    DateTimeField(
        "InvoiceDate",
        required=1,
        default_method="get_current_date",
        widget=DateTimeWidget(
            label=_("Date"),
        ),
    ),
))

TitleField = schema["title"]
TitleField.required = 0
TitleField.widget.visible = False


class Invoice(BaseFolder):
    implements(IInvoice)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """Return the Invoice ID as title
        """
        return safe_unicode(self.getId()).encode("utf-8")

    def get_current_date(self):
        """Return the current Date
        """


registerType(Invoice, PROJECTNAME)
