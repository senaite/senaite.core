# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import sys

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IInvoice
from plone.app.blob.field import FileField as BlobFileField
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import FileWidget
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import registerType
from Products.ATExtensions.ateapi import DateTimeField
from Products.ATExtensions.ateapi import DateTimeWidget
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    BlobFileField(
        "InvoicePDF",
        widget=FileWidget(
            label=_("Invoice PDF"),
        )
    ),
    ReferenceField(
        "Client",
        required=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=("Client",),
        relationship="ClientInvoice",
    ),
    ReferenceField(
        "AnalysisRequest",
        required=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=("AnalysisRequest",),
        relationship="AnalysisRequestInvoice",
    ),
    ReferenceField(
        "SupplyOrder",
        required=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=("SupplyOrder",),
        relationship="SupplyOrderInvoice",
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
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """Return the Invoice ID as title
        """
        return safe_unicode(self.getId()).encode("utf-8")

    def get_current_date(self):
        """Return the current Date
        """


registerType(Invoice, PROJECTNAME)
